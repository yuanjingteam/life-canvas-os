"""
Agent 模块初始化

负责初始化 LLM 客户端、注册 Skills、创建执行器实例。
"""

import os
from typing import Dict, Any, Optional
from .llm.base import LLMClient, LLMMessage, LLMToolDefinition, LLMResponse, LLMProviderType
from .llm.client_with_fallback import LLMClientWithFallback
from .llm.factory import LLMClientFactory
from .skills.base import BaseSkill, RiskLevel
from .skills.registry import SkillRegistry
from .tools.registry import ToolRegistry
from .core.context import ContextManager, get_context_manager
from .core.executor import ReActExecutor

# 全局 Agent 执行器实例
_agent_executor: Optional[ReActExecutor] = None
_context_manager: Optional[ContextManager] = None
_pending_confirmations: Dict[str, Dict[str, Any]] = {}


def _create_llm_client_with_fallback() -> LLMClientWithFallback:
    """
    创建带故障转移的 LLM 客户端

    Returns:
        LLMClientWithFallback: LLM 客户端实例
    """
    clients = []

    # 尝试创建 DeepSeek 客户端
    deepseek_key = os.environ.get("DEEPSEEK_API_KEY", "")
    if deepseek_key:
        try:
            from .llm.deepseek import DeepSeekClient
            client = LLMClientFactory.create(
                LLMProviderType.DEEPSEEK,
                {"api_key": deepseek_key, "base_url": "https://api.deepseek.com", "model": "deepseek-chat"}
            )
            if client:
                clients.append(client)
        except Exception as e:
            print(f"创建 DeepSeek 客户端失败：{e}")

    # 尝试创建豆包客户端
    doubao_key = os.environ.get("DOUBAO_API_KEY", "")
    if doubao_key:
        try:
            from .llm.doubao import DoubaoClient
            client = LLMClientFactory.create(
                LLMProviderType.DOUBAO,
                {"api_key": doubao_key, "base_url": "https://ark.cn-beijing.volces.com/api/v3", "model": "doubao-pro-32k"}
            )
            if client:
                clients.append(client)
        except Exception as e:
            print(f"创建豆包客户端失败：{e}")

    # 如果没有任何客户端，创建一个空的 DeepSeek 客户端（会在运行时失败）
    if not clients:
        from .llm.deepseek import DeepSeekClient
        clients.append(DeepSeekClient(api_key="", base_url="https://api.deepseek.com", model="deepseek-chat"))

    return LLMClientWithFallback(clients=clients)


def initialize_agent() -> ReActExecutor:
    """
    初始化 Agent 执行器

    Returns:
        ReActExecutor: Agent 执行器实例
    """
    global _agent_executor, _context_manager

    # 创建 LLM 客户端（带故障转移）
    llm_client = _create_llm_client_with_fallback()

    # 获取上下文管理器
    _context_manager = get_context_manager()

    # 创建 Skill 注册中心并注册所有 Skills
    skill_registry = SkillRegistry()
    skill_registry.register(CreateJournalSkill(), category="journal")
    skill_registry.register(QueryJournalsSkill(), category="journal")
    skill_registry.register(UpdateJournalSkill(), category="journal")
    skill_registry.register(DeleteJournalSkill(), category="journal")

    # 获取所有 Skills
    skills = skill_registry.get_all()

    # 创建 Tool 注册中心（预留扩展）
    tool_registry = ToolRegistry()
    tools = tool_registry.get_all()

    # 创建执行器
    _agent_executor = ReActExecutor(
        llm_client=llm_client,
        context_manager=_context_manager,
        skills=skills,
        tools=tools,
    )

    return _agent_executor


def get_agent_executor() -> Optional[ReActExecutor]:
    """获取 Agent 执行器实例"""
    return _agent_executor


def get_context_manager_instance() -> Optional[ContextManager]:
    """获取上下文管理器实例"""
    return _context_manager


def get_pending_confirmations() -> Dict[str, Dict[str, Any]]:
    """获取待确认请求字典"""
    return _pending_confirmations


async def execute_chat(
    message: str,
    session_id: Optional[str] = None,
    user_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    执行聊天请求

    Args:
        message: 用户消息
        session_id: 会话 ID
        user_id: 用户 ID

    Returns:
        响应数据字典
    """
    global _agent_executor, _pending_confirmations

    # 如果执行器未初始化，则初始化
    if _agent_executor is None:
        _agent_executor = initialize_agent()

    # 执行 ReAct 循环
    result, requires_confirmation = await _agent_executor.execute(
        message=message,
        session_id=session_id,
        user_id=user_id,
    )

    # 构建响应
    response_data = {
        "response": result.response,
        "action_taken": result.data,
        "requires_confirmation": result.requires_confirmation,
        "session_id": session_id,
    }

    # 处理确认请求
    if result.requires_confirmation:
        confirmation_id = result.confirmation_id or f"confirm_{len(_pending_confirmations) + 1}"

        # 存储确认请求
        _pending_confirmations[confirmation_id] = {
            "session_id": session_id,
            "risk_level": RiskLevel.HIGH.value,  # 默认高风险
            "action_type": "delete_journal" if "delete" in (result.data or {}) else "unknown",
            "action_data": result.data or {},
            "confirmation_message": result.confirmation_message,
        }

        response_data["confirmation_id"] = confirmation_id
        response_data["confirmation_message"] = result.confirmation_message

    return response_data


# 在这里导入以避免循环依赖
from .skills.journal_skills import (
    CreateJournalSkill,
    QueryJournalsSkill,
    UpdateJournalSkill,
    DeleteJournalSkill,
)
