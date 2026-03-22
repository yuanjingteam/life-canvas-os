"""
上下文操作工具
提供会话上下文的读写能力

设计原则：
- 原子操作：get/set 单一职责
- 可复用：供 Skills 管理会话状态
- 通用性：支持任意类型的上下文值
"""
from typing import Any, Dict, List, Optional

from backend.agent.tools.base import BaseTool, ToolResult, ToolParameter
from backend.agent.utils.logger import get_logger

logger = get_logger("context")


class ContextTool(BaseTool):
    """
    上下文操作工具

    提供会话上下文的读写操作，用于：
    - 存储实体引用（如最近操作的日记ID）
    - 获取上下文信息

    持久化策略：
    - 默认延迟持久化（auto_persist=False）
    - 需要时调用 flush() 手动触发
    """

    def __init__(self, context=None, context_manager=None, auto_persist=False):
        """
        初始化上下文工具

        Args:
            context: SessionContext 实例
            context_manager: ContextManager 实例（用于持久化）
            auto_persist: 是否自动持久化（默认False，使用延迟更新策略）
        """
        super().__init__()
        self.context = context
        self.context_manager = context_manager
        self.auto_persist = auto_persist
        self._pending_updates = {}  # 待持久化的更新

    @property
    def name(self) -> str:
        return "context"

    @property
    def description(self) -> str:
        return "上下文操作工具，用于存取会话状态"

    @property
    def parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="operation",
                type="string",
                description="操作类型：get/set",
                required=True,
                enum=["get", "set"]
            ),
            ToolParameter(
                name="key",
                type="string",
                description="上下文键名",
                required=True
            ),
            ToolParameter(
                name="value",
                type="any",
                description="要设置的值（仅 set 操作需要）",
                required=False
            )
        ]

    async def execute(self, **kwargs) -> ToolResult:
        """
        执行上下文操作

        这是一个通用入口，实际使用时建议直接调用具体方法。
        """
        operation = kwargs.get("operation")
        key = kwargs.get("key")

        if operation == "get":
            return await self.get(key)
        elif operation == "set":
            value = kwargs.get("value")
            return await self.set(key, value)
        else:
            return ToolResult(
                success=False,
                error=f"不支持的操作类型: {operation}"
            )

    async def get(self, key: str) -> ToolResult:
        """
        获取上下文值

        Args:
            key: 键名（如 last_journal_id, last_deviation_id）

        Returns:
            上下文值
        """
        if not self.context:
            return ToolResult(success=False, error="上下文不可用")

        try:
            value = self.context.get_entity_reference(key)
            return ToolResult(success=True, data={"key": key, "value": value})
        except Exception as e:
            logger.error(f"Context get failed: {e}")
            return ToolResult(success=False, error=str(e))

    async def set(self, key: str, value: Any) -> ToolResult:
        """
        设置上下文值

        Args:
            key: 键名
            value: 值

        Returns:
            操作结果
        """
        if not self.context:
            return ToolResult(success=False, error="上下文不可用")

        try:
            self.context.set_entity_reference(key, value)
            return ToolResult(
                success=True,
                data={"key": key, "value": value}
            )
        except Exception as e:
            logger.error(f"Context set failed: {e}")
            return ToolResult(success=False, error=str(e))

    def get_sync(self, key: str) -> Any:
        """
        同步获取上下文值（便捷方法）

        Args:
            key: 键名

        Returns:
            上下文值，不存在返回 None
        """
        if not self.context:
            return None
        return self.context.get_entity_reference(key)

    def set_sync(self, key: str, value: Any) -> None:
        """
        同步设置上下文值（延迟持久化）

        Args:
            key: 键名
            value: 值
        """
        if self.context:
            self.context.set_entity_reference(key, value)
            self._pending_updates[key] = value

            # 只有在 auto_persist=True 时才立即持久化
            if self.auto_persist and self.context_manager:
                self.context_manager.update_session(self.context)

    def flush(self) -> None:
        """
        手动触发持久化

        将所有待持久化的更新写入数据库。
        通常在会话结束时调用。
        """
        if self.context and self.context_manager and self._pending_updates:
            self.context_manager.update_session(self.context)
            self._pending_updates.clear()

    def get_pending_updates(self) -> Dict[str, Any]:
        """获取待持久化的更新"""
        return self._pending_updates.copy()