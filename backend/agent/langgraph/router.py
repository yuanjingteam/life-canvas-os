"""
Edge Routing Conditions for LangGraph

Defines the conditions for routing edges in the agent graph.
"""
from typing import Literal

from backend.agent.langgraph.state import AgentState


def should_continue(state: AgentState) -> Literal["tools", "confirm", " END"]:
    """
    Determine whether to continue the agent loop or end.

    Args:
        state: Current agent state

    Returns:
        Routing decision: "tools", "confirm", or " END"
    """
    # Check if there's an error
    if state.get("error"):
        return " END"

    # Check if confirmation is required
    if state.get("confirmation_required"):
        return "confirm"

    # Check if there are pending tool calls
    if state.get("pending_tool_calls"):
        return "tools"

    # Check if the last message contains tool calls
    messages = state.get("messages", [])
    if messages:
        last_msg = messages[-1]
        # Check for AIMessage with tool calls
        if hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
            return "tools"

    # Default: end the conversation
    return " END"


def should_interrupt(state: AgentState) -> bool:
    """
    Determine whether to interrupt for user confirmation.

    Args:
        state: Current agent state

    Returns:
        True if should interrupt for confirmation
    """
    confirmation = state.get("confirmation_required")
    if not confirmation:
        return False

    # Check if the confirmation hasn't been handled yet
    return confirmation.get("requires_confirmation", False)


def needs_confirmation(state: AgentState) -> Literal["confirm", "tools"]:
    """
    Decide between confirmation and tool execution.

    Args:
        state: Current agent state

    Returns:
        "confirm" if confirmation needed, "tools" otherwise
    """
    if state.get("confirmation_required"):
        return "confirm"
    return "tools"
