"""
Agent 数据库模型
用于会话持久化和历史消息存储
"""
from sqlalchemy import Column, Integer, String, JSON, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from backend.db.base import Base
from backend.db.session import localnow_func


class AgentSession(Base):
    """Agent 会话表"""
    __tablename__ = "agent_sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(32), unique=True, index=True)  # 唯一会话ID
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # 标题（从第一条用户消息提取）
    title = Column(String(200), nullable=True)

    # 固定状态 (0: 未固定, 1: 已固定)
    pinned = Column(Integer, default=0)

    # 上下文数据（JSON）
    referenced_entities = Column(JSON, default={})  # 实体引用
    last_operations = Column(JSON, default=[])  # 最近操作

    # 时间戳
    created_at = Column(DateTime, server_default=localnow_func())
    updated_at = Column(DateTime, server_default=localnow_func(), onupdate=localnow_func())
    expires_at = Column(DateTime, nullable=True)  # 过期时间

    # 关系
    messages = relationship(
        "AgentMessage",
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="AgentMessage.created_at"
    )


class AgentMessage(Base):
    """Agent 消息表"""
    __tablename__ = "agent_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(32), ForeignKey("agent_sessions.session_id"), index=True)

    role = Column(String(20), nullable=False)  # user / assistant
    content = Column(Text, nullable=False)
    actions = Column(JSON, default=[])  # 执行的操作

    created_at = Column(DateTime, server_default=localnow_func())

    # 关系
    session = relationship("AgentSession", back_populates="messages")