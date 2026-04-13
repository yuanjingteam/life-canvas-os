"""
Agent State Definition for LangGraph

Defines the state structure used throughout the agent graph.
"""
from typing import Annotated, List, Optional, Dict, Any
from typing_extensions import TypedDict

from langchain_core.messages import BaseMessage


class AgentState(TypedDict):
    """Agent state for LangGraph StateGraph"""

    # Conversation history - annotated for message addition operator
    messages: Annotated[List[BaseMessage], "conversation history"]

    # Session identifier
    session_id: str

    # User ID (optional)
    user_id: Optional[int]

    # Pending tool calls waiting to be executed
    pending_tool_calls: List[Dict[str, Any]]

    # Results from tool executions
    tool_results: List[Dict[str, Any]]

    # Actions taken during the conversation
    actions: List[Dict[str, Any]]

    # Error message if any
    error: Optional[str]

    # Confirmation required for high-risk operations
    confirmation_required: Optional[Dict[str, Any]]

    # Whether the graph should continue or end
    should_continue: str

    # Output message to return
    output: str


def create_initial_state(
    session_id: str,
    user_id: Optional[int] = None,
    messages: Optional[List[BaseMessage]] = None
) -> AgentState:
    """
    Create initial agent state

    Args:
        session_id: Session identifier
        user_id: Optional user ID
        messages: Optional initial messages

    Returns:
        Initial AgentState
    """
    from langchain_core.messages import HumanMessage

    return AgentState(
        messages=messages or [HumanMessage(content="")],
        session_id=session_id,
        user_id=user_id,
        pending_tool_calls=[],
        tool_results=[],
        actions=[],
        error=None,
        confirmation_required=None,
        should_continue="continue",
        output=""
    )
