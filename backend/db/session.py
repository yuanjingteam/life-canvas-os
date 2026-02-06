from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.core.config import settings

# 针对 SQLite 的特殊参数：check_same_thread=False
# 允许在不同线程中使用同一个连接（FastAPI 是多线程的）
connect_args = {"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,  # 自动检测断开的连接
    echo=False           # 设置为 True 可打印 SQL 语句，方便调试
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 依赖注入函数：用于在 API 中获取数据库会话
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
