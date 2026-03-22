"""
LLM 客户端工厂
"""
from typing import Optional, Dict, Any, Union

from backend.agent.llm.base import BaseLLMClient
from backend.agent.llm.deepseek import DeepSeekClient
from backend.agent.llm.doubao import DoubaoClient
from backend.agent.utils.logger import get_logger

logger = get_logger("factory")

# 支持的提供商及其默认模型
SUPPORTED_PROVIDERS = {
    "deepseek": {
        "client_class": DeepSeekClient,
        "default_model": "deepseek-chat",
        "base_url": "https://api.deepseek.com/v1"
    },
    "doubao": {
        "client_class": DoubaoClient,
        "default_model": "doubao-seed-2-0-lite-260215",
        "base_url": "https://ark.cn-beijing.volces.com/api/v3"
    }
}


class LLMClientFactory:
    """LLM 客户端工厂"""

    @staticmethod
    def create(
        provider: str,
        api_key: str,
        model: Optional[str] = None,
        **kwargs
    ) -> BaseLLMClient:
        """
        创建 LLM 客户端

        Args:
            provider: 提供商名称 (deepseek, doubao)
            api_key: API 密钥
            model: 模型名称
            **kwargs: 其他配置参数

        Returns:
            LLM 客户端实例

        Raises:
            ValueError: 不支持的提供商
        """
        provider_lower = provider.lower()

        if provider_lower not in SUPPORTED_PROVIDERS:
            raise ValueError(
                f"不支持的 AI 提供商: {provider}，"
                f"仅支持: {', '.join(SUPPORTED_PROVIDERS.keys())}"
            )

        provider_config = SUPPORTED_PROVIDERS[provider_lower]
        client_class = provider_config["client_class"]

        # 使用默认模型如果未指定
        if not model:
            model = provider_config["default_model"]

        logger.info(f"Creating {provider_lower} client with model {model}")

        return client_class(
            api_key=api_key,
            model=model,
            **kwargs
        )

    @staticmethod
    def create_langchain(
        provider: str,
        api_key: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        **kwargs
    ):
        """
        创建 LangChain 兼容的 ChatModel

        Args:
            provider: 提供商名称 (deepseek, doubao)
            api_key: API 密钥
            model: 模型名称
            temperature: 温度参数
            **kwargs: 其他配置参数

        Returns:
            LangChain ChatModel 实例
        """
        from langchain_openai import ChatOpenAI

        provider_lower = provider.lower()

        if provider_lower not in SUPPORTED_PROVIDERS:
            raise ValueError(
                f"不支持的 AI 提供商: {provider}，"
                f"仅支持: {', '.join(SUPPORTED_PROVIDERS.keys())}"
            )

        provider_config = SUPPORTED_PROVIDERS[provider_lower]
        base_url = provider_config["base_url"]
        model_name = model or provider_config["default_model"]

        logger.info(f"Creating LangChain {provider_lower} chat model with {model_name}")

        return ChatOpenAI(
            model=model_name,
            api_key=api_key,
            base_url=base_url,
            temperature=temperature,
            **kwargs
        )

    @staticmethod
    def create_from_config(config: Dict[str, Any], langchain: bool = False) -> Union[BaseLLMClient, "BaseChatModel"]:
        """
        从配置字典创建客户端

        Args:
            config: 配置字典，包含 provider, api_key, model 等字段
            langchain: 是否创建 LangChain ChatModel

        Returns:
            LLM 客户端实例或 LangChain ChatModel
        """
        provider = config.get("provider")
        api_key = config.get("api_key")
        model = config.get("model")
        temperature = config.get("temperature", 0.7)

        if not provider:
            raise ValueError("配置中缺少 provider 字段")
        if not api_key:
            raise ValueError("配置中缺少 api_key 字段")

        if langchain:
            return LLMClientFactory.create_langchain(
                provider=provider,
                api_key=api_key,
                model=model,
                temperature=temperature
            )
        else:
            return LLMClientFactory.create(
                provider=provider,
                api_key=api_key,
                model=model
            )

    @staticmethod
    def get_supported_providers() -> Dict[str, str]:
        """获取支持的提供商列表"""
        return {
            name: config["default_model"]
            for name, config in SUPPORTED_PROVIDERS.items()
        }