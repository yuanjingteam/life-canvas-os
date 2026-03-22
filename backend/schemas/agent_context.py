"""
Agent 上下文 Schema
用于会话持久化相关的 API 响应
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class MessageResponse(BaseModel):
    """消息响应"""

    id: int
    role: str
    content: str
    actions: List[Dict[str, Any]] = Field(default_factory=list)
    created_at: datetime

    model_config = {"protected_namespaces": ()}


class AgentSessionResponse(BaseModel):
    """会话响应"""

    session_id: str
    title: Optional[str] = None
    messages: List[MessageResponse] = Field(default_factory=list)
    referenced_entities: Dict[str, Any] = Field(default_factory=dict)
    last_operations: List[Dict[str, Any]] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
    expires_at: Optional[datetime] = None

    model_config = {"protected_namespaces": ()}


class AgentSessionListItem(BaseModel):
    """会话列表项"""

    session_id: str
    title: Optional[str] = None
    message_count: int
    created_at: datetime
    updated_at: datetime
    last_message: Optional[str] = None
    pinned: int = 0  # 0: 未固定, 1: 已固定

    model_config = {"protected_namespaces": ()}


class AgentSessionListResponse(BaseModel):
    """会话列表响应"""

    sessions: List[AgentSessionListItem]
    total: int

    model_config = {"protected_namespaces": ()}