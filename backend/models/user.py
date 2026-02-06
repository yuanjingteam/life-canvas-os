from sqlalchemy import Column, Integer, String, JSON, DateTime
from sqlalchemy.sql import func
from backend.db.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, default="Owner")
    pin_hash = Column(String, nullable=True)

    # 基础偏好 (主题, 布局)
    preferences = Column(JSON, default={})

    # --- 新增：AI 配置字段 ---
    # 结构示例:
    # {
    #   "provider": "deepseek",  # deepseek / openai / doubao
    #   "api_key": "sk-xxxxxx",
    #   "base_url": "https://api.deepseek.com", # 可选，自定义代理地址
    #   "model": "deepseek-chat"
    # }
    ai_config = Column(JSON, default={})

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
