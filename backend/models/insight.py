# backend/models/insight.py
from sqlalchemy import Column, Integer, Date, String, Text, DateTime
from sqlalchemy.sql import func
from backend.db.base import Base

class Insight(Base):
    __tablename__ = "insights"

    id = Column(Integer, primary_key=True)
    date = Column(Date)              # 洞察生成的日期
    type = Column(String)            # 类型: "daily", "weekly_review"
    content = Column(Text)           # AI 生成的 markdown 内容
    created_at = Column(DateTime, server_default=func.now())
