"""
Agent Service
业务逻辑层，处理会话管理相关操作
"""
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session

from backend.models.agent import AgentSession, AgentMessage
from backend.agent.core.context import ContextManager, get_context_manager_with_db
from backend.agent.utils.logger import get_logger

logger = get_logger("agent_service")


class AgentService:
    """Agent 服务层"""

    def __init__(self, db: Session):
        """
        初始化服务

        Args:
            db: 数据库会话
        """
        self.db = db
        self._context_manager: Optional[ContextManager] = None

    @property
    def context_manager(self) -> ContextManager:
        """获取上下文管理器（延迟初始化）"""
        if self._context_manager is None:
            self._context_manager = get_context_manager_with_db(self.db)
        return self._context_manager

    # ========== 会话 CRUD ==========

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        获取会话详情

        Args:
            session_id: 会话ID

        Returns:
            会话信息，不存在返回 None
        """
        context = self.context_manager.get_session(session_id)
        if not context:
            return None

        # 获取标题
        db_session = self.db.query(AgentSession).filter(
            AgentSession.session_id == session_id
        ).first()

        return {
            "session_id": context.session_id,
            "title": db_session.title if db_session else None,
            "messages": [m.model_dump() for m in context.messages],
            "referenced_entities": context.referenced_entities,
            "last_operations": context.last_operations,
            "created_at": context.created_at.isoformat(),
            "updated_at": context.updated_at.isoformat()
        }

    def list_sessions(
        self,
        limit: int = 20,
        offset: int = 0
    ) -> Tuple[List[Dict[str, Any]], int]:
        """
        获取会话列表

        Args:
            limit: 返回数量限制
            offset: 偏移量

        Returns:
            (会话列表, 总数)
        """
        sessions = self.context_manager.list_sessions(limit=limit, offset=offset)
        total = self.context_manager.get_total_session_count()
        return sessions, total

    def delete_session(self, session_id: str) -> bool:
        """
        删除会话及其所有消息

        Args:
            session_id: 会话ID

        Returns:
            是否成功
        """
        try:
            # 删除消息
            self.db.query(AgentMessage).filter(
                AgentMessage.session_id == session_id
            ).delete()

            # 删除会话
            self.db.query(AgentSession).filter(
                AgentSession.session_id == session_id
            ).delete()

            self.db.commit()

            # 清理内存缓存
            self.context_manager._cache.pop(session_id, None)

            logger.info(f"Deleted session: {session_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete session {session_id}: {e}")
            self.db.rollback()
            return False

    def toggle_pin(self, session_id: str, pinned: int) -> Optional[Dict[str, Any]]:
        """
        切换会话固定状态

        Args:
            session_id: 会话ID
            pinned: 固定状态 (0: 取消固定, 1: 固定)

        Returns:
            更新后的信息，会话不存在返回 None
        """
        db_session = self.db.query(AgentSession).filter(
            AgentSession.session_id == session_id
        ).first()

        if not db_session:
            return None

        db_session.pinned = pinned
        self.db.commit()

        logger.info(f"Session {session_id} pinned={pinned}")
        return {
            "session_id": session_id,
            "pinned": pinned
        }

    # ========== 辅助方法 ==========

    def session_exists(self, session_id: str) -> bool:
        """
        检查会话是否存在

        Args:
            session_id: 会话ID

        Returns:
            是否存在
        """
        return self.db.query(AgentSession).filter(
            AgentSession.session_id == session_id
        ).first() is not None
