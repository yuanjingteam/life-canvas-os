"""
Session Persistence via ContextManager

LangGraph checkpointer is not used - instead we use the existing
ContextManager for session persistence which is already implemented
and working with database persistence.

This module provides integration utilities between LangGraph state
and the existing ContextManager.
"""
from typing import Any, Dict, Optional, List

from langchain_core.messages import HumanMessage, AIMessage, BaseMessage

from backend.agent.core.context import ContextManager
from backend.agent.models.context import SessionContext
from backend.agent.utils.logger import get_logger

logger = get_logger("checkpointer")


def state_to_messages(state: Dict[str, Any]) -> List[Dict[str, str]]:
    """
    Extract conversation history from agent state for ContextManager

    Args:
        state: Agent state dict

    Returns:
        List of message dicts with role and content
    """
    messages = state.get("messages", [])
    result = []

    for msg in messages:
        if isinstance(msg, HumanMessage):
            result.append({"role": "user", "content": msg.content})
        elif isinstance(msg, AIMessage):
            result.append({"role": "assistant", "content": msg.content or ""})
        # Skip ToolMessages in history for LLM context

    return result


def actions_to_list(actions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Convert actions from agent state to ContextManager format

    Args:
        actions: List of action dicts from state

    Returns:
        Formatted actions list
    """
    result = []
    for action in actions:
        result.append({
            "skill": action.get("skill", ""),
            "action": action.get("action", ""),
            "params": action.get("params", {}),
            "risk_level": action.get("risk_level", "LOW")
        })
    return result


def sync_state_to_context(
    session_id: str,
    state: Dict[str, Any],
    context_manager: ContextManager
):
    """
    Sync agent state to ContextManager for persistence

    Args:
        session_id: Session identifier
        state: Current agent state
        context_manager: ContextManager instance
    """
    # Get context
    context = context_manager.get_session(session_id)
    if not context:
        logger.warning(f"Session not found for sync: {session_id}")
        return

    # Add messages to context
    messages = state_to_messages(state)
    for msg in messages:
        # Only add if not already in context
        existing = [m for m in context.messages if m.role == msg["role"] and m.content == msg["content"]]
        if not existing:
            context.add_message(msg["role"], msg["content"])

    # Update actions
    actions = actions_to_list(state.get("actions", []))
    for action in actions:
        context_manager.add_operation(
            session_id,
            skill=action["skill"],
            action=action["action"],
            params=action["params"],
            result=None
        )

    # Update session
    context_manager.update_session(context)


def load_context_for_state(
    session_id: str,
    context_manager: ContextManager
) -> Optional[List[BaseMessage]]:
    """
    Load conversation history from ContextManager into LangChain messages

    Args:
        session_id: Session identifier
        context_manager: ContextManager instance

    Returns:
        List of LangChain BaseMessages or None
    """
    context = context_manager.get_session(session_id)
    if not context:
        return None

    messages = []
    for msg in context.messages:
        if msg.role == "user":
            messages.append(HumanMessage(content=msg.content))
        elif msg.role == "assistant":
            messages.append(AIMessage(content=msg.content))

    return messages


class AgentCheckpointer:
    """
    Checkpointer that uses ContextManager for persistence

    This is a compatibility layer that adapts ContextManager
    to work with LangGraph's checkpointing interface if needed.
    """

    def __init__(self, context_manager: ContextManager):
        self.context_manager = context_manager

    def get(self, config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Get checkpoint for a given configuration

        Args:
            config: Checkpoint config with session_id

        Returns:
            State dict or None
        """
        session_id = config.get("configurable", {}).get("session_id")
        if not session_id:
            return None

        messages = load_context_for_state(session_id, self.context_manager)
        if messages is None:
            return None

        return {
            "messages": messages,
            "pending_tool_calls": [],
            "tool_results": [],
            "actions": [],
            "error": None,
            "confirmation_required": None,
            "should_continue": "continue",
            "output": ""
        }

    def put(self, config: Dict[str, Any], state: Dict[str, Any]) -> None:
        """
        Save checkpoint

        Args:
            config: Checkpoint config with session_id
            state: State to save
        """
        session_id = config.get("configurable", {}).get("session_id")
        if not session_id:
            return

        sync_state_to_context(session_id, state, self.context_manager)
