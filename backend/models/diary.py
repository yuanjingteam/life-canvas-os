# backend/models/diary.py
from sqlalchemy import Column, Integer, Date, ForeignKey, Text, JSON
from backend.db.base import Base

class Diary(Base):
    __tablename__ = "diaries"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    date = Column(Date, unique=True)  # 每天一篇日记

    content = Column(Text)            # Markdown 或纯文本内容
    mood = Column(String)             # 心情标签 (如 "Happy", "Anxious")
    tags = Column(JSON)               # 标签数组 ["work", "milestone"]
