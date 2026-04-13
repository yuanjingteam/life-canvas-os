"""
LangChain Tools 定义
将 Skills 转换为 LangChain Tools

设计原则：
- Skills 是业务能力的封装
- LangChain Tools 是 LangChain 可调用的工具
- 这里负责将 Skills 转换为 LangChain 可理解的格式
- 支持高风险操作的确认机制
- 支持枚举值约束，防止参数幻觉
"""
import json
from typing import Any, Dict, List, Literal, Optional, Type, Union, get_args
from pydantic import BaseModel, Field, create_model

from langchain_core.tools import BaseTool as LangChainBaseTool

from backend.agent.skills.registry import SkillRegistry
from backend.agent.skills.base import BaseSkill, RiskLevel
from backend.agent.utils.logger import get_logger

logger = get_logger("langchain_tools")


def create_pydantic_model_from_parameters(
    parameters: List[Any],
    model_name: str = "DynamicInput"
) -> Type[BaseModel]:
    """
    从 Skill 参数定义创建 Pydantic 模型

    Args:
        parameters: Skill 参数列表
        model_name: 模型名称

    Returns:
        Pydantic 模型类
    """
    type_map = {
        "string": str,
        "integer": int,
        "number": float,
        "boolean": bool,
        "array": list,
        "object": dict,
    }

    fields = {}
    for param in parameters:
        field_type = type_map.get(param.type, str)

        # 如果有枚举约束，使用 Literal 类型
        if param.enum and param.type == "string":
            # 创建 Literal 类型，例如 Literal["FUEL", "PHYSICAL", ...]
            enum_values = tuple(param.enum)
            field_type = Literal[enum_values]  # type: ignore

        if param.required:
            if param.default is not None:
                fields[param.name] = (field_type, Field(
                    default=param.default,
                    description=param.description,
                    json_schema_extra={"enum": param.enum} if param.enum else None
                ))
            else:
                fields[param.name] = (field_type, Field(
                    ...,
                    description=param.description,
                    json_schema_extra={"enum": param.enum} if param.enum else None
                ))
        else:
            default_val = param.default if param.default is not None else None
            # 可选参数，使用 Union 类型
            if param.enum and param.type == "string":
                enum_values = tuple(param.enum)
                field_type = Optional[Literal[enum_values]]  # type: ignore
            else:
                field_type = Optional[field_type]  # type: ignore
            fields[param.name] = (field_type, Field(
                default=default_val,
                description=param.description,
                json_schema_extra={"enum": param.enum} if param.enum else None
            ))

    if not fields:
        # 无参数时创建空模型
        return create_model(model_name)

    return create_model(model_name, **fields)


class SkillToToolWrapper(LangChainBaseTool):
    """
    将 Skill 转换为 LangChain Tool

    支持实际的 Skill 执行，包含数据库会话和上下文
    """

    name: str = Field(..., description="Tool name")
    description: str = Field(..., description="Tool description")
    skill_name: str = Field(..., description="Skill name to execute")
    db_session: Any = Field(None, description="Database session")
    context: Any = Field(None, description="Session context")
    context_manager: Any = Field(None, description="Context manager for persistence")
    args_schema: Type[BaseModel] = Field(None, description="Arguments schema")
    risk_level: str = Field("LOW", description="Risk level")

    def _run(self, *args, **kwargs) -> str:
        """同步执行（不支持）"""
        raise NotImplementedError("SkillToToolWrapper only supports async execution")

    async def _arun(self, **kwargs) -> str:
        """
        异步执行 Skill，支持确认机制

        Args:
            **kwargs: Skill 参数

        Returns:
            执行结果消息（JSON格式用于确认请求）
        """
        skill = SkillRegistry.get_skill(
            self.skill_name,
            db_session=self.db_session,
            context=self.context,
            context_manager=self.context_manager
        )

        if not skill:
            return json.dumps({"error": f"Skill '{self.skill_name}' not found"})

        # 验证参数
        error = skill.validate_parameters(kwargs)
        if error:
            return json.dumps({"error": error})

        try:
            # 检查是否需要确认（高风险操作）
            if skill.check_confirmation_required(**kwargs):
                return json.dumps({
                    "requires_confirmation": True,
                    "skill": self.skill_name,
                    "risk_level": skill.risk_level.value,
                    "message": f"此操作需要确认：{skill.description}",
                    "params": kwargs
                })

            result = await skill.execute(**kwargs)

            # 处理需要确认的结果
            if result.requires_confirmation:
                return json.dumps({
                    "requires_confirmation": True,
                    "skill": self.skill_name,
                    "risk_level": result.risk_level.value,
                    "message": result.confirmation_message or result.message,
                    "params": kwargs
                })

            # 正常返回消息
            return self._format_result(result)

        except Exception as e:
            logger.error(f"Skill execution failed: {self.skill_name} - {e}")
            return json.dumps({"error": str(e)})

    def _format_result(self, result) -> str:
        """
        格式化 SkillResult 返回给 LLM

        如果有数据，添加到返回消息中，让 LLM 能够看到实际的查询结果
        """
        # 如果有数据且是列表，格式化展示
        if result.data is not None:
            if isinstance(result.data, list):
                if len(result.data) == 0:
                    return result.message

                # 格式化列表数据，展示关键信息
                items = []
                for item in result.data[:5]:  # 最多展示5条
                    if isinstance(item, dict):
                        # 提取关键字段
                        created_at = item.get("created_at", "未知时间")
                        content = item.get("content", "")
                        mood = item.get("mood", "")
                        # 截取内容前100字符
                        content_preview = content[:100] + "..." if len(content) > 100 else content
                        item_str = f"[{created_at}] {content_preview}"
                        if mood:
                            item_str = f"[{created_at}][{mood}] {content_preview}"
                        items.append(item_str)
                    else:
                        items.append(str(item))

                if items:
                    separator = "\n"
                    return f"{result.message}\n\n{separator.join(items)}"

            # 非列表数据，直接返回
            return f"{result.message}\n\n{result.data}"

        return result.message


def create_langchain_tool_from_skill(
    skill_class: Type[BaseSkill],
    db_session=None,
    context=None,
    context_manager=None
) -> Optional[SkillToToolWrapper]:
    """
    将单个 Skill 转换为 LangChain Tool

    Args:
        skill_class: Skill 类
        db_session: 数据库会话
        context: 会话上下文
        context_manager: 上下文管理器

    Returns:
        LangChain Tool 实例
    """
    try:
        skill_instance = skill_class()
        skill_name = skill_instance.name
        skill_description = skill_instance.description
        parameters = skill_instance.parameters
        risk_level = skill_instance.risk_level.value

        # 创建参数 Schema
        args_schema = create_pydantic_model_from_parameters(
            parameters,
            model_name=f"{skill_name}_input"
        )

        tool = SkillToToolWrapper(
            name=skill_name,
            description=skill_description,
            skill_name=skill_name,
            db_session=db_session,
            context=context,
            context_manager=context_manager,
            args_schema=args_schema,
            risk_level=risk_level
        )

        return tool

    except Exception as e:
        logger.error(f"Failed to create tool for skill {skill_class.__name__}: {e}")
        return None


def create_langchain_tools(
    db_session=None,
    context=None,
    context_manager=None
) -> List[SkillToToolWrapper]:
    """
    从所有注册的 Skills 创建 LangChain Tools

    Args:
        db_session: 数据库会话
        context: 会话上下文
        context_manager: 上下文管理器

    Returns:
        LangChain Tool 列表
    """
    tools = []

    for skill_name, skill_class in SkillRegistry._skills.items():
        tool = create_langchain_tool_from_skill(
            skill_class,
            db_session=db_session,
            context=context,
            context_manager=context_manager
        )
        if tool:
            tools.append(tool)

    logger.info(f"Created {len(tools)} LangChain tools from skills")
    return tools


def get_tool_schemas() -> List[Dict[str, Any]]:
    """
    获取所有工具的 Schema（用于 API 返回）

    Returns:
        工具 Schema 列表
    """
    schemas = []

    for skill_name, skill_class in SkillRegistry._skills.items():
        skill_instance = skill_class()
        schemas.append(skill_instance.get_schema())

    return schemas


def get_available_tool_names() -> List[str]:
    """
    获取所有可用工具的名称列表

    Returns:
        工具名称列表
    """
    return list(SkillRegistry._skills.keys())


def validate_tool_name(tool_name: str) -> bool:
    """
    验证工具名称是否有效

    Args:
        tool_name: 工具名称

    Returns:
        是否是有效的工具名称
    """
    return tool_name in SkillRegistry._skills