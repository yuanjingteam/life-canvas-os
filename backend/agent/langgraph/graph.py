"""
LangGraph Construction for Agent

Builds the StateGraph for the ReAct agent with proper routing.
"""
from typing import Any, Dict, Optional

from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

from backend.agent.langgraph.state import AgentState
from backend.agent.langgraph.nodes import (
    llm_node_async,
    tool_node,
    confirm_interrupt_node,
    error_node,
    ToolExecutor
)
from backend.agent.langgraph.router import should_continue, needs_confirmation
from backend.agent.langgraph.tools import create_langchain_tools


def create_agent_graph(
    db_session=None,
    context=None,
    context_manager=None,
    llm=None,
    user_config: Optional[Dict[str, Any]] = None
) -> StateGraph:
    """
    Create the agent StateGraph

    Args:
        db_session: Database session
        context: Session context
        context_manager: Context manager for persistence
        llm: Pre-configured LangChain LLM (optional, will create from config if not provided)
        user_config: User AI config for LLM creation

    Returns:
        Compiled StateGraph
    """
    from backend.agent.langgraph.nodes import create_langchain_llm

    # Create LLM if not provided
    if llm is None:
        if not user_config:
            raise ValueError("Either llm or user_config must be provided")
        provider = user_config.get("provider")
        api_key = user_config.get("api_key")
        model = user_config.get("model")
        decrypted_key = api_key

        # Try to decrypt API key
        try:
            from backend.services.user_service import UserService
            decrypted_key = UserService.decrypt_api_key(api_key)
        except Exception:
            pass

        llm = create_langchain_llm(
            provider=provider,
            api_key=decrypted_key,
            model=model
        )

    # Create tools
    tools = create_langchain_tools(
        db_session=db_session,
        context=context,
        context_manager=context_manager
    )

    # Build the graph
    graph = StateGraph(AgentState)

    # Add nodes
    graph.add_node("llm", lambda state: llm_node_async(state, llm, tools))
    graph.add_node("tools", tool_node)
    graph.add_node("confirm", confirm_interrupt_node)
    graph.add_node("error", error_node)

    # Set entry point
    graph.set_entry_point("llm")

    # Add edges
    # llm -> decide (tools/confirm/end)
    graph.add_conditional_edges(
        "llm",
        should_continue,
        {
            "tools": "tools",
            "confirm": "confirm",
            " END": END
        }
    )

    # tools -> llm (if no confirmation) or confirm
    graph.add_conditional_edges(
        "tools",
        needs_confirmation,
        {
            "confirm": "confirm",
            "tools": "llm"  # Loop back to LLM
        }
    )

    # confirm -> llm (after user confirms) or END (if rejected)
    # Note: actual routing is handled in post_confirm_node in the executor

    # Compile the graph
    return graph.compile()


class InterruptException(Exception):
    """Raised when agent needs user confirmation"""

    def __init__(self, confirmation_data: Dict[str, Any]):
        self.confirmation_data = confirmation_data
        super().__init__(f"Confirmation required: {confirmation_data.get('skill')}")


def run_graph_with_interrupts(
    graph: StateGraph,
    initial_state: AgentState,
    config: Dict[str, Any]
) -> Any:
    """
    Run the graph with interrupt support for confirmations

    Args:
        graph: Compiled StateGraph
        initial_state: Initial agent state
        config: Graph configuration

    Returns:
        Final state or raises InterruptException for confirmations
    """
    state = initial_state
    max_iterations = 50  # Prevent infinite loops
    iteration = 0

    while iteration < max_iterations:
        iteration += 1

        try:
            # Run one step
            state = graph.invoke(state, config)

            # Check if interrupted for confirmation
            if state.get("confirmation_required"):
                confirmation = state["confirmation_required"]
                if confirmation.get("requires_confirmation"):
                    raise InterruptException(confirmation)

            # Check if should end
            if state.get("should_continue") == " END":
                break

        except InterruptException:
            raise
        except Exception as e:
            logger.error(f"Graph execution error: {e}")
            state = error_node(state, e)
            break

    return state


# Import logger
from backend.agent.utils.logger import get_logger
logger = get_logger("langgraph_graph")
