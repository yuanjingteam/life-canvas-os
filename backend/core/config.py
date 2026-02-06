import os
from pydantic_settings import BaseSettings
from pathlib import Path

# 获取 backend 目录的父级目录 (即项目根目录)
BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    PROJECT_NAME: str = "Life Canvas OS"
    API_V1_STR: str = "/api/v1"

    # 数据库配置
    # 默认使用 SQLite，文件存储在根目录下
    SQLITE_URL: str = f"sqlite:///{BASE_DIR}/life_canvas.db"

    # 如果将来想换 PostgreSQL，只需修改环境变量即可覆盖
    DATABASE_URL: str = os.getenv("DATABASE_URL", SQLITE_URL)

    class Config:
        case_sensitive = True

settings = Settings()
