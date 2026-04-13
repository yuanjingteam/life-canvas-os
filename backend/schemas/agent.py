"""
Agent Schema 定义
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any


class ChatRequest(BaseModel):
    """聊天请求"""

    message: str = Field(..., description="用户消息", min_length=1, max_length=2000)
    session_id: Optional[str] = Field(None, description="会话 ID")


class ChatResponse(BaseModel):
    """聊天响应"""

    response: str = Field(..., description="AI 回复内容")
    action_taken: Optional[Dict[str, Any]] = Field(None, description="已执行的操作")
    requires_confirmation: bool = Field(False, description="是否需要确认")
    confirmation_id: Optional[str] = Field(None, description="确认 ID")
    confirmation_message: Optional[str] = Field(None, description="确认消息")


class ConfirmRequest(BaseModel):
    """确认请求"""

    session_id: str = Field(..., description="会话 ID")
    confirmation_id: str = Field(..., description="确认 ID")
    confirmed: bool = Field(..., description="是否确认")
    code: Optional[str] = Field(None, description="验证码（CRITICAL 等级需要）")


class ConfirmResponse(BaseModel):
    """确认响应"""

    response: str = Field(..., description="AI 回复内容")
    action_taken: Optional[Dict[str, Any]] = Field(None, description="已执行的操作")


class HistoryResponse(BaseModel):
    """历史记录响应"""

    messages: list = Field(..., description="消息列表")
    session_id: str = Field(..., description="会话 ID")
