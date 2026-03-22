"""
LLM 客户端基础接口
"""
from abc import ABC, abstractmethod
from typing import AsyncIterator, Dict, Any, List, Optional, Union
from pydantic import BaseModel
from enum import Enum


class MessageRole(str, Enum):
    """消息角色"""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class LLMMessage(BaseModel):
    """LLM 消息格式"""

    role: str
    content: str

    model_config = {"protected_namespaces": ()}


class LLMResponse(BaseModel):
    """LLM 响应格式"""

    content: str
    finish_reason: str = "stop"
    # 使用 Any 类型以支持不同 API 返回的 usage 结构
    # DeepSeek 返回 prompt_tokens_details: {'cached_tokens': 0}
    usage: Optional[Dict[str, Any]] = None

    model_config = {"protected_namespaces": ()}


class BaseLLMClient(ABC):
    """LLM 客户端基础接口"""

    def __init__(
        self,
        api_key: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        timeout: float = 60.0
    ):
        """
        初始化 LLM 客户端

        Args:
            api_key: API 密钥
            model: 模型名称
            temperature: 温度参数
            max_tokens: 最大 token 数
            timeout: 请求超时时间
        """
        self.api_key = api_key
        self.model = model or self.default_model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """提供商名称"""
        pass

    @property
    @abstractmethod
    def default_model(self) -> str:
        """默认模型"""
        pass

    @property
    @abstractmethod
    def api_base_url(self) -> str:
        """API 基础 URL"""
        pass

    @abstractmethod
    async def chat(
        self,
        messages: List[LLMMessage],
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> LLMResponse:
        """
        发送聊天请求

        Args:
            messages: 消息列表
            system_prompt: 系统提示
            **kwargs: 其他参数

        Returns:
            LLM 响应
        """
        pass

    @abstractmethod
    async def stream_chat(
        self,
        messages: List[LLMMessage],
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> AsyncIterator[str]:
        """
        流式聊天

        Args:
            messages: 消息列表
            system_prompt: 系统提示
            **kwargs: 其他参数

        Yields:
            内容块
        """
        pass

    def build_messages(
        self,
        messages: List[LLMMessage],
        system_prompt: Optional[str] = None
    ) -> List[Dict[str, str]]:
        """构建请求消息列表"""
        result = []
        if system_prompt:
            result.append({"role": "system", "content": system_prompt})
        result.extend([{"role": m.role, "content": m.content} for m in messages])
        return result

    def to_langchain(self) -> "BaseChatModel":
        """
        转换为 LangChain ChatModel

        Returns:
            LangChain ChatModel 实例
        """
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(
            model=self.model,
            api_key=self.api_key,
            base_url=self.api_base_url.rsplit("/", 1)[0],  # 去掉 /chat/completions 后缀
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            timeout=self.timeout
        )