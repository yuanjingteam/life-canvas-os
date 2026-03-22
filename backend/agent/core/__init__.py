"""
Agent 核心模块
包含上下文管理和 Prompt 模板
"""

from backend.agent.core.context import ContextManager, get_context_manager, get_context_manager_with_db

__all__ = ["ContextManager", "get_context_manager", "get_context_manager_with_db"]