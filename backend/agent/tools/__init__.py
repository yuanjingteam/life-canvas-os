"""
Tool 工具模块
提供 Agent 可调用的底层工具

工具层原则：
- 原子操作：每个工具只做一件事
- 可复用：工具不包含业务逻辑
- 通用性：工具可以在不同 Skill 中复用
"""
from backend.agent.tools.base import BaseTool, ToolResult, ToolParameter
from backend.agent.tools.database import DatabaseTool
from backend.agent.tools.datetime import DateTimeTool
from backend.agent.tools.context import ContextTool

__all__ = [
    "BaseTool",
    "ToolResult",
    "ToolParameter",
    "DatabaseTool",
    "DateTimeTool",
    "ContextTool"
]