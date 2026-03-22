"""
Agent API Schema
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class AgentChatRequest(BaseModel):
    """Agent 聊天请求"""

    message: str = Field(..., description="用户消息")
    session_id: Optional[str] = Field(None, description="会话ID")
    stream: bool = Field(False, description="是否流式输出")

    model_config = {"protected_namespaces": ()}


class AgentConfirmRequest(BaseModel):
    """Agent 确认请求"""

    session_id: str = Field(..., description="会话ID")
    confirmation_id: str = Field(..., description="确认ID")
    confirmed: bool = Field(..., description="是否确认")
    user_reason: Optional[str] = Field(None, description="拒绝原因")

    model_config = {"protected_namespaces": ()}


class ActionInfoSchema(BaseModel):
    """操作信息"""

    skill: str
    action: str
    params: Dict[str, Any] = Field(default_factory=dict)
    risk_level: str = "LOW"

    model_config = {"protected_namespaces": ()}


class ConfirmationSchema(BaseModel):
    """确认信息"""

    confirmation_id: str
    action: ActionInfoSchema
    message: str
    risk_level: str
    requires_code: bool = False

    model_config = {"protected_namespaces": ()}


class AgentChatResponse(BaseModel):
    """Agent 聊天响应"""

    session_id: str
    message: str
    actions: List[ActionInfoSchema] = Field(default_factory=list)
    confirmation_required: Optional[ConfirmationSchema] = None
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)

    model_config = {"protected_namespaces": ()}


class AgentHistoryResponse(BaseModel):
    """Agent 历史响应"""

    session_id: str
    messages: List[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime

    model_config = {"protected_namespaces": ()}