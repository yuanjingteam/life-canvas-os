# 数据库模块
# backend/db/__init__.py

from .base import Base
from .session import get_db, engine, SessionLocal

# 这样在 API 路由里只需：from backend.db import get_db
