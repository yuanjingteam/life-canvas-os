"""
LangChain 集成模块
提供 LangChain Agent 和 Tools 支持
"""
from backend.agent.langchain.tools import (
    create_langchain_tools,
    create_langchain_tool_from_skill,
    get_tool_schemas
)
from backend.agent.langchain.agent import (
    AgentExecutor,
    create_langchain_llm,
    build_chat_history
)

__all__ = [
    # Tools
    "create_langchain_tools",
    "create_langchain_tool_from_skill",
    "get_tool_schemas",
    # Agent
    "AgentExecutor",
    "create_langchain_llm",
    "build_chat_history"
]