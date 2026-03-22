"""
Life Canvas OS - Agent 模块
AI 助手核心模块，支持自然语言交互

架构：
- Tools: 原子操作层，通用、可复用
- Skills: 业务能力层，编排 Tools，包含业务逻辑
- LangChain Agent: 执行引擎，使用 LangChain AgentExecutor
"""

from backend.agent.langchain.agent import AgentExecutor
from backend.agent.core.context import ContextManager, get_context_manager, get_context_manager_with_db
from backend.agent.skills.registry import SkillRegistry
from backend.agent.tools import DatabaseTool, DateTimeTool, ContextTool

__all__ = [
    "AgentExecutor",
    "ContextManager",
    "get_context_manager",
    "get_context_manager_with_db",
    "SkillRegistry",
    "DatabaseTool",
    "DateTimeTool",
    "ContextTool"
]