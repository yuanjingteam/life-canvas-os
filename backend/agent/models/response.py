"""
Agent 响应模型
"""
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime
from pydantic import BaseModel, Field


class StreamChunk(BaseModel):
    """流式输出块"""

    type: Literal["stream_start", "stream_chunk", "stream_end"] = Field(
        ..., description="事件类型"
    )
    session_id: str = Field(..., description="会话ID")
    content: Optional[str] = Field(None, description="内容块")
    result: Optional[Dict[str, Any]] = Field(None, description="最终结果")

    model_config = {"protected_namespaces": ()}


class ActionInfo(BaseModel):
    """执行的操作信息"""

    skill: str = Field(..., description="技能名称")
    action: str = Field(..., description="具体操作")
    params: Dict[str, Any] = Field(default_factory=dict, description="操作参数")
    risk_level: str = Field("LOW", description="风险等级")

    model_config = {"protected_namespaces": ()}


class ConfirmationRequired(BaseModel):
    """需要确认的操作"""

    confirmation_id: str = Field(..., description="确认ID")
    action: ActionInfo = Field(..., description="待确认的操作")
    message: str = Field(..., description="提示消息")
    risk_level: str = Field(..., description="风险等级")
    requires_code: bool = Field(False, description="是否需要验证码")

    model_config = {"protected_namespaces": ()}


class AgentResponse(BaseModel):
    """Agent 响应模型"""

    session_id: str = Field(..., description="会话ID")
    message: str = Field(..., description="响应消息")
    actions: List[ActionInfo] = Field(
        default_factory=list, description="执行的操作列表"
    )
    confirmation_required: Optional[ConfirmationRequired] = Field(
        None, description="需要确认的操作"
    )
    error: Optional[str] = Field(None, description="错误信息")
    timestamp: datetime = Field(
        default_factory=datetime.now, description="响应时间"
    )

    model_config = {
        "protected_namespaces": (),
        "json_schema_extra": {
            "examples": [
                {
                    "session_id": "abc123",
                    "message": "已为您创建一篇日记",
                    "actions": [
                        {
                            "skill": "journal",
                            "action": "create_journal",
                            "params": {"content": "今天心情很好"},
                            "risk_level": "MEDIUM"
                        }
                    ],
                    "timestamp": "2024-01-01T12:00:00"
                }
            ]
        }
    }


class AgentHistoryResponse(BaseModel):
    """会话历史响应"""

    session_id: str
    messages: List[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime

    model_config = {"protected_namespaces": ()}