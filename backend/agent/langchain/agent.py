"""
LangChain Agent 执行器
基于 LangGraph 的 Agent 实现

这是 Agent 的主要执行引擎，使用 LangGraph（LangChain 推荐的新 Agent 框架）。
支持高风险操作的确认机制。
"""
import json
from typing import Any, Dict, List, Optional, AsyncIterator
from datetime import datetime
import asyncio
import uuid

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage, ToolMessage
from langchain_core.language_models import BaseChatModel
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent

from backend.agent.langchain.tools import create_langchain_tools, validate_tool_name, get_available_tool_names
from backend.agent.skills.registry import SkillRegistry
from backend.agent.skills.base import RiskLevel
from backend.agent.core.context import ContextManager, get_context_manager_with_db
from backend.agent.models.response import AgentResponse, ActionInfo, ConfirmationRequired
from backend.agent.utils.logger import get_logger

logger = get_logger("langchain_agent")

# LangChain Agent System Prompt
LANGCHAIN_SYSTEM_PROMPT = """你是 Life Canvas OS 的 AI 助手，一个帮助用户管理个人生活的智能助手。

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
    创建 LangChain 兼容的 LLM

    Args:
        provider: 提供商名称 (deepseek, doubao)
        api_key: API 密钥
        model: 模型名称
        temperature: 温度参数

    Returns:
        LangChain ChatModel 实例
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
    将消息历史转换为 LangChain 消息格式

    Args:
        messages: 消息列表 [{"role": "user/assistant", "content": "..."}]

    Returns:
        LangChain 消息列表
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


class AgentExecutor:
    """
    基于 LangGraph 的 Agent 执行器

    这是 Agent 的主要执行引擎，使用 LangChain create_agent。
    支持会话管理、工具调用和风险操作确认。
    """

    def __init__(
        self,
        db_session=None,
        context_manager: Optional[ContextManager] = None
    ):
        """
        初始化 Agent 执行器

        Args:
            db_session: 数据库会话
            context_manager: 上下文管理器
        """
        self.db_session = db_session
        self.context_manager = context_manager or get_context_manager_with_db(db_session)

    async def chat(
        self,
        message: str,
        session_id: Optional[str] = None,
        user_config: Optional[Dict[str, Any]] = None,
        user_id: Optional[int] = None
    ) -> AgentResponse:
        """
        处理用户消息

        Args:
            message: 用户消息
            session_id: 会话ID
            user_config: 用户配置（包含 AI 配置）
            user_id: 用户ID

        Returns:
            Agent 响应
        """
        # 获取或创建会话
        context = self.context_manager.get_or_create_session(session_id, user_id=user_id)
        session_id = context.session_id

        try:
            # 创建 LLM
            llm = self._create_llm(user_config)

            # 创建工具 - 传递 context_manager
            tools = create_langchain_tools(
                db_session=self.db_session,
                context=context,
                context_manager=self.context_manager
            )

            # 创建 ReAct Agent
            # create_agent 参数: model, tools, system_prompt
            agent = create_agent(
                model=llm,
                tools=tools,
                system_prompt=LANGCHAIN_SYSTEM_PROMPT
            )

            # 获取对话历史
            history = context.get_conversation_history()
            chat_history = build_chat_history(history)

            # 执行 Agent
            result = await agent.ainvoke({
                "messages": chat_history + [HumanMessage(content=message)]
            })

            # 提取响应和 actions
            output = ""
            actions = []
            confirmation_required = None

            if result and "messages" in result:
                # 遍历所有消息，收集工具调用信息
                for msg in result["messages"]:
                    # 处理 ToolMessage（工具执行结果） - 关键修复！
                    if isinstance(msg, ToolMessage):
                        tool_content = msg.content
                        logger.info(f"ToolMessage received, content type: {type(tool_content)}, content preview: {str(tool_content)[:200]}")

                        # 检查是否是确认请求（JSON格式的响应）
                        if isinstance(tool_content, str) and tool_content.startswith("{"):
                            try:
                                parsed = json.loads(tool_content)
                                logger.info(f"ToolMessage parsed JSON: requires_confirmation={parsed.get('requires_confirmation')}, skill={parsed.get('skill')}")

                                # 处理错误响应
                                if parsed.get("error"):
                                    logger.warning(f"Tool execution error: {parsed.get('error')}")
                                    continue

                                # 处理确认请求
                                if parsed.get("requires_confirmation"):
                                    confirmation_required = ConfirmationRequired(
                                        confirmation_id=str(uuid.uuid4()),
                                        action=ActionInfo(
                                            skill=parsed.get("skill", ""),
                                            action=parsed.get("skill", ""),
                                            params=parsed.get("params", {}),
                                            risk_level=parsed.get("risk_level", "HIGH")
                                        ),
                                        message=parsed.get("message", "此操作需要确认"),
                                        risk_level=parsed.get("risk_level", "HIGH")
                                    )
                                    # 保存待确认信息到上下文
                                    context.set_entity_reference(
                                        "pending_confirmation",
                                        {
                                            "confirmation_id": confirmation_required.confirmation_id,
                                            "skill": parsed.get("skill"),
                                            "params": parsed.get("params", {})
                                        }
                                    )
                                    logger.info(f"Created confirmation_required from ToolMessage: {confirmation_required.confirmation_id}")
                            except json.JSONDecodeError as e:
                                logger.warning(f"ToolMessage JSON parse error: {e}")

                    # 处理 AIMessage（收集工具调用信息用于 actions 列表）
                    if isinstance(msg, AIMessage):
                        # 收集所有工具调用
                        if hasattr(msg, 'tool_calls') and msg.tool_calls:
                            for tc in msg.tool_calls:
                                tool_name = tc.get("name", "")

                                # 验证工具名称是否有效（防止幻觉）
                                if tool_name and not validate_tool_name(tool_name):
                                    logger.warning(f"Invalid tool name detected: {tool_name}")
                                    # 跳过无效的工具调用
                                    continue

                                # 注意：tc 中不包含执行结果，结果在 ToolMessage 中
                                action = {
                                    "skill": tool_name,
                                    "action": tool_name,
                                    "params": tc.get("args", {}),
                                    "risk_level": "MEDIUM"
                                }
                                # 避免重复
                                if action not in actions:
                                    actions.append(action)

                # 获取最后的 AI 响应内容
                for msg in reversed(result["messages"]):
                    if isinstance(msg, AIMessage) and msg.content:
                        output = msg.content
                        break

            if not output:
                output = "抱歉，我无法处理您的请求。"

            # 保存消息（带 actions）
            self.context_manager.add_message(session_id, "user", message)
            self.context_manager.add_message(session_id, "assistant", output, actions)

            # 显式持久化 context（确保 referenced_entities 被保存）
            self.context_manager.update_session(context)

            return AgentResponse(
                session_id=session_id,
                message=output,
                actions=[
                    ActionInfo(
                        skill=a["skill"],
                        action=a["action"],
                        params=a["params"],
                        risk_level=a["risk_level"]
                    )
                    for a in actions
                ],
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
        流式处理用户消息

        Args:
            message: 用户消息
            session_id: 会话ID
            user_config: 用户配置
            user_id: 用户ID

        Yields:
            流式事件
        """
        # 获取或创建会话
        context = self.context_manager.get_or_create_session(session_id, user_id=user_id)
        session_id = context.session_id

        # 发送开始事件
        yield {
            "type": "stream_start",
            "session_id": session_id
        }

        try:
            # 执行并获取结果
            response = await self.chat(message, session_id, user_config)
            print(f"[DEBUG] chat() returned, response.error={response.error}", flush=True)

            # 模拟流式输出
            full_message = response.message
            print(f"[DEBUG] full_message length: {len(full_message)}", flush=True)
            chunk_size = 5

            for i in range(0, len(full_message), chunk_size):
                chunk = full_message[i:i + chunk_size]
                yield {
                    "type": "stream_chunk",
                    "session_id": session_id,
                    "content": chunk
                }
                await asyncio.sleep(0.05)

            print(f"[DEBUG] About to build stream_end", flush=True)

            # 发送结束事件 - 直接手动构建结果，避免序列化问题
            def convert_params(params: Any) -> Any:
                """递归转换 params 为可序列化的 Python 对象"""
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

            try:
                result_data = {
                    "session_id": response.session_id,
                    "message": response.message,
                    "actions": [
                        {
                            "skill": a.skill,
                            "action": a.action,
                            "params": convert_params(a.params),
                            "risk_level": a.risk_level
                        }
                        for a in (response.actions or [])
                    ],
                    "error": response.error,
                    "timestamp": response.timestamp.isoformat() if response.timestamp else None
                }
                # 如果有 confirmation_required，也需要手动处理
                if response.confirmation_required:
                    logger.info(f"Sending confirmation_required in stream_end: {response.confirmation_required.confirmation_id}, action={response.confirmation_required.action.skill}")
                    result_data["confirmation_required"] = {
                        "confirmation_id": response.confirmation_required.confirmation_id,
                        "message": response.confirmation_required.message,
                        "risk_level": response.confirmation_required.risk_level,
                        "requires_code": response.confirmation_required.requires_code,
                        "action": {
                            "skill": response.confirmation_required.action.skill,
                            "action": response.confirmation_required.action.action,
                            "params": convert_params(response.confirmation_required.action.params),
                            "risk_level": response.confirmation_required.action.risk_level
                        }
                    }
                else:
                    logger.info(f"stream_end: no confirmation_required in this response")
                print(f"[DEBUG] About to yield stream_end", flush=True)
                yield {
                    "type": "stream_end",
                    "session_id": session_id,
                    "result": result_data
                }
            except Exception as e:
                import traceback
                traceback.print_exc()
                print(f"[DEBUG] Error building stream_end: {e}", flush=True)
                yield {
                    "type": "stream_end",
                    "session_id": session_id,
                    "error": str(e)
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
        确认操作

        Args:
            session_id: 会话ID
            confirmation_id: 确认ID
            confirmed: 是否确认
            user_reason: 用户拒绝原因

        Returns:
            Agent 响应
        """
        # 从上下文获取待确认的操作
        context = self.context_manager.get_session(session_id)
        if not context:
            return AgentResponse(
                session_id=session_id,
                message="会话已过期，请重新开始",
                error="会话不存在"
            )

        pending = context.referenced_entities.get("pending_confirmation")
        if not pending or pending.get("confirmation_id") != confirmation_id:
            return AgentResponse(
                session_id=session_id,
                message="确认信息无效或已过期",
                error="无效的确认ID"
            )

        if confirmed:
            # 执行技能
            skill_name = pending["skill"]
            params = pending["params"]
            return await self._execute_skill_direct(session_id, skill_name, params)
        else:
            # 用户拒绝
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
        """直接执行技能"""
        context = self.context_manager.get_session(session_id)

        result = await SkillRegistry.execute_skill(
            skill_name,
            params,
            self.db_session,
            context,
            self.context_manager
        )

        # 记录操作
        self.context_manager.add_operation(
            session_id, skill_name, skill_name, params, result.data
        )

        # 记录助手消息
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

    def _create_llm(self, user_config: Optional[Dict[str, Any]]) -> BaseChatModel:
        """
        创建 LangChain LLM

        Args:
            user_config: 用户配置

        Returns:
            LangChain ChatModel
        """
        if not user_config:
            raise ValueError("未配置 AI 服务")

        provider = user_config.get("provider")
        api_key = user_config.get("api_key")
        model = user_config.get("model")

        # 解密 API Key
        from backend.services.user_service import UserService
        try:
            decrypted_key = UserService.decrypt_api_key(api_key)
            api_key = decrypted_key
        except Exception:
            pass

        return create_langchain_llm(
            provider=provider,
            api_key=api_key,
            model=model
        )
