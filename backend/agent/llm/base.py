"""
LLM 客户端基础接口

定义统一的 LLM 调用接口，支持多家提供商。
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, AsyncIterator
from enum import Enum


class LLMProviderType(Enum):
    """LLM 提供商类型"""

    DEEPSEEK = "deepseek"
    DOUBAO = "doubao"
    OPENAI = "openai"


@dataclass
class LLMMessage:
    """LLM 消息"""

    role: str  # system, user, assistant
    content: str


@dataclass
class LLMToolDefinition:
    """LLM Tool 定义（用于 Function Calling）"""

    name: str
    description: str
    parameters: Dict[str, Any]


@dataclass
class LLMResponse:
    """LLM 响应"""

    content: str
    tool_calls: List[Dict[str, Any]] = field(default_factory=list)
    usage: Dict[str, int] = field(default_factory=dict)
    model: str = ""
    finish_reason: str = ""

    @property
    def has_tool_calls(self) -> bool:
        """是否有工具调用"""
        return len(self.tool_calls) > 0


class LLMError(Exception):
    """LLM 错误基类"""

    pass


class RateLimitError(LLMError):
    """速率限制错误"""

    pass


class TimeoutError(LLMError):
    """超时错误"""

    pass


class AuthenticationError(LLMError):
    """认证错误"""

    pass


class ServerError(LLMError):
    """服务端错误"""

    pass


class LLMClient(ABC):
    """LLM 客户端抽象基类"""

    provider_type: LLMProviderType = LLMProviderType.DEEPSEEK

    def __init__(
        self,
        api_key: str,
        base_url: str,
        model: str,
        timeout: int = 30,
    ):
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.timeout = timeout

    @abstractmethod
    async def chat(
        self,
        messages: List[LLMMessage],
        tools: Optional[List[LLMToolDefinition]] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> LLMResponse:
        """
        发送聊天请求

        Args:
            messages: 消息列表
            tools: Tool 定义列表（用于 Function Calling）
            temperature: 温度参数
            max_tokens: 最大 token 数

        Returns:
            LLMResponse: LLM 响应
        """
        pass

    @abstractmethod
    async def stream_chat(
        self,
        messages: List[LLMMessage],
        tools: Optional[List[LLMToolDefinition]] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> AsyncIterator[str]:
        """
        流式聊天

        Args:
            messages: 消息列表
            tools: Tool 定义列表
            temperature: 温度参数
            max_tokens: 最大 token 数

        Yields:
            str: 响应文本片段
        """
        pass

    @abstractmethod
    def get_token_count(self, text: str) -> int:
        """
        计算文本的 token 数

        Args:
            text: 文本

        Returns:
            int: token 数
        """
        pass

    @abstractmethod
    def supports_function_calling(self) -> bool:
        """
        是否支持 Function Calling

        Returns:
            bool: 是否支持
        """
        pass

    def _build_headers(self) -> Dict[str, str]:
        """构建请求头"""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
