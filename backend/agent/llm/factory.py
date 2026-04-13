"""
LLM 客户端工厂

根据配置创建对应的 LLM 客户端实例。
"""

from typing import Optional, Dict, Any
from .base import LLMClient, LLMProviderType


class LLMClientFactory:
    """LLM 客户端工厂"""

    _providers: Dict[LLMProviderType, type] = {}

    @classmethod
    def register_provider(cls, provider_type: LLMProviderType, client_class: type):
        """
        注册提供商客户端

        Args:
            provider_type: 提供商类型
            client_class: 客户端类
        """
        cls._providers[provider_type] = client_class

    @classmethod
    def create(
        cls,
        provider_type: LLMProviderType,
        config: Dict[str, Any],
    ) -> Optional[LLMClient]:
        """
        创建 LLM 客户端

        Args:
            provider_type: 提供商类型
            config: 配置字典（包含 api_key, base_url, model 等）

        Returns:
            Optional[LLMClient]: LLM 客户端实例
        """
        client_class = cls._providers.get(provider_type)
        if client_class is None:
            return None

        try:
            return client_class(**config)
        except Exception as e:
            print(f"创建 LLM 客户端失败：{e}")
            return None

    @classmethod
    def get_available_providers(cls) -> list:
        """获取可用的提供商列表"""
        return list(cls._providers.keys())
