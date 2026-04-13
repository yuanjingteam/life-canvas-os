"""
LLM 客户端模块

提供统一的 LLM 调用接口，支持多家提供商和自动故障转移。
"""

from .base import (
    LLMClient,
    LLMMessage,
    LLMToolDefinition,
    LLMResponse,
    LLMProviderType,
    LLMError,
    RateLimitError,
    TimeoutError,
    AuthenticationError,
    ServerError,
)
from .factory import LLMClientFactory
from .client_with_fallback import LLMClientWithFallback
from .deepseek import DeepSeekClient
from .doubao import DoubaoClient

# 注册提供商
LLMClientFactory.register_provider(LLMProviderType.DEEPSEEK, DeepSeekClient)
LLMClientFactory.register_provider(LLMProviderType.DOUBAO, DoubaoClient)

__all__ = [
    "LLMClient",
    "LLMMessage",
    "LLMToolDefinition",
    "LLMResponse",
    "LLMProviderType",
    "LLMError",
    "RateLimitError",
    "TimeoutError",
    "AuthenticationError",
    "ServerError",
    "LLMClientFactory",
    "LLMClientWithFallback",
    "DeepSeekClient",
    "DoubaoClient",
]
