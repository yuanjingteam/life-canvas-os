"""
LangGraph Agent Executor

Replaces langchain/agent.py with a proper LangGraph StateGraph implementation.
Uses explicit graph construction with interrupt support for confirmations.
"""
import json
import asyncio
import uuid
from typing import Any, Dict, List, Optional, AsyncIterator

from langchain_core.messages import HumanMessage, AIMessage, BaseMessage, ToolMessage

from backend.agent.langgraph.state import AgentState, create_initial_state
from backend.agent.langgraph.nodes import (
    create_langchain_llm,
    build_chat_history,
    ToolExecutor
)
from backend.agent.langgraph.graph import create_agent_graph, InterruptException
from backend.agent.langgraph.tools import create_langchain_tools, validate_tool_name
from backend.agent.skills.registry import SkillRegistry
from backend.agent.core.context import ContextManager, get_context_manager_with_db
from backend.agent.models.response import AgentResponse, ActionInfo, ConfirmationRequired
from backend.agent.utils.logger import get_logger

logger = get_logger("langgraph_agent")


class AgentExecutor:
    """
    LangGraph-based Agent Executor

    Uses StateGraph instead of langchain.agents.create_agent for:
    1. Explicit control over ReAct loop
    2. Proper interrupt support for confirmations
    3. True token streaming support
    """

    def __init__(
        self,
        db_session=None,
        context_manager: Optional[ContextManager] = None
    ):
        """
        Initialize Agent Executor

        Args:
            db_session: Database session
            context_manager: Context manager (creates new if not provided)
        """
        self.db_session = db_session
        self.context_manager = context_manager or get_context_manager_with_db(db_session)

    def _create_llm(self, user_config: Dict[str, Any]):
        """
        Create LangChain LLM from user config

        Args:
            user_config: User AI configuration

        Returns:
            LangChain ChatModel
        """
        provider = user_config.get("provider")
        api_key = user_config.get("api_key")
        model = user_config.get("model")

        # Decrypt API key
        decrypted_key = api_key
        try:
            from backend.services.user_service import UserService
            decrypted_key = UserService.decrypt_api_key(api_key)
        except Exception:
            pass

        return create_langchain_llm(
            provider=provider,
            api_key=decrypted_key,
            model=model
        )

    def _build_initial_state(
        self,
        message: str,
        session_id: str,
        user_id: Optional[int],
        context
    ) -> AgentState:
        """
        Build initial agent state from context and new message

        Args:
            message: New user message
            session_id: Session ID
            user_id: User ID
            context: Session context

        Returns:
            Initial AgentState
        """
        # Get conversation history from context
        history = context.get_conversation_history()
        chat_history = build_chat_history(history)

        # Add the new message
        messages = chat_history + [HumanMessage(content=message)]

        state = create_initial_state(
            session_id=session_id,
            user_id=user_id,
            messages=messages
        )

        # Attach db session and context for tool execution
        state["db_session"] = self.db_session
        state["context"] = context
        state["context_manager"] = self.context_manager

        return state

    async def chat(
        self,
        message: str,
        session_id: Optional[str] = None,
        user_config: Optional[Dict[str, Any]] = None,
        user_id: Optional[int] = None
    ) -> AgentResponse:
        """
        Process user message

        Args:
            message: User message
            session_id: Session ID (creates new if not provided)
            user_config: User AI configuration
            user_id: User ID

        Returns:
            Agent response
        """
        # Get or create session
        context = self.context_manager.get_or_create_session(session_id, user_id=user_id)
        session_id = context.session_id

        try:
            # Create LLM
            llm = self._create_llm(user_config)

            # Create tools
            tools = create_langchain_tools(
                db_session=self.db_session,
                context=context,
                context_manager=self.context_manager
            )

            # Build initial state
            state = self._build_initial_state(message, session_id, user_id, context)

            # Build and compile graph
            from backend.agent.langgraph.graph import create_agent_graph
            graph = create_agent_graph(
                db_session=self.db_session,
                context=context,
                context_manager=self.context_manager,
                llm=llm
            )

            # Run graph with interrupt handling
            confirmation_required = None
            max_iterations = 30
            iteration = 0

            while iteration < max_iterations:
                iteration += 1

                try:
                    # Run LLM step
                    from backend.agent.langgraph.nodes import llm_node_async
                    state = await llm_node_async(state, llm, tools)

                    # Check if we need to execute tools
                    if state.get("pending_tool_calls"):
                        # Execute tools
                        from backend.agent.langgraph.nodes import tool_node
                        state = tool_node(state)

                        # Check for confirmation requirement
                        if state.get("confirmation_required"):
                            confirmation = state["confirmation_required"]
                            confirmation_required = ConfirmationRequired(
                                confirmation_id=confirmation.get("confirmation_id", str(uuid.uuid4())),
                                action=ActionInfo(
                                    skill=confirmation.get("skill", ""),
                                    action=confirmation.get("skill", ""),
                                    params=confirmation.get("params", {}),
                                    risk_level=confirmation.get("risk_level", "HIGH")
                                ),
                                message=confirmation.get("message", "此操作需要确认"),
                                risk_level=confirmation.get("risk_level", "HIGH")
                            )

                            # Save pending confirmation to context
                            context.set_entity_reference(
                                "pending_confirmation",
                                {
                                    "confirmation_id": confirmation_required.confirmation_id,
                                    "skill": confirmation.get("skill"),
                                    "params": confirmation.get("params", {})
                                }
                            )
                            break

                    # Check if should end
                    if state.get("should_continue") == " END":
                        break

                except Exception as e:
                    logger.error(f"Graph iteration error: {e}")
                    state["error"] = str(e)
                    state["should_continue"] = " END"
                    break

            # Extract output message
            output = state.get("output", "")
            if not output:
                # Get from last AI message
                for msg in reversed(state.get("messages", [])):
                    if isinstance(msg, AIMessage) and msg.content:
                        output = msg.content
                        break

            if not output:
                output = "抱歉，我无法处理您的请求。"

            # Collect actions
            actions = []
            for a in state.get("actions", []):
                actions.append(ActionInfo(
                    skill=a.get("skill", ""),
                    action=a.get("action", ""),
                    params=a.get("params", {}),
                    risk_level=a.get("risk_level", "LOW")
                ))

            # Save conversation to context
            self.context_manager.add_message(session_id, "user", message)
            self.context_manager.add_message(session_id, "assistant", output, [
                {"skill": a.skill, "action": a.action, "params": a.params, "risk_level": a.risk_level}
                for a in actions
            ])
            self.context_manager.update_session(context)

            return AgentResponse(
                session_id=session_id,
                message=output,
                actions=actions,
                confirmation_required=confirmation_required
            )

        except Exception as e:
            logger.error(f"Agent execution failed: {e}")
            return AgentResponse(
                session_id=session_id,
                message=f"处理出错: {str(e)}",
                error=str(e)
            )

    async def stream_chat(
        self,
        message: str,
        session_id: Optional[str] = None,
        user_config: Optional[Dict[str, Any]] = None,
        user_id: Optional[int] = None
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        Stream process user message

        Args:
            message: User message
            session_id: Session ID
            user_config: User AI configuration
            user_id: User ID

        Yields:
            Stream events
        """
        # Get or create session
        context = self.context_manager.get_or_create_session(session_id, user_id=user_id)
        session_id = context.session_id

        yield {
            "type": "stream_start",
            "session_id": session_id
        }

        try:
            # Create LLM
            llm = self._create_llm(user_config)

            # Create tools
            tools = create_langchain_tools(
                db_session=self.db_session,
                context=context,
                context_manager=self.context_manager
            )

            # Build initial state
            state = self._build_initial_state(message, session_id, user_id, context)

            # Build and compile graph
            from backend.agent.langgraph.graph import create_agent_graph
            graph = create_agent_graph(
                db_session=self.db_session,
                context=context,
                context_manager=self.context_manager,
                llm=llm
            )

            # Run graph with iteration
            confirmation_required = None
            max_iterations = 30
            iteration = 0
            full_output = ""

            while iteration < max_iterations:
                iteration += 1

                try:
                    # Run LLM step
                    from backend.agent.langgraph.nodes import llm_node_async
                    state = await llm_node_async(state, llm, tools)

                    # Stream tokens if we have output
                    if state.get("output"):
                        # Stream in chunks
                        chunk_size = 5
                        output = state["output"]
                        for i in range(0, len(output), chunk_size):
                            chunk = output[i:i + chunk_size]
                            full_output += chunk
                            yield {
                                "type": "stream_chunk",
                                "session_id": session_id,
                                "content": chunk
                            }
                            await asyncio.sleep(0.02)

                    # Check if we need to execute tools
                    if state.get("pending_tool_calls"):
                        # Execute tools
                        from backend.agent.langgraph.nodes import tool_node
                        state = tool_node(state)

                        # Continue to get next LLM response
                        continue

                    # Check for confirmation
                    if state.get("confirmation_required"):
                        confirmation = state["confirmation_required"]
                        confirmation_required = {
                            "confirmation_id": confirmation.get("confirmation_id", str(uuid.uuid4())),
                            "message": confirmation.get("message", "此操作需要确认"),
                            "risk_level": confirmation.get("risk_level", "HIGH"),
                            "action": {
                                "skill": confirmation.get("skill", ""),
                                "action": confirmation.get("skill", ""),
                                "params": confirmation.get("params", {}),
                                "risk_level": confirmation.get("risk_level", "HIGH")
                            }
                        }
                        break

                    # Check if should end
                    if state.get("should_continue") == " END":
                        break

                except Exception as e:
                    logger.error(f"Stream iteration error: {e}")
                    yield {
                        "type": "error",
                        "session_id": session_id,
                        "content": str(e)
                    }
                    return

            # Send final result
            def convert_params(params: Any) -> Any:
                if params is None:
                    return None
                if isinstance(params, dict):
                    return {k: convert_params(v) for k, v in params.items()}
                if isinstance(params, list):
                    return [convert_params(item) for item in params]
                if hasattr(params, 'model_dump'):
                    return params.model_dump()
                if hasattr(params, 'isoformat'):
                    return params.isoformat()
                return params

            result_data = {
                "session_id": session_id,
                "message": full_output or state.get("output", ""),
                "actions": [
                    {
                        "skill": a.get("skill", ""),
                        "action": a.get("action", ""),
                        "params": convert_params(a.get("params", {})),
                        "risk_level": a.get("risk_level", "LOW")
                    }
                    for a in state.get("actions", [])
                ],
                "timestamp": None
            }

            if confirmation_required:
                result_data["confirmation_required"] = confirmation_required

            yield {
                "type": "stream_end",
                "session_id": session_id,
                "result": result_data
            }

        except Exception as e:
            logger.error(f"Stream chat failed: {e}")
            yield {
                "type": "stream_end",
                "session_id": session_id,
                "error": str(e)
            }

    async def confirm_action(
        self,
        session_id: str,
        confirmation_id: str,
        confirmed: bool,
        user_reason: Optional[str] = None
    ) -> AgentResponse:
        """
        Confirm a pending action

        Args:
            session_id: Session ID
            confirmation_id: Confirmation ID
            confirmed: Whether user confirmed
            user_reason: User's reason (if rejected)

        Returns:
            Agent response
        """
        # Get session context
        context = self.context_manager.get_session(session_id)
        if not context:
            return AgentResponse(
                session_id=session_id,
                message="会话已过期，请重新开始",
                error="会话不存在"
            )

        # Get pending confirmation
        pending = context.referenced_entities.get("pending_confirmation")
        if not pending or pending.get("confirmation_id") != confirmation_id:
            return AgentResponse(
                session_id=session_id,
                message="确认信息无效或已过期",
                error="无效的确认ID"
            )

        if confirmed:
            # Execute the confirmed action
            skill_name = pending["skill"]
            params = pending["params"]
            return await self._execute_skill_direct(session_id, skill_name, params)
        else:
            # User rejected
            reason = user_reason or "用户取消操作"
            return AgentResponse(
                session_id=session_id,
                message=f"已取消操作。{reason}"
            )

    async def _execute_skill_direct(
        self,
        session_id: str,
        skill_name: str,
        params: Dict[str, Any]
    ) -> AgentResponse:
        """Directly execute a skill"""
        context = self.context_manager.get_session(session_id)

        result = await SkillRegistry.execute_skill(
            skill_name,
            params,
            self.db_session,
            context,
            self.context_manager
        )

        # Record operation
        self.context_manager.add_operation(
            session_id, skill_name, skill_name, params, result.data
        )

        # Record assistant message
        self.context_manager.add_message(session_id, "assistant", result.message)

        return AgentResponse(
            session_id=session_id,
            message=result.message,
            actions=[
                ActionInfo(
                    skill=skill_name,
                    action=skill_name,
                    params=params,
                    risk_level=result.risk_level.value
                )
            ] if result.success else []
        )
