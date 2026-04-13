"""
Node Functions for LangGraph Agent

Implements the nodes used in the ReAct agent graph:
- llm_node: Calls LLM with system prompt + history
- tool_node: Executes tools via ToolNode
- decide_node: Routes based on LLM output
- confirm_interrupt_node: Suspends for user confirmation
- post_confirm_node: Handles user response after interrupt
- error_node: Handles exceptions
"""
import json
import uuid
from typing import Any, Dict, List, Optional, AsyncIterator

from langchain_core.messages import (
    HumanMessage,
    AIMessage,
    SystemMessage,
    BaseMessage,
    ToolMessage,
    message_to_dict,
    messages_to_dict
)
from langchain_core.language_models import BaseChatModel
from langchain_openai import ChatOpenAI

from backend.agent.langgraph.state import AgentState
from backend.agent.langgraph.tools import create_langchain_tools
from backend.agent.core.context import ContextManager, get_context_manager_with_db
from backend.agent.models.response import AgentResponse, ActionInfo, ConfirmationRequired
from backend.agent.utils.logger import get_logger

logger = get_logger("langgraph_nodes")

# System prompt for the agent
AGENT_SYSTEM_PROMPT = """你是 Life Canvas OS 的 AI 助手，一个帮助用户管理个人生活的智能助手。

## 你的能力
你可以帮助用户：
1. 管理日记：创建、查看、修改、删除日记
2. 管理系统评分：查看和更新八维系统评分
3. 生成洞察：基于系统评分生成 AI 建议
4. 管理饮食系统：设置饮食基准、记录偏离事件、查看统计信息

## 八维系统说明
Life Canvas OS 基于"八维生命平衡模型"，包含以下系统：
- FUEL（饮食系统）：管理饮食习惯，支持基准设置和偏离记录
- PHYSICAL（运动系统）：管理运动健身
- INTELLECTUAL（读书系统）：管理学习成长
- OUTPUT（工作系统）：管理工作产出
- DREAM（梦想系统）：管理个人梦想与恢复
- ASSET（财务系统）：管理财务状况
- CONNECTION（社交系统）：管理社交关系
- ENVIRONMENT（环境系统）：管理生活环境

## 行为规范
1. 始终使用中文回复
2. 对于模糊的请求，主动澄清确认
3. 简洁明了，避免冗长的解释
4. 根据用户请求选择合适的工具执行操作
5. 对于日期相关的查询（如"最近一周"、"昨天"），使用自然语言日期表达式作为参数

## 上下文记忆
- 你可以记住最近操作的实体（如最后创建的日记ID）
- 用户说"刚才那个"、"最近那个"时，使用上下文中的引用实体ID

## 重要约束（防止错误）
1. **只能使用提供的工具**：不要编造工具名称，不要猜测不存在的工具
2. **超出能力范围时**：直接告知用户"抱歉，我暂时无法帮您完成这个操作"，并说明你能做什么
3. **参数值必须符合约束**：
   - system_type 只能是: FUEL, PHYSICAL, INTELLECTUAL, OUTPUT, DREAM, ASSET, CONNECTION, ENVIRONMENT
   - meal_type 只能是: breakfast, lunch, dinner, taste
   - mood 只能是: great(很棒), good(不错), neutral(一般), bad(不好), terrible(很糟)
4. **不要猜测参数**：如果用户没有提供必要的参数值，询问用户而不是编造
5. **删除操作需要确认**：删除日记或偏离记录时，系统会自动要求确认，你只需要正常执行工具调用"""


def create_langchain_llm(
    provider: str,
    api_key: str,
    model: Optional[str] = None,
    temperature: float = 0.7
) -> BaseChatModel:
    """
    Create LangChain compatible LLM

    Args:
        provider: Provider name (deepseek, doubao)
        api_key: API key
        model: Model name
        temperature: Temperature parameter

    Returns:
        LangChain ChatModel instance
    """
    provider_config = {
        "deepseek": {
            "base_url": "https://api.deepseek.com/v1",
            "default_model": "deepseek-chat"
        },
        "doubao": {
            "base_url": "https://ark.cn-beijing.volces.com/api/v3",
            "default_model": "doubao-seed-2-0-lite-260215"
        }
    }

    config = provider_config.get(provider.lower())
    if not config:
        raise ValueError(f"不支持的 AI 提供商: {provider}")

    model_name = model or config["default_model"]

    llm = ChatOpenAI(
        model=model_name,
        api_key=api_key,
        base_url=config["base_url"],
        temperature=temperature
    )

    return llm


def build_chat_history(messages: List[Dict[str, str]]) -> List[BaseMessage]:
    """
    Convert message history to LangChain message format

    Args:
        messages: Message list [{"role": "user/assistant", "content": "..."}]

    Returns:
        LangChain message list
    """
    chat_history = []
    for msg in messages:
        role = msg.get("role", "")
        content = msg.get("content", "")
        if role == "user":
            chat_history.append(HumanMessage(content=content))
        elif role == "assistant":
            chat_history.append(AIMessage(content=content))
    return chat_history


def llm_node(
    state: AgentState,
    llm: BaseChatModel,
    tools: Optional[List[Any]] = None
) -> AgentState:
    """
    LLM node - calls the LLM with system prompt and conversation history

    Args:
        state: Current agent state
        llm: LangChain ChatModel instance
        tools: Optional list of tools for binding

    Returns:
        Updated agent state
    """
    from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

    # Build prompt with system message and conversation history
    prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content=AGENT_SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="messages")
    ])

    # Get conversation messages
    messages = state.get("messages", [])

    # Bind tools if provided
    if tools:
        llm_with_tools = llm.bind_tools(tools)
        response = llm_with_tools.invoke(prompt.invoke({"messages": messages}))
    else:
        response = llm.invoke(prompt.invoke({"messages": messages}))

    # Update state with LLM response
    new_messages = list(state.get("messages", []))
    new_messages.append(response)

    # Check if the response contains tool calls
    pending_tool_calls = []
    if hasattr(response, "tool_calls") and response.tool_calls:
        for tc in response.tool_calls:
            tool_name = tc.get("name", "")
            if tool_name:
                pending_tool_calls.append({
                    "name": tool_name,
                    "args": tc.get("args", {}),
                    "id": tc.get("id", str(uuid.uuid4()))
                })

    return {
        **state,
        "messages": new_messages,
        "pending_tool_calls": pending_tool_calls,
        "should_continue": "tools" if pending_tool_calls else " END",
        "output": response.content if hasattr(response, "content") else ""
    }


async def llm_node_async(
    state: AgentState,
    llm: BaseChatModel,
    tools: Optional[List[Any]] = None
) -> AgentState:
    """
    Async LLM node - calls the LLM asynchronously

    Args:
        state: Current agent state
        llm: LangChain ChatModel instance
        tools: Optional list of tools for binding

    Returns:
        Updated agent state
    """
    from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

    # Build prompt with system message and conversation history
    prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content=AGENT_SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="messages")
    ])

    # Get conversation messages
    messages = state.get("messages", [])

    # Bind tools if provided
    if tools:
        llm_with_tools = llm.bind_tools(tools)
        response = await llm_with_tools.ainvoke(prompt.invoke({"messages": messages}))
    else:
        response = await llm.ainvoke(prompt.invoke({"messages": messages}))

    # Update state with LLM response
    new_messages = list(state.get("messages", []))
    new_messages.append(response)

    # Check if the response contains tool calls
    pending_tool_calls = []
    if hasattr(response, "tool_calls") and response.tool_calls:
        for tc in response.tool_calls:
            tool_name = tc.get("name", "")
            if tool_name:
                pending_tool_calls.append({
                    "name": tool_name,
                    "args": tc.get("args", {}),
                    "id": tc.get("id", str(uuid.uuid4()))
                })

    return {
        **state,
        "messages": new_messages,
        "pending_tool_calls": pending_tool_calls,
        "should_continue": "tools" if pending_tool_calls else " END",
        "output": response.content if hasattr(response, "content") else ""
    }


class ToolExecutor:
    """
    Tool executor for running tools and handling results
    """

    def __init__(
        self,
        db_session=None,
        context=None,
        context_manager: Optional[ContextManager] = None
    ):
        self.db_session = db_session
        self.context = context
        self.context_manager = context_manager

    def execute_tool(
        self,
        tool_name: str,
        tool_args: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute a single tool and return the result

        Args:
            tool_name: Name of the tool to execute
            tool_args: Arguments to pass to the tool

        Returns:
            Tool execution result dict
        """
        from backend.agent.langgraph.tools import create_langchain_tools, validate_tool_name

        # Validate tool name
        if not validate_tool_name(tool_name):
            return {
                "success": False,
                "error": f"Invalid tool name: {tool_name}",
                "content": f"工具 '{tool_name}' 不存在"
            }

        # Create tools with current context
        tools = create_langchain_tools(
            db_session=self.db_session,
            context=self.context,
            context_manager=self.context_manager
        )

        # Find the matching tool
        tool = None
        for t in tools:
            if t.name == tool_name:
                tool = t
                break

        if not tool:
            return {
                "success": False,
                "error": f"Tool not found: {tool_name}",
                "content": f"工具 '{tool_name}' 未找到"
            }

        # Execute tool asynchronously
        import asyncio

        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        try:
            result = loop.run_until_complete(tool._arun(**tool_args))
            return {
                "success": True,
                "content": result,
                "tool_name": tool_name
            }
        except Exception as e:
            logger.error(f"Tool execution error: {tool_name} - {e}")
            return {
                "success": False,
                "error": str(e),
                "content": f"执行错误: {str(e)}"
            }

    def execute_tools(
        self,
        tool_calls: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Execute multiple tool calls

        Args:
            tool_calls: List of tool calls with 'name' and 'args'

        Returns:
            List of tool results
        """
        results = []
        for tc in tool_calls:
            tool_name = tc.get("name", "")
            tool_args = tc.get("args", {})
            result = self.execute_tool(tool_name, tool_args)
            results.append({
                "tool": tool_name,
                "args": tool_args,
                "id": tc.get("id"),
                "result": result
            })
        return results


def tool_node(state: AgentState) -> AgentState:
    """
    Tool execution node

    Args:
        state: Current agent state

    Returns:
        Updated agent state with tool results
    """
    pending_tool_calls = state.get("pending_tool_calls", [])
    if not pending_tool_calls:
        return {**state, "should_continue": " END"}

    # Create tool executor
    db_session = state.get("db_session")
    context = state.get("context")
    context_manager = state.get("context_manager")

    executor = ToolExecutor(
        db_session=db_session,
        context=context,
        context_manager=context_manager
    )

    # Execute tools
    tool_results = executor.execute_tools(pending_tool_calls)

    # Process results and check for confirmation requirements
    new_messages = list(state.get("messages", []))
    new_actions = list(state.get("actions", []))
    confirmation_required = None

    for tr in tool_results:
        result_data = tr.get("result", {})
        content = result_data.get("content", "")

        # Create tool message
        # tool_call_id 必须与 AIMessage.tool_calls 中的 id 匹配
        tool_call_id = tr.get("id") or str(uuid.uuid4())
        tool_msg = ToolMessage(
            content=content,
            tool_call_id=tool_call_id,
            name=tr.get("tool", "")
        )
        new_messages.append(tool_msg)

        # Track action
        new_actions.append({
            "skill": tr.get("tool", ""),
            "action": tr.get("tool", ""),
            "params": tr.get("args", {}),
            "risk_level": "MEDIUM"
        })

        # Check for confirmation requirement
        if isinstance(content, str) and content.startswith("{"):
            try:
                parsed = json.loads(content)
                if parsed.get("requires_confirmation"):
                    confirmation_id = str(uuid.uuid4())
                    confirmation_required = {
                        "confirmation_id": confirmation_id,
                        "skill": parsed.get("skill", ""),
                        "params": parsed.get("params", {}),
                        "risk_level": parsed.get("risk_level", "HIGH"),
                        "message": parsed.get("message", "此操作需要确认"),
                        "requires_confirmation": True
                    }
            except json.JSONDecodeError:
                pass

    return {
        **state,
        "messages": new_messages,
        "tool_results": tool_results,
        "actions": new_actions,
        "pending_tool_calls": [],
        "confirmation_required": confirmation_required,
        "should_continue": "confirm" if confirmation_required else "continue"
    }


def confirm_interrupt_node(state: AgentState) -> AgentState:
    """
    Confirmation interrupt node

    This node sets up the confirmation requirement and signals the graph
    to suspend for user confirmation.

    Args:
        state: Current agent state

    Returns:
        Updated agent state with confirmation info
    """
    confirmation = state.get("confirmation_required")
    if not confirmation:
        return {**state, "should_continue": "continue"}

    # The state already has confirmation_required set by tool_node
    # This node just validates and prepares for interrupt
    logger.info(f"Confirmation required: {confirmation.get('skill')}")

    return {
        **state,
        "should_continue": "confirm"
    }


def post_confirm_node(
    state: AgentState,
    confirmed: bool,
    reason: Optional[str] = None
) -> AgentState:
    """
    Post-confirmation node - handles user response after interrupt

    Args:
        state: Current agent state
        confirmed: Whether user confirmed the action
        reason: User's reason (if rejected)

    Returns:
        Updated agent state
    """
    if not confirmed:
        # User rejected the action
        new_messages = list(state.get("messages", []))
        rejection_msg = AIMessage(
            content=f"已取消操作。{reason or '用户拒绝执行此操作'}"
        )
        new_messages.append(rejection_msg)

        return {
            **state,
            "messages": new_messages,
            "confirmation_required": None,
            "pending_tool_calls": [],
            "should_continue": " END",
            "output": rejection_msg.content
        }

    # User confirmed - execute the pending tool call
    confirmation = state.get("confirmation_required", {})
    skill_name = confirmation.get("skill", "")
    params = confirmation.get("params", {})

    if not skill_name:
        return {
            **state,
            "error": "No pending action to execute",
            "should_continue": " END"
        }

    # Execute the confirmed tool
    db_session = state.get("db_session")
    context = state.get("context")
    context_manager = state.get("context_manager")

    executor = ToolExecutor(
        db_session=db_session,
        context=context,
        context_manager=context_manager
    )

    result = executor.execute_tool(skill_name, params)

    # Add tool result to messages
    new_messages = list(state.get("messages", []))

    tool_msg = ToolMessage(
        content=result.get("content", ""),
        tool_call_id=str(uuid.uuid4()),
        name=skill_name
    )
    new_messages.append(tool_msg)

    # Continue to get LLM response
    return {
        **state,
        "messages": new_messages,
        "confirmation_required": None,
        "should_continue": "continue"
    }


def error_node(state: AgentState, error: Exception) -> AgentState:
    """
    Error handling node

    Args:
        state: Current agent state
        error: The exception that occurred

    Returns:
        Updated agent state with error info
    """
    logger.error(f"Agent error: {error}")

    new_messages = list(state.get("messages", []))
    error_msg = AIMessage(
        content=f"处理出错: {str(error)}"
    )
    new_messages.append(error_msg)

    return {
        **state,
        "messages": new_messages,
        "error": str(error),
        "should_continue": " END",
        "output": error_msg.content
    }


def should_end(state: AgentState) -> bool:
    """
    Determine if the agent should end

    Args:
        state: Current agent state

    Returns:
        True if should end
    """
    return state.get("should_continue") == " END"
