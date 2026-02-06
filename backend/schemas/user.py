from pydantic import BaseModel
from typing import Optional, Literal

# 定义支持的 AI 厂商
AIProvider = Literal["openai", "deepseek", "doubao", "custom"]

class AIConfigUpdate(BaseModel):
    provider: AIProvider
    api_key: str
    model: Optional[str] = None
    base_url: Optional[str] = None

class UserUpdate(BaseModel):
    preferences: Optional[dict] = None
    ai_config: Optional[AIConfigUpdate] = None
