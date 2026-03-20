"""Agent 会话服务"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session as DBSession
from sqlalchemy import desc
from backend.models.session import AgentSession, AgentMessage


class AgentSessionService:
    """
    Agent 会话服务

    负责会话和消息的持久化操作
    """

    @staticmethod
    def create_session(db: DBSession, session_id: str) -> AgentSession:
        """
        创建新会话

        Args:
            db: 数据库会话
            session_id: 会话 ID

        Returns:
            AgentSession: 创建的会话对象
        """
        session = AgentSession(
            session_id=session_id,
            message_count=0,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            is_active=True,
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        return session

    @staticmethod
    def get_session(db: DBSession, session_id: str) -> Optional[AgentSession]:
        """
        获取会话

        Args:
            db: 数据库会话
            session_id: 会话 ID

        Returns:
            Optional[AgentSession]: 会话对象，不存在返回 None
        """
        return db.query(AgentSession).filter(AgentSession.session_id == session_id).first()

    @staticmethod
    def get_or_create_session(db: DBSession, session_id: str) -> AgentSession:
        """
        获取或创建会话

        Args:
            db: 数据库会话
            session_id: 会话 ID

        Returns:
            AgentSession: 会话对象
        """
        session = AgentSessionService.get_session(db, session_id)
        if not session:
            session = AgentSessionService.create_session(db, session_id)
        return session

    @staticmethod
    def update_session_title(db: DBSession, session_id: str, title: str) -> bool:
        """
        更新会话标题

        Args:
            db: 数据库会话
            session_id: 会话 ID
            title: 标题

        Returns:
            bool: 是否成功更新
        """
        session = AgentSessionService.get_session(db, session_id)
        if not session:
            return False
        session.title = title
        session.updated_at = datetime.now()
        db.commit()
        return True

    @staticmethod
    def increment_message_count(db: DBSession, session_id: str) -> bool:
        """
        增加会话消息计数

        Args:
            db: 数据库会话
            session_id: 会话 ID

        Returns:
            bool: 是否成功更新
        """
        session = AgentSessionService.get_session(db, session_id)
        if not session:
            return False
        session.message_count += 1
        session.updated_at = datetime.now()
        db.commit()
        return True

    @staticmethod
    def add_message(
        db: DBSession,
        session_id: str,
        role: str,
        content: str,
        token_count: Optional[int] = None,
        extra_data: Optional[Dict[str, Any]] = None,
    ) -> AgentMessage:
        """
        添加消息

        Args:
            db: 数据库会话
            session_id: 会话 ID
            role: 消息角色（user/assistant）
            content: 消息内容
            token_count: token 数量
            extra_data: 扩展元数据

        Returns:
            AgentMessage: 创建的消息对象
        """
        # 确保会话存在
        AgentSessionService.get_or_create_session(db, session_id)

        message = AgentMessage(
            session_id=session_id,
            role=role,
            content=content,
            token_count=token_count or 0,
            timestamp=datetime.now(),
            extra_data=extra_data,
        )
        db.add(message)
        db.commit()
        db.refresh(message)

        # 更新会话计数
        AgentSessionService.increment_message_count(db, session_id)

        return message

    @staticmethod
    def get_messages(
        db: DBSession,
        session_id: str,
        limit: int = 50,
    ) -> List[AgentMessage]:
        """
        获取会话消息列表

        Args:
            db: 数据库会话
            session_id: 会话 ID
            limit: 限制数量

        Returns:
            List[AgentMessage]: 消息列表
        """
        return (
            db.query(AgentMessage)
            .filter(AgentMessage.session_id == session_id)
            .order_by(AgentMessage.timestamp.asc())
            .limit(limit)
            .all()
        )

    @staticmethod
    def delete_session(db: DBSession, session_id: str) -> bool:
        """
        删除会话（级联删除消息）

        Args:
            db: 数据库会话
            session_id: 会话 ID

        Returns:
            bool: 是否成功删除
        """
        session = AgentSessionService.get_session(db, session_id)
        if not session:
            return False
        db.delete(session)
        db.commit()
        return True

    @staticmethod
    def get_all_sessions(db: DBSession, limit: int = 100) -> List[AgentSession]:
        """
        获取所有会话列表

        Args:
            db: 数据库会话
            limit: 限制数量

        Returns:
            List[AgentSession]: 会话列表
        """
        return (
            db.query(AgentSession)
            .filter(AgentSession.is_active == True)
            .order_by(desc(AgentSession.updated_at))
            .limit(limit)
            .all()
        )

    @staticmethod
    def deactivate_session(db: DBSession, session_id: str) -> bool:
        """
        停用会话（软删除）

        Args:
            db: 数据库会话
            session_id: 会话 ID

        Returns:
            bool: 是否成功更新
        """
        session = AgentSessionService.get_session(db, session_id)
        if not session:
            return False
        session.is_active = False
        session.updated_at = datetime.now()
        db.commit()
        return True
