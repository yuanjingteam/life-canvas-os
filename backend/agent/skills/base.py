"""
Skill 基础类
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from enum import Enum
from pydantic import BaseModel, Field

from backend.agent.tools.base import ToolResult
from backend.agent.tools.database import DatabaseTool
from backend.agent.tools.datetime import DateTimeTool
from backend.agent.tools.context import ContextTool


class RiskLevel(str, Enum):
    """风险等级"""

    LOW = "LOW"  # 低风险：只读操作
    MEDIUM = "MEDIUM"  # 中风险：创建、更新操作
    HIGH = "HIGH"  # 高风险：删除操作
    CRITICAL = "CRITICAL"  # 极高风险：批量删除、系统重置


class SkillParameter(BaseModel):
    """技能参数定义"""

    name: str = Field(..., description="参数名")
    type: str = Field(..., description="参数类型")
    description: str = Field(..., description="参数描述")
    required: bool = Field(True, description="是否必需")
    default: Any = Field(None, description="默认值")
    enum: Optional[List[str]] = Field(None, description="枚举值列表（用于约束可选值）")

    model_config = {"protected_namespaces": ()}


class SkillResult(BaseModel):
    """技能执行结果"""

    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="结果消息")
    data: Any = Field(None, description="返回数据")
    risk_level: RiskLevel = Field(RiskLevel.LOW, description="风险等级")
    requires_confirmation: bool = Field(False, description="是否需要确认")
    confirmation_message: Optional[str] = Field(None, description="确认提示消息")

    model_config = {"protected_namespaces": ()}


class BaseSkill(ABC):
    """
    技能基类

    Skills 使用 Tools 完成具体操作，专注于业务逻辑：
    - 验证业务规则
    - 编排多个 Tools
    - 格式化输出

    可用的 Tools:
    - self.db: DatabaseTool - 数据库 CRUD 操作
    - self.datetime: DateTimeTool - 日期解析
    - self.ctx: ContextTool - 上下文存取

    注意：对于复杂的业务逻辑（如AI洞察生成、评分联动更新），
    Skills 可以直接调用 Service 层，不需要通过 Tool 层。
    """

    def __init__(self, db_session=None, context=None, context_manager=None):
        """
        初始化技能

        Args:
            db_session: 数据库会话
            context: 会话上下文
            context_manager: 上下文管理器（用于持久化）
        """
        self.db_session = db_session
        self.context = context
        self.context_manager = context_manager

        # 初始化工具
        self.db: Optional[DatabaseTool] = DatabaseTool(db_session) if db_session else None
        self.datetime: DateTimeTool = DateTimeTool()
        # 传递 context_manager 给 ContextTool
        self.ctx: Optional[ContextTool] = ContextTool(context, context_manager) if context else None

    @property
    @abstractmethod
    def name(self) -> str:
        """技能名称"""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """技能描述"""
        pass

    @property
    @abstractmethod
    def risk_level(self) -> RiskLevel:
        """风险等级"""
        pass

    @property
    @abstractmethod
    def parameters(self) -> List[SkillParameter]:
        """参数定义"""
        pass

    @property
    def keywords(self) -> List[str]:
        """触发关键词"""
        return []

    @property
    def examples(self) -> List[str]:
        """使用示例"""
        return []

    @abstractmethod
    async def execute(self, **kwargs) -> SkillResult:
        """
        执行技能

        Args:
            **kwargs: 技能参数

        Returns:
            执行结果
        """
        pass

    def get_schema(self) -> Dict[str, Any]:
        """获取技能的 JSON Schema"""
        properties = {}
        required = []

        for param in self.parameters:
            prop = {
                "type": param.type,
                "description": param.description
            }

            # 添加枚举约束
            if param.enum:
                prop["enum"] = param.enum

            if param.default is not None:
                prop["default"] = param.default

            properties[param.name] = prop

            if param.required:
                required.append(param.name)

        return {
            "name": self.name,
            "description": self.description,
            "risk_level": self.risk_level.value,
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required
            },
            "keywords": self.keywords,
            "examples": self.examples
        }

    def validate_parameters(self, params: Dict[str, Any]) -> Optional[str]:
        """
        验证参数

        Args:
            params: 参数字典

        Returns:
            错误信息，None 表示验证通过
        """
        param_defs = {p.name: p for p in self.parameters}
        required_params = {p.name for p in self.parameters if p.required}

        # 检查必需参数
        missing = required_params - set(params.keys())
        if missing:
            return f"缺少必需参数: {', '.join(missing)}"

        # 检查枚举值约束
        for key, value in params.items():
            param_def = param_defs.get(key)
            if param_def and param_def.enum and value not in param_def.enum:
                return f"参数 '{key}' 的值 '{value}' 无效，可选值: {', '.join(param_def.enum)}"

        return None

    def check_confirmation_required(self, **kwargs) -> bool:
        """
        检查是否需要确认

        Args:
            **kwargs: 技能参数

        Returns:
            是否需要确认
        """
        return self.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]

    def get_context_entity_id(
        self, key: str, explicit_id: Any = None
    ) -> Any:
        """
        获取上下文实体ID（优先使用显式传入的值）

        这是一个便捷方法，避免在多个Skill中重复相同的代码。
        例如：journal_id = self.get_context_entity_id("last_journal_id", kwargs.get("journal_id"))

        Args:
            key: 上下文键名（如 last_journal_id, last_deviation_id）
            explicit_id: 显式传入的ID值

        Returns:
            实体ID，如果都不存在则返回 None
        """
        if explicit_id:
            return explicit_id
        if self.ctx:
            return self.ctx.get_sync(key)
        return None