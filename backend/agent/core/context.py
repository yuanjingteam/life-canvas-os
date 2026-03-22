"""
上下文管理器
管理会话上下文和记忆（持久化版本）
"""
from typing import Dict, Optional, List, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import json

from backend.agent.models.context import SessionContext, Message
from backend.agent.utils.logger import get_logger
from backend.models.agent import AgentSession, AgentMessage

logger = get_logger("context")


class ContextManager:
    """上下文管理器（持久化版本）"""

    def __init__(
        self,
        db_session: Optional[Session] = None,
        max_sessions: int = 100,
        session_ttl: int = 604800  # 7 days
    ):
        """
        初始化上下文管理器

        Args:
            db_session: 数据库会话（可选，为 None 时使用纯内存模式）
            max_sessions: 最大会话数（内存缓存）
            session_ttl: 会话过期时间（秒）
        """
        self._cache: Dict[str, SessionContext] = {}  # 内存缓存
        self._db: Optional[Session] = db_session
        self.max_sessions = max_sessions
        self.session_ttl = session_ttl

    def get_or_create_session(
        self,
        session_id: Optional[str] = None,
        user_id: Optional[int] = None
    ) -> SessionContext:
        """
        获取或创建会话

        Args:
            session_id: 会话ID（可选）
            user_id: 用户ID（可选）

        Returns:
            会话上下文
        """
        # 清理过期会话
        self._cleanup_expired_sessions()

        # 1. 检查内存缓存
        if session_id and session_id in self._cache:
            logger.debug(f"Session found in cache: {session_id}")
            return self._cache[session_id]

        # 2. 从数据库加载（如果有数据库）
        if session_id and self._db:
            db_context = self._load_from_db(session_id)
            if db_context:
                self._cache[session_id] = db_context
                logger.debug(f"Session loaded from database: {session_id}")
                return db_context

        # 3. 创建新会话
        context = SessionContext()
        if session_id:
            context.session_id = session_id

        # 4. 持久化到数据库（如果有数据库）
        if self._db:
            self._save_to_db(context, user_id=user_id)
            logger.info(f"Created and persisted new session: {context.session_id}")
        else:
            logger.info(f"Created new session (memory-only): {context.session_id}")

        # 5. 加入内存缓存
        self._cache[context.session_id] = context

        # 6. 检查内存缓存数量限制
        if len(self._cache) > self.max_sessions:
            self._evict_oldest_session()

        return context

    def get_session(self, session_id: str) -> Optional[SessionContext]:
        """
        获取会话

        Args:
            session_id: 会话ID

        Returns:
            会话上下文，不存在返回 None
        """
        # 先检查缓存
        if session_id in self._cache:
            return self._cache[session_id]

        # 从数据库加载
        if self._db:
            db_context = self._load_from_db(session_id)
            if db_context:
                self._cache[session_id] = db_context
                return db_context

        return None

    def update_session(self, context: SessionContext):
        """
        更新会话

        Args:
            context: 会话上下文
        """
        print(f"[UPDATE] Session {context.session_id}, messages: {len(context.messages)}", flush=True)
        context.updated_at = datetime.now()
        self._cache[context.session_id] = context

        # 同步到数据库
        if self._db:
            self._update_session_in_db(context)

    def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        actions: List[Dict[str, Any]] = None
    ):
        """
        添加消息到会话

        Args:
            session_id: 会话ID
            role: 角色
            content: 内容
            actions: 执行的操作
        """
        context = self.get_session(session_id)
        if context:
            context.add_message(role, content, actions)
            print(f"[MSG] Added {role} msg to {session_id}, total: {len(context.messages)}", flush=True)
            self.update_session(context)

            # 单独持久化消息到数据库
            if self._db:
                self._save_message_to_db(session_id, role, content, actions)
        else:
            print(f"[MSG] Session {session_id} NOT FOUND", flush=True)

    def add_operation(
        self,
        session_id: str,
        skill: str,
        action: str,
        params: Dict[str, Any],
        result: Any
    ):
        """
        添加操作记录

        Args:
            session_id: 会话ID
            skill: 技能名称
            action: 操作名称
            params: 参数
            result: 结果
        """
        context = self.get_session(session_id)
        if context:
            operation = {
                "skill": skill,
                "action": action,
                "params": params,
                "result": result,
                "timestamp": datetime.now().isoformat()
            }
            context.last_operations.append(operation)
            # 保持最近 10 个操作
            if len(context.last_operations) > 10:
                context.last_operations = context.last_operations[-10:]
            self.update_session(context)

    def set_entity_reference(
        self,
        session_id: str,
        entity_type: str,
        entity_id: Any
    ):
        """
        设置实体引用

        Args:
            session_id: 会话ID
            entity_type: 实体类型
            entity_id: 实体ID
        """
        context = self.get_session(session_id)
        if context:
            context.set_entity_reference(entity_type, entity_id)
            self.update_session(context)

    def get_context_for_prompt(self, session_id: str) -> Dict[str, Any]:
        """
        获取用于 Prompt 的上下文信息

        Args:
            session_id: 会话ID

        Returns:
            上下文数据
        """
        context = self.get_session(session_id)
        if not context:
            return {}

        return {
            "referenced_entities": context.referenced_entities,
            "last_operations": context.last_operations[-5:]  # 最近 5 个操作
        }

    def _load_from_db(self, session_id: str) -> Optional[SessionContext]:
        """从数据库加载会话"""
        if not self._db:
            return None

        try:
            # 查询会话
            db_session = self._db.query(AgentSession).filter(
                AgentSession.session_id == session_id
            ).first()

            if not db_session:
                # 尝试从消息表重建会话
                return self._rebuild_session_from_messages(session_id)

            # 检查是否过期
            if db_session.expires_at and db_session.expires_at < datetime.now():
                self._db.delete(db_session)
                self._db.commit()
                logger.info(f"Session expired and deleted: {session_id}")
                # 过期删除后，尝试从消息表重建
                return self._rebuild_session_from_messages(session_id)

            # 查询消息
            messages = self._db.query(AgentMessage).filter(
                AgentMessage.session_id == session_id
            ).order_by(AgentMessage.created_at).all()

            # 构建 SessionContext
            context = SessionContext(
                session_id=db_session.session_id,
                referenced_entities=db_session.referenced_entities or {},
                last_operations=db_session.last_operations or [],
                created_at=db_session.created_at,
                updated_at=db_session.updated_at
            )

            # 添加消息
            for msg in messages:
                message = Message(
                    role=msg.role,
                    content=msg.content,
                    actions=msg.actions or [],
                    timestamp=msg.created_at
                )
                context.messages.append(message)

            return context

        except Exception as e:
            logger.error(f"Failed to load session from database: {e}")
            return None

    def _rebuild_session_from_messages(self, session_id: str) -> Optional[SessionContext]:
        """
        从消息表重建会话

        当 AgentSession 表中找不到会话时，检查 AgentMessage 表是否有该会话的消息，
        如果有则重建会话上下文。

        Args:
            session_id: 会话ID

        Returns:
            重建的会话上下文，消息不存在则返回 None
        """
        if not self._db:
            return None

        try:
            # 查询消息表
            messages = self._db.query(AgentMessage).filter(
                AgentMessage.session_id == session_id
            ).order_by(AgentMessage.created_at).all()

            if not messages:
                logger.debug(f"No messages found for session: {session_id}")
                return None

            # 从消息中获取时间信息
            first_message_time = messages[0].created_at
            last_message_time = messages[-1].created_at

            # 构建 SessionContext
            context = SessionContext(
                session_id=session_id,
                referenced_entities={},  # 从消息中无法恢复实体引用
                last_operations=[],  # 从消息中无法恢复操作记录
                created_at=first_message_time,
                updated_at=last_message_time
            )

            # 添加消息
            for msg in messages:
                message = Message(
                    role=msg.role,
                    content=msg.content,
                    actions=msg.actions or [],
                    timestamp=msg.created_at
                )
                context.messages.append(message)

            # 将会话重新保存到数据库，延长过期时间
            db_session = AgentSession(
                session_id=session_id,
                referenced_entities=context.referenced_entities,
                last_operations=context.last_operations,
                expires_at=datetime.now() + timedelta(seconds=self.session_ttl)
            )
            self._db.add(db_session)
            self._db.commit()

            logger.info(f"Rebuilt session from messages: {session_id}, {len(messages)} messages")
            return context

        except Exception as e:
            logger.error(f"Failed to rebuild session from messages: {e}")
            if self._db.is_active:
                self._db.rollback()
            return None

    def _save_to_db(self, context: SessionContext, user_id: Optional[int] = None):
        """保存会话到数据库

        Args:
            context: 会话上下文
            user_id: 用户ID（可选）
        """
        if not self._db:
            return

        try:
            # 检查是否已存在
            existing = self._db.query(AgentSession).filter(
                AgentSession.session_id == context.session_id
            ).first()

            if existing:
                # 更新现有记录 - 只更新内容，不自动更新时间戳
                existing.referenced_entities = context.referenced_entities
                existing.last_operations = context.last_operations
                # 如果有第一条用户消息且标题为空，则生成标题
                if not existing.title:
                    first_user_msg = next(
                        (m for m in context.messages if m.role == "user"),
                        None
                    )
                    if first_user_msg:
                        existing.title = self._generate_title(first_user_msg.content)
                        logger.info(f"Generated title for session {context.session_id}: {existing.title}")
            else:
                # 创建新记录 - 显式设置时间戳确保排序正确
                now = datetime.now()
                db_session = AgentSession(
                    session_id=context.session_id,
                    user_id=user_id,
                    title=None,  # 标题将在用户发送消息后生成
                    referenced_entities=context.referenced_entities,
                    last_operations=context.last_operations,
                    created_at=now,
                    updated_at=now,
                    expires_at=now + timedelta(seconds=self.session_ttl)
                )
                self._db.add(db_session)
                logger.debug(f"Created new session record: {context.session_id}")

            self._db.commit()

        except Exception as e:
            logger.error(f"Failed to save session to database: {e}")
            self._db.rollback()

    def _generate_title(self, content: str) -> str:
        """从消息内容生成标题（取前50个字符）"""
        # 去除多余空白字符
        cleaned = " ".join(content.split())
        if len(cleaned) > 50:
            return cleaned[:50] + "..."
        return cleaned

    def _update_session_in_db(self, context: SessionContext):
        """更新数据库中的会话"""
        if not self._db:
            return

        try:
            db_session = self._db.query(AgentSession).filter(
                AgentSession.session_id == context.session_id
            ).first()

            if db_session:
                # 只更新实际内容，不自动更新 updated_at 和 expires_at
                # updated_at 由数据库 onupdate 自动管理（只在有实际 UPDATE 时触发）
                db_session.referenced_entities = context.referenced_entities
                db_session.last_operations = context.last_operations

                # 如果标题为空，尝试从用户消息生成
                if not db_session.title:
                    first_user_msg = next(
                        (m for m in context.messages if m.role == "user"),
                        None
                    )
                    if first_user_msg:
                        new_title = self._generate_title(first_user_msg.content)
                        db_session.title = new_title
                        print(f"[TITLE] Generated for {context.session_id}: {new_title}", flush=True)
                        logger.info(f"Generated title for session {context.session_id}: {new_title}")
                    else:
                        print(f"[TITLE] No user msg, context has {len(context.messages)} messages", flush=True)
                else:
                    print(f"[TITLE] Already set: {db_session.title}", flush=True)

                self._db.commit()

        except Exception as e:
            print(f"[TITLE] Error: {e}", flush=True)
            logger.error(f"Failed to update session in database: {e}")
            self._db.rollback()

    def _save_message_to_db(
        self,
        session_id: str,
        role: str,
        content: str,
        actions: List[Dict[str, Any]] = None
    ):
        """保存消息到数据库，同时更新会话的时间戳"""
        if not self._db:
            return

        try:
            # 保存消息
            message = AgentMessage(
                session_id=session_id,
                role=role,
                content=content,
                actions=actions or []
            )
            self._db.add(message)

            # 更新会话的 updated_at 和 expires_at（只有新消息时才更新）
            db_session = self._db.query(AgentSession).filter(
                AgentSession.session_id == session_id
            ).first()
            if db_session:
                db_session.updated_at = datetime.now()
                db_session.expires_at = datetime.now() + timedelta(seconds=self.session_ttl)

            self._db.commit()

        except Exception as e:
            logger.error(f"Failed to save message to database: {e}")
            self._db.rollback()

    def _cleanup_expired_sessions(self):
        """清理过期会话"""
        now = datetime.now()
        expired_cache = []

        # 清理内存缓存
        for session_id, context in self._cache.items():
            age = (now - context.updated_at).total_seconds()
            if age > self.session_ttl:
                expired_cache.append(session_id)

        for session_id in expired_cache:
            del self._cache[session_id]

        if expired_cache:
            logger.info(f"Cleaned up {len(expired_cache)} expired sessions from cache")

        # 清理数据库中的过期会话
        if self._db:
            try:
                deleted = self._db.query(AgentSession).filter(
                    AgentSession.expires_at < now
                ).delete()
                if deleted > 0:
                    self._db.commit()
                    logger.info(f"Cleaned up {deleted} expired sessions from database")
            except Exception as e:
                logger.error(f"Failed to cleanup expired sessions from database: {e}")
                self._db.rollback()

    def _evict_oldest_session(self):
        """驱逐最老的会话（仅从内存缓存）"""
        if not self._cache:
            return

        oldest_id = min(
            self._cache.keys(),
            key=lambda sid: self._cache[sid].updated_at
        )
        del self._cache[oldest_id]
        logger.info(f"Evicted oldest session from cache: {oldest_id}")

    def get_session_count(self) -> int:
        """获取当前会话数（内存缓存）"""
        return len(self._cache)

    def get_total_session_count(self) -> int:
        """获取总会话数（包括数据库）"""
        if not self._db:
            return len(self._cache)

        try:
            return self._db.query(AgentSession).count()
        except Exception:
            return len(self._cache)

    def list_sessions(
        self,
        limit: int = 20,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """
        列出所有会话

        Args:
            limit: 返回数量限制
            offset: 偏移量

        Returns:
            会话列表
        """
        logger.debug(f"list_sessions called with limit={limit}, offset={offset}")

        if not self._db:
            # 纯内存模式
            sessions = []
            for session_id, context in self._cache.items():
                # 从第一条用户消息生成标题
                title = None
                first_user_msg = next(
                    (m for m in context.messages if m.role == "user"),
                    None
                )
                if first_user_msg:
                    title = self._generate_title(first_user_msg.content)

                sessions.append({
                    "session_id": session_id,
                    "title": title,
                    "message_count": len(context.messages),
                    "created_at": context.created_at,
                    "updated_at": context.updated_at,
                    "last_message": context.messages[-1].content if context.messages else None
                })
            return sessions[offset:offset + limit]

        try:
            print("[DEBUG] Starting list_sessions query")
            logger.debug("Starting list_sessions query")
            # 从数据库查询（固定会话排在前面）
            db_sessions = self._db.query(AgentSession).order_by(
                AgentSession.pinned.desc(),
                AgentSession.updated_at.desc()
            ).offset(offset).limit(limit).all()

            print(f"[DEBUG] db_sessions count: {len(db_sessions)}")
            logger.debug(f"db_sessions count: {len(db_sessions)}")

            # 如果数据库查询不到会话，尝试从消息表重建
            if not db_sessions:
                # 从 agent_messages 表按 session_id 分组查询
                from sqlalchemy import func

                # 获取所有不同的 session_id，按最新的消息时间排序
                session_info = self._db.query(
                    AgentMessage.session_id,
                    func.count(AgentMessage.id).label('message_count'),
                    func.max(AgentMessage.created_at).label('max_created_at'),
                    func.min(AgentMessage.created_at).label('min_created_at')
                ).group_by(AgentMessage.session_id).all()

                if session_info:
                    logger.debug(f"Found {len(session_info)} sessions from messages table")
                    # 获取最后一条消息内容
                    result = []
                    for info in session_info:
                        last_message = self._db.query(AgentMessage).filter(
                            AgentMessage.session_id == info.session_id
                        ).order_by(AgentMessage.created_at.desc()).first()

                        # 获取第一条用户消息作为标题
                        first_message = self._db.query(AgentMessage).filter(
                            AgentMessage.session_id == info.session_id,
                            AgentMessage.role == "user"
                        ).order_by(AgentMessage.created_at.asc()).first()

                        result.append({
                            "session_id": info.session_id,
                            "title": self._generate_title(first_message.content) if first_message else None,
                            "message_count": info.message_count,
                            "created_at": info.min_created_at,
                            "updated_at": info.max_created_at,
                            "last_message": last_message.content if last_message else None,
                            "pinned": 0  # 从消息表重建的会话默认未固定
                        })

                    # 按 updated_at 降序排序后应用分页
                    result.sort(key=lambda x: x["updated_at"], reverse=True)
                    logger.debug(f"Returning {len(result)} sessions from fallback")
                    return result[offset:offset + limit]

                logger.debug("No session_info found, returning empty list")
                return []

            result = []
            for db_session in db_sessions:
                # 获取消息数量和最后一条消息
                message_count = self._db.query(AgentMessage).filter(
                    AgentMessage.session_id == db_session.session_id
                ).count()

                last_message = self._db.query(AgentMessage).filter(
                    AgentMessage.session_id == db_session.session_id
                ).order_by(AgentMessage.created_at.desc()).first()

                result.append({
                    "session_id": db_session.session_id,
                    "title": db_session.title,
                    "message_count": message_count,
                    "created_at": db_session.created_at,
                    "updated_at": db_session.updated_at,
                    "last_message": last_message.content if last_message else None,
                    "pinned": db_session.pinned or 0
                })

            # 注意：不再在加载会话列表时刷新 expires_at
            # expires_at 只在发送新消息时延长，避免每次打开聊天框都刷新时间戳

            return result

        except Exception as e:
            logger.error(f"Failed to list sessions: {e}")
            return []

    def delete_session(self, session_id: str) -> bool:
        """
        删除会话

        Args:
            session_id: 会话ID

        Returns:
            是否成功
        """
        # 从内存缓存删除
        if session_id in self._cache:
            del self._cache[session_id]

        # 从数据库删除
        if self._db:
            try:
                # 先删除消息（外键关联）
                self._db.query(AgentMessage).filter(
                    AgentMessage.session_id == session_id
                ).delete()

                # 再删除会话
                deleted = self._db.query(AgentSession).filter(
                    AgentSession.session_id == session_id
                ).delete()

                self._db.commit()
                if deleted > 0:
                    logger.info(f"Deleted session from database: {session_id}")
                    return True
            except Exception as e:
                logger.error(f"Failed to delete session from database: {e}")
                self._db.rollback()
                return False

        return session_id not in self._cache

    def clear_all_sessions(self):
        """清除所有会话"""
        # 清除内存缓存
        self._cache.clear()

        # 清除数据库
        if self._db:
            try:
                self._db.query(AgentMessage).delete()
                self._db.query(AgentSession).delete()
                self._db.commit()
                logger.info("Cleared all sessions from database")
            except Exception as e:
                logger.error(f"Failed to clear sessions from database: {e}")
                self._db.rollback()

        logger.info("Cleared all sessions")


# 全局上下文管理器实例（内存模式，用于向后兼容）
_context_manager: Optional[ContextManager] = None


def get_context_manager() -> ContextManager:
    """获取全局上下文管理器（内存模式）"""
    global _context_manager
    if _context_manager is None:
        _context_manager = ContextManager()
    return _context_manager


def get_context_manager_with_db(db: Session) -> ContextManager:
    """
    获取带数据库会话的上下文管理器

    Args:
        db: 数据库会话

    Returns:
        ContextManager 实例
    """
    return ContextManager(db_session=db)
