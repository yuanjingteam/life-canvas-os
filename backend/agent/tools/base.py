"""
Tool 基类定义

Tool 是原子化的、通用的、与领域无关的操作单元。
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Optional
import time


@dataclass
class ToolResult:
    """Tool 执行结果"""

    success: bool
    data: Any = None
    error: Optional[str] = None
    execution_time: float = field(default=0.0)

    @classmethod
    def ok(cls, data: Any, execution_time: float = 0.0) -> "ToolResult":
        """创建成功结果"""
        return cls(success=True, data=data, execution_time=execution_time)

    @classmethod
    def fail(cls, error: str) -> "ToolResult":
        """创建失败结果"""
        return cls(success=False, error=error)


class BaseTool(ABC):
    """Tool 基类"""

    # Tool 唯一标识
    name: str = ""

    # Tool 描述，面向 LLM
    description: str = ""

    # 参数 Schema（JSON Schema 格式）
    parameters: dict = field(default_factory=dict)

    def __init__(self):
        if not self.name:
            raise ValueError("Tool 必须定义 name")
        if not self.description:
            raise ValueError("Tool 必须定义 description")

    @abstractmethod
    async def execute(self, **kwargs) -> ToolResult:
        """
        执行 Tool 操作

        Args:
            **kwargs: 动态参数

        Returns:
            ToolResult: 执行结果
        """
        pass

    async def __call__(self, **kwargs) -> ToolResult:
        """允许像函数一样调用 Tool"""
        start_time = time.time()
        try:
            result = await self.execute(**kwargs)
            result.execution_time = time.time() - start_time
            return result
        except Exception as e:
            return ToolResult.fail(f"Tool 执行失败：{str(e)}")

    def validate_params(self, **kwargs) -> tuple[bool, Optional[str]]:
        """
        验证参数

        Args:
            **kwargs: 待验证的参数

        Returns:
            (是否有效，错误信息)
        """
        # 简单的必填参数验证
        for param_name, param_schema in self.parameters.get("properties", {}).items():
            if param_schema.get("required", False) and param_name not in kwargs:
                return False, f"缺少必填参数：{param_name}"
        return True, None
