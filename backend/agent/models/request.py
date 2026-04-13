"""
请求模型
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class ChatMessage(BaseModel):
    """聊天消息"""

    role: str  # user, assistant, system
    content: str
    timestamp: Optional[datetime] = None


class AgentRequest(BaseModel):
    """Agent 请求"""

    message: str = Field(..., description="用户消息")
    session_id: Optional[str] = Field(None, description="会话 ID")

    class Config:
        json_schema_extra = {
            "example": {
                "message": "帮我写一篇日记，今天心情很好",
                "session_id": "sess_abc123",
            }
        }
