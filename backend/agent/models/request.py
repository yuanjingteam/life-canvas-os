"""
Agent 请求模型
"""
from typing import Optional
from pydantic import BaseModel, Field


class AgentRequest(BaseModel):
    """Agent 请求模型"""

    message: str = Field(..., description="用户消息内容")
    session_id: Optional[str] = Field(None, description="会话ID，用于多轮对话")
    stream: bool = Field(False, description="是否启用流式输出")

    model_config = {
        "protected_namespaces": (),
        "json_schema_extra": {
            "examples": [
                {
                    "message": "帮我写一篇日记，今天心情很好",
                    "session_id": "abc123",
                    "stream": False
                }
            ]
        }
    }


class ConfirmRequest(BaseModel):
    """确认操作请求"""

    session_id: str = Field(..., description="会话ID")
    confirmation_id: str = Field(..., description="确认ID")
    confirmed: bool = Field(..., description="是否确认执行")
    user_reason: Optional[str] = Field(None, description="用户拒绝原因")

    model_config = {"protected_namespaces": ()}