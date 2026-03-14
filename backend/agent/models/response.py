"""
响应模型
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any


class ActionTaken(BaseModel):
    """已执行的操作"""

    skill: str = Field(..., description="使用的技能")
    params: Optional[Dict[str, Any]] = Field(None, description="技能参数")
    result: Optional[Dict[str, Any]] = Field(None, description="执行结果")


class ConfirmationRequest(BaseModel):
    """确认请求"""

    confirmation_id: str = Field(..., description="确认 ID")
    confirmed: bool = Field(..., description="是否确认")
    code: Optional[str] = Field(None, description="验证码（CRITICAL 等级需要）")


class AgentResponse(BaseModel):
    """Agent 响应"""

    response: str = Field(..., description="AI 回复内容")
    action_taken: Optional[ActionTaken] = Field(None, description="已执行的操作")
    requires_confirmation: bool = Field(False, description="是否需要确认")
    confirmation_id: Optional[str] = Field(None, description="确认 ID")
    confirmation_message: Optional[str] = Field(None, description="确认消息")

    class Config:
        json_schema_extra = {
            "example": {
                "response": "已为您创建日记《今天心情很好》！",
                "action_taken": {
                    "skill": "create_journal",
                    "params": {"title": "今天心情很好", "mood": "good"},
                    "result": {"id": 123},
                },
                "requires_confirmation": False,
            }
        }
