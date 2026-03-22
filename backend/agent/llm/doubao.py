"""
豆包 LLM 客户端
"""
import json
from typing import AsyncIterator, Dict, Any, List, Optional
import httpx

from backend.agent.llm.base import BaseLLMClient, LLMMessage, LLMResponse
from backend.agent.utils.logger import get_logger
from backend.agent.utils.retry import with_retry

logger = get_logger("doubao")


class DoubaoClient(BaseLLMClient):
    """豆包 API 客户端"""

    @property
    def provider_name(self) -> str:
        return "doubao"

    @property
    def default_model(self) -> str:
        return "doubao-seed-2-0-lite-260215"

    @property
    def api_base_url(self) -> str:
        return "https://ark.cn-beijing.volces.com/api/v3/chat/completions"

    @with_retry(max_retries=2, delay=1.0, exceptions=(httpx.HTTPStatusError,))
    async def chat(
        self,
        messages: List[LLMMessage],
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> LLMResponse:
        """发送聊天请求"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": self.build_messages(messages, system_prompt),
            "temperature": kwargs.get("temperature", self.temperature),
            "max_tokens": kwargs.get("max_tokens", self.max_tokens),
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                self.api_base_url,
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            result = response.json()

        content = result["choices"][0]["message"]["content"]
        finish_reason = result["choices"][0].get("finish_reason", "stop")
        usage = result.get("usage")

        return LLMResponse(
            content=content,
            finish_reason=finish_reason,
            usage=usage
        )

    async def stream_chat(
        self,
        messages: List[LLMMessage],
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> AsyncIterator[str]:
        """流式聊天"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": self.build_messages(messages, system_prompt),
            "temperature": kwargs.get("temperature", self.temperature),
            "max_tokens": kwargs.get("max_tokens", self.max_tokens),
            "stream": True
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            async with client.stream(
                "POST",
                self.api_base_url,
                headers=headers,
                json=payload
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data = line[6:]
                        if data == "[DONE]":
                            break
                        try:
                            chunk = json.loads(data)
                            if chunk["choices"]:
                                delta = chunk["choices"][0].get("delta", {})
                                content = delta.get("content", "")
                                if content:
                                    yield content
                        except json.JSONDecodeError:
                            continue