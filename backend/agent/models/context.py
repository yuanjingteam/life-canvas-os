"""
Agent 上下文模型
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
import uuid


class Message(BaseModel):
    """对话消息"""

    role: str = Field(..., description="角色: user 或 assistant")
    content: str = Field(..., description="消息内容")
    timestamp: datetime = Field(
        default_factory=datetime.now, description="消息时间"
    )
    actions: List[Dict[str, Any]] = Field(
        default_factory=list, description="执行的操作"
    )

    model_config = {"protected_namespaces": ()}


class SessionContext(BaseModel):
    """会话上下文"""

    # 类级别配置：内存中保留的最大消息数
    MAX_MESSAGES_IN_MEMORY: int = 50

    session_id: str = Field(
        default_factory=lambda: str(uuid.uuid4())[:8],
        description="会话ID"
    )
    messages: List[Message] = Field(
        default_factory=list,
        description="对话历史"
    )
    last_operations: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="最近执行的操作"
    )
    referenced_entities: Dict[str, Any] = Field(
        default_factory=dict,
        description="实体引用（如 journal_id）"
    )
    created_at: datetime = Field(
        default_factory=datetime.now,
        description="创建时间"
    )
    updated_at: datetime = Field(
        default_factory=datetime.now,
        description="更新时间"
    )

    model_config = {"protected_namespaces": ()}

    def add_message(self, role: str, content: str, actions: List[Dict[str, Any]] = None):
        """添加消息到历史"""
        message = Message(
            role=role,
            content=content,
            actions=actions or []
        )
        self.messages.append(message)
        # 保持内存中的消息数不超过配置值
        if len(self.messages) > self.MAX_MESSAGES_IN_MEMORY:
            self.messages = self.messages[-self.MAX_MESSAGES_IN_MEMORY:]
        self.updated_at = datetime.now()

    def get_conversation_history(self, max_messages: int = 20) -> List[Dict[str, str]]:
        """获取对话历史（格式化为 LLM 输入）

        Args:
            max_messages: 返回的最大消息数，默认20条（10轮对话）
        """
        recent = self.messages[-max_messages:] if len(self.messages) > max_messages else self.messages
        return [{"role": m.role, "content": m.content} for m in recent]

    def set_entity_reference(self, entity_type: str, entity_id: Any):
        """设置实体引用"""
        self.referenced_entities[entity_type] = entity_id
        self.updated_at = datetime.now()

    def get_entity_reference(self, entity_type: str) -> Optional[Any]:
        """获取实体引用"""
        return self.referenced_entities.get(entity_type)