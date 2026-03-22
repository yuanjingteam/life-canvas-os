"""
Tool 基础类
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List
from pydantic import BaseModel, Field
from enum import Enum


class ToolResult(BaseModel):
    """工具执行结果"""

    success: bool = Field(..., description="是否成功")
    data: Any = Field(None, description="返回数据")
    error: Optional[str] = Field(None, description="错误信息")

    model_config = {"protected_namespaces": ()}


class ToolParameter(BaseModel):
    """工具参数定义"""

    name: str = Field(..., description="参数名")
    type: str = Field(..., description="参数类型")
    description: str = Field(..., description="参数描述")
    required: bool = Field(True, description="是否必需")
    enum: Optional[List[str]] = Field(None, description="枚举值")

    model_config = {"protected_namespaces": ()}


class BaseTool(ABC):
    """工具基类"""

    def __init__(self, db_session=None):
        """
        初始化工具

        Args:
            db_session: 数据库会话（可选）
        """
        self.db_session = db_session

    @property
    @abstractmethod
    def name(self) -> str:
        """工具名称"""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """工具描述"""
        pass

    @property
    @abstractmethod
    def parameters(self) -> List[ToolParameter]:
        """参数定义"""
        pass

    @abstractmethod
    async def execute(self, **kwargs) -> ToolResult:
        """
        执行工具

        Args:
            **kwargs: 工具参数

        Returns:
            执行结果
        """
        pass

    def get_schema(self) -> Dict[str, Any]:
        """获取工具的 JSON Schema"""
        properties = {}
        required = []

        for param in self.parameters:
            prop = {
                "type": param.type,
                "description": param.description
            }
            if param.enum:
                prop["enum"] = param.enum
            properties[param.name] = prop

            if param.required:
                required.append(param.name)

        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required
            }
        }

    def validate_parameters(self, params: Dict[str, Any]) -> Optional[str]:
        """
        验证参数

        Args:
            params: 参数字典

        Returns:
            错误信息，None 表示验证通过
        """
        param_names = {p.name for p in self.parameters}
        required_params = {p.name for p in self.parameters if p.required}

        # 检查必需参数
        missing = required_params - set(params.keys())
        if missing:
            return f"缺少必需参数: {', '.join(missing)}"

        # 检查未知参数
        unknown = set(params.keys()) - param_names
        if unknown:
            return f"未知参数: {', '.join(unknown)}"

        # 检查枚举值
        param_enums = {p.name: p.enum for p in self.parameters if p.enum}
        for name, enum_values in param_enums.items():
            if name in params and params[name] not in enum_values:
                return f"参数 {name} 的值必须是: {', '.join(enum_values)}"

        return None