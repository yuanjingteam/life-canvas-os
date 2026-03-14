"""
Skill 基类定义

Skill 是面向用户的、领域特定的、可组合的能力单元。
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Optional, Dict, List
from enum import Enum
import time


class RiskLevel(Enum):
    """风险等级"""

    LOW = "LOW"  # 只读查询，不需要确认
    MEDIUM = "MEDIUM"  # 创建、更新，可选确认
    HIGH = "HIGH"  # 删除、批量操作，必须确认
    CRITICAL = "CRITICAL"  # 数据导出、系统重置，必须确认 + 二次验证


@dataclass
class SkillParameter:
    """Skill 参数定义"""

    name: str
    type: str  # string, integer, number, boolean, array, object
    description: str
    required: bool = False
    enum: Optional[List[Any]] = None  # 枚举值
    default: Any = None


@dataclass
class SkillResult:
    """Skill 执行结果"""

    success: bool
    response: str  # 给用户的回复
    data: Any = None
    requires_confirmation: bool = False
    confirmation_id: Optional[str] = None
    confirmation_message: Optional[str] = None
    error: Optional[str] = None
    execution_time: float = field(default=0.0)

    @classmethod
    def ok(
        cls,
        response: str,
        data: Any = None,
        requires_confirmation: bool = False,
        confirmation_id: str = None,
        confirmation_message: str = None,
        execution_time: float = 0.0,
    ) -> "SkillResult":
        """创建成功结果"""
        return cls(
            success=True,
            response=response,
            data=data,
            requires_confirmation=requires_confirmation,
            confirmation_id=confirmation_id,
            confirmation_message=confirmation_message,
            execution_time=execution_time,
        )

    @classmethod
    def fail(cls, error: str, response: str = "") -> "SkillResult":
        """创建失败结果"""
        return cls(success=False, response=response, error=error)


class BaseSkill(ABC):
    """Skill 基类"""

    # Skill 唯一标识
    name: str = ""

    # Skill 描述，面向 LLM
    description: str = ""

    # 触发词列表（用于规则匹配降级）
    trigger_words: List[str] = []

    # 参数定义
    parameters: List[SkillParameter] = []

    # 风险等级
    risk_level: RiskLevel = RiskLevel.LOW

    # 是否需要确认
    requires_confirmation: bool = False

    def __init__(self):
        if not self.name:
            raise ValueError("Skill 必须定义 name")
        if not self.description:
            raise ValueError("Skill 必须定义 description")

    @abstractmethod
    async def execute(self, **kwargs) -> SkillResult:
        """
        执行 Skill

        Args:
            **kwargs: 参数

        Returns:
            SkillResult: 执行结果
        """
        pass

    async def __call__(self, **kwargs) -> SkillResult:
        """允许像函数一样调用 Skill"""
        start_time = time.time()
        try:
            # 参数验证
            is_valid, error_msg = self.validate_params(**kwargs)
            if not is_valid:
                return SkillResult.fail(error_msg)

            # 执行
            result = await self.execute(**kwargs)
            result.execution_time = time.time() - start_time
            return result
        except Exception as e:
            return SkillResult.fail(f"Skill 执行失败：{str(e)}")

    def validate_params(self, **kwargs) -> tuple[bool, Optional[str]]:
        """
        验证参数

        Args:
            **kwargs: 待验证的参数

        Returns:
            (是否有效，错误信息)
        """
        for param in self.parameters:
            # 检查必填参数
            if param.required and param.name not in kwargs:
                return False, f"缺少必填参数：{param.name}"

            # 检查类型
            if param.name in kwargs:
                value = kwargs[param.name]
                if not self._check_type(value, param.type):
                    return False, f"参数 {param.name} 类型错误，期望 {param.type}"

                # 检查枚举值
                if param.enum and value not in param.enum:
                    return False, f"参数 {param.name} 值不在允许范围内：{param.enum}"

        return True, None

    def _check_type(self, value: Any, type_name: str) -> bool:
        """检查值类型"""
        type_map = {
            "string": str,
            "integer": int,
            "number": (int, float),
            "boolean": bool,
            "array": list,
            "object": dict,
        }
        expected_type = type_map.get(type_name)
        if expected_type is None:
            return True
        return isinstance(value, expected_type)

    def get_tool_definitions(self) -> List[Dict]:
        """
        获取 Tool 定义（用于 LLM Function Calling）

        Returns:
            Tool 定义列表
        """

        def param_to_schema(param: SkillParameter) -> Dict:
            schema = {
                "type": param.type,
                "description": param.description,
            }
            if param.enum:
                schema["enum"] = param.enum
            return schema

        properties = {
            param.name: param_to_schema(param) for param in self.parameters
        }
        required = [param.name for param in self.parameters if param.required]

        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required,
                },
            },
        }
