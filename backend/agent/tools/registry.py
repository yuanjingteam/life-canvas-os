"""
Tool 注册中心

管理所有可用 Tool 的注册和查找。
"""

from typing import Dict, Optional, List
from .base import BaseTool


class ToolRegistry:
    """Tool 注册中心（单例模式）"""

    _instance: Optional["ToolRegistry"] = None
    _tools: Dict[str, BaseTool] = {}

    def __new__(cls) -> "ToolRegistry":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def register(self, tool: BaseTool) -> None:
        """
        注册 Tool

        Args:
            tool: Tool 实例
        """
        self._tools[tool.name] = tool

    def unregister(self, name: str) -> bool:
        """
        注销 Tool

        Args:
            name: Tool 名称

        Returns:
            bool: 是否成功注销
        """
        if name in self._tools:
            del self._tools[name]
            return True
        return False

    def get(self, name: str) -> Optional[BaseTool]:
        """
        获取 Tool

        Args:
            name: Tool 名称

        Returns:
            Optional[BaseTool]: Tool 实例，不存在返回 None
        """
        return self._tools.get(name)

    def get_all(self) -> Dict[str, BaseTool]:
        """获取所有 Tool"""
        return self._tools.copy()

    def get_names(self) -> List[str]:
        """获取所有 Tool 名称"""
        return list(self._tools.keys())

    def clear(self) -> None:
        """清空所有 Tool"""
        self._tools.clear()

    def __contains__(self, name: str) -> bool:
        return name in self._tools

    def __len__(self) -> int:
        return len(self._tools)
