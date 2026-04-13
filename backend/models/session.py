"""Agent 会话模型"""
from datetime import datetime
from sqlalchemy import String, Text, DateTime, Integer, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.db.base import Base


class AgentSession(Base):
    """
    Agent 会话表

    存储所有 Agent 会话的基本信息和消息历史
    """
    __tablename__ = "agent_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)

    # 会话元数据
    title: Mapped[str | None] = mapped_column(String(256), nullable=True, comment="会话标题（由 AI 生成）")
    message_count: Mapped[int] = mapped_column(Integer, default=0, comment="消息数量")

    # 时间戳
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)

    # 会话状态
    is_active: Mapped[bool] = mapped_column(default=True, comment="是否活跃")

    # 外键关系 - 使用 cascade 删除
    messages: Mapped[list["AgentMessage"]] = relationship(
        back_populates="session",
        cascade="all, delete-orphan",
        lazy="select"
    )

    def __repr__(self) -> str:
        return f"<AgentSession(session_id={self.session_id}, title={self.title})>"


class AgentMessage(Base):
    """
    Agent 消息表

    存储会话中的每条消息
    """
    __tablename__ = "agent_messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(String(64), ForeignKey("agent_sessions.session_id", ondelete="CASCADE"), nullable=False, index=True)

    # 消息内容
    role: Mapped[str] = mapped_column(String(32), nullable=False, comment="消息角色：user/assistant")
    content: Mapped[str] = mapped_column(Text, nullable=False, comment="消息内容")

    # 消息元数据
    token_count: Mapped[int | None] = mapped_column(Integer, default=0, comment="消息 token 数")
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)

    # 扩展信息（用于存储工具调用、确认请求等）
    extra_data: Mapped[dict | None] = mapped_column(JSON, nullable=True, comment="扩展元数据")

    # 外键关系
    session: Mapped["AgentSession"] = relationship(back_populates="messages")

    def __repr__(self) -> str:
        return f"<AgentMessage(session_id={self.session_id}, role={self.role}, timestamp={self.timestamp})>"
