"""
上下文模型
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime


@dataclass
class ContextState:
    """上下文状态"""

    session_id: str
    created_at: datetime = field(default_factory=datetime.now)
    messages: List[Dict[str, Any]] = field(default_factory=list)
    last_operations: List[Dict[str, Any]] = field(default_factory=list)
    referenced_entities: Dict[str, Any] = field(default_factory=dict)
    token_count: int = 0

    def add_message(self, role: str, content: str) -> None:
        """添加消息"""
        self.messages.append(
            {
                "role": role,
                "content": content,
                "timestamp": datetime.now().isoformat(),
            }
        )

    def add_operation(self, skill: str, result: Dict[str, Any]) -> None:
        """添加操作记录"""
        self.last_operations.append(
            {"skill": skill, "result": result, "timestamp": datetime.now().isoformat()}
        )
        # 保留最近 10 条操作
        if len(self.last_operations) > 10:
            self.last_operations = self.last_operations[-10:]

    def set_reference(self, key: str, value: Any) -> None:
        """设置实体引用"""
        self.referenced_entities[key] = value

    def get_reference(self, key: str, default: Any = None) -> Any:
        """获取实体引用"""
        return self.referenced_entities.get(key, default)

    def clear(self) -> None:
        """清空上下文"""
        self.messages.clear()
        self.last_operations.clear()
        self.referenced_entities.clear()
        self.token_count = 0
