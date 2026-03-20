"""
上下文管理器

管理会话上下文和对话记忆。
"""

import uuid
from typing import Dict, Optional, List
from datetime import datetime, timedelta
from ..models.context import ContextState


def _get_db_session():
    """
    获取数据库会话

    延迟导入以避免循环依赖

    Returns:
        数据库上下文管理器
    """
    from backend.db.session import get_db_context
    return get_db_context


class ContextManager:
    """
    上下文管理器

    负责管理所有会话的上下文状态，支持：
    - 会话创建和销毁
    - 上下文记忆（短期、中期）
    - 记忆压缩（当 token 数接近阈值时）
    - 数据库持久化
    """

    # 上下文配置
    MAX_TOKENS = 4000  # 最大 token 数
    MAX_MESSAGES = 30  # 最大消息轮数
    SESSION_TTL = timedelta(hours=24)  # 会话超时时间

    def __init__(self):
        self._contexts: Dict[str, ContextState] = {}
        self._last_accessed: Dict[str, datetime] = {}

    def _sync_to_db(self, session_id: str, role: str, content: str) -> None:
        """
        同步消息到数据库

        Args:
            session_id: 会话 ID
            role: 消息角色（user/assistant）
            content: 消息内容
        """
        try:
            from backend.services.agent_session_service import AgentSessionService

            with _get_db_session()() as session:
                AgentSessionService.add_message(
                    db=session,
                    session_id=session_id,
                    role=role,
                    content=content,
                )
        except Exception as e:
            print(f"同步消息到数据库失败：{e}")

    def add_message_to_context(self, session_id: str, role: str, content: str) -> None:
        """
        添加消息到上下文并同步到数据库

        Args:
            session_id: 会话 ID
            role: 消息角色（user/assistant）
            content: 消息内容
        """
        # 获取或创建上下文
        context = self.get_or_create(session_id)

        # 添加到内存中的上下文
        context.add_message(role, content)

        # 同步到数据库
        self._sync_to_db(session_id, role, content)

    def _ensure_session_exists(self, session_id: str) -> None:
        """
        确保会话在数据库中存在

        Args:
            session_id: 会话 ID
        """
        try:
            from backend.services.agent_session_service import AgentSessionService

            with _get_db_session()() as session:
                AgentSessionService.get_or_create_session(session, session_id)
        except Exception as e:
            print(f"确保会话存在失败：{e}")

    def get_or_create(self, session_id: Optional[str] = None) -> ContextState:
        """
        获取或创建会话上下文

        Args:
            session_id: 会话 ID，为空则创建新会话

        Returns:
            ContextState: 上下文状态
        """
        if session_id is None:
            session_id = self._generate_session_id()

        # 检查是否已存在
        if session_id not in self._contexts:
            self._contexts[session_id] = ContextState(session_id=session_id)
            # 确保数据库中存在会话记录
            self._ensure_session_exists(session_id)

        # 更新最后访问时间
        self._last_accessed[session_id] = datetime.now()
        return self._contexts[session_id]

    def get(self, session_id: str) -> Optional[ContextState]:
        """
        获取会话上下文

        Args:
            session_id: 会话 ID

        Returns:
            Optional[ContextState]: 上下文状态，不存在返回 None
        """
        # 更新最后访问时间
        if session_id in self._contexts:
            self._last_accessed[session_id] = datetime.now()
        return self._contexts.get(session_id)

    def delete(self, session_id: str) -> bool:
        """
        删除会话上下文

        Args:
            session_id: 会话 ID

        Returns:
            bool: 是否成功删除
        """
        if session_id in self._contexts:
            del self._contexts[session_id]
            if session_id in self._last_accessed:
                del self._last_accessed[session_id]
            return True
        return False

    def clear(self) -> None:
        """清空所有会话"""
        self._contexts.clear()
        self._last_accessed.clear()

    def cleanup_expired(self) -> int:
        """
        清理过期会话

        Returns:
            int: 清理的会话数量
        """
        now = datetime.now()
        expired = [
            sid
            for sid, last_accessed in self._last_accessed.items()
            if now - last_accessed > self.SESSION_TTL
        ]

        for sid in expired:
            self.delete(sid)

        return len(expired)

    def should_compress(self, context: ContextState) -> bool:
        """
        判断是否需要压缩上下文

        Args:
            context: 上下文状态

        Returns:
            bool: 是否需要压缩
        """
        # Token 数接近阈值
        if context.token_count > 0.8 * self.MAX_TOKENS:
            return True

        # 消息轮数超过限制
        if len(context.messages) > self.MAX_MESSAGES:
            return True

        return False

    def _generate_session_id(self) -> str:
        """生成会话 ID"""
        return f"sess_{uuid.uuid4().hex[:12]}"

    def get_stats(self) -> Dict[str, int]:
        """获取统计信息"""
        return {
            "active_sessions": len(self._contexts),
            "total_messages": sum(len(ctx.messages) for ctx in self._contexts.values()),
            "total_operations": sum(
                len(ctx.last_operations) for ctx in self._contexts.values()
            ),
        }


# 单例实例
_context_manager_instance: Optional["ContextManager"] = None


def get_context_manager() -> ContextManager:
    """获取 ContextManager 单例"""
    global _context_manager_instance
    if _context_manager_instance is None:
        _context_manager_instance = ContextManager()
    return _context_manager_instance
