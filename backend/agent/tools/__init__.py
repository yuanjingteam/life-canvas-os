"""
Tool 工具模块

Tool 是原子化的、通用的、与领域无关的操作单元。
"""

from .base import BaseTool, ToolResult
from .registry import ToolRegistry

__all__ = [
    "BaseTool",
    "ToolResult",
    "ToolRegistry",
]
