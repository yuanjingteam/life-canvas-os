"""
LangGraph Agent Module

Replaces langchain/agent.py with a proper LangGraph StateGraph implementation.
Provides explicit control over ReAct loop with proper interrupt support.
"""
from backend.agent.langgraph.agent import AgentExecutor
from backend.agent.langgraph.state import AgentState, create_initial_state
from backend.agent.langgraph.nodes import create_langchain_llm, build_chat_history
from backend.agent.langgraph.graph import create_agent_graph
from backend.agent.langgraph.checkpointer import (
    AgentCheckpointer,
    sync_state_to_context,
    load_context_for_state
)

__all__ = [
    # Main executor
    "AgentExecutor",
    # State
    "AgentState",
    "create_initial_state",
    # Utilities
    "create_langchain_llm",
    "build_chat_history",
    # Graph
    "create_agent_graph",
    # Checkpointing
    "AgentCheckpointer",
    "sync_state_to_context",
    "load_context_for_state"
]
