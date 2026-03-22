"""数据库初始化脚本（增强版）"""
from sqlalchemy.orm import Session
from sqlalchemy import inspect, text
from backend.db.base import Base
from backend.db.session import engine, SessionLocal

# 导入所有模型确保它们被 SQLAlchemy 注册
from backend.models.user import User, UserSettings
from backend.models.dimension import (
    System,
    SystemLog,
    SystemAction,
    MealDeviation,
    SystemScoreLog,
    SYSTEM_TYPES,
    DEFAULT_SYSTEM_DETAILS
)
from backend.models.diary import Diary, DiaryAttachment, DiaryEditHistory
from backend.models.insight import Insight
from backend.models.record import DailyRecord
from backend.models.agent import AgentSession, AgentMessage


def _migrate_agent_sessions_table(db: Session) -> None:
    """
    迁移 agent_sessions 表，添加缺失的列
    SQLAlchemy 的 create_all 不会修改已存在的表
    """
    inspector = inspect(engine)

    # 检查 agent_sessions 表是否存在
    table_names = inspector.get_table_names()
    print(f"[DEBUG] Existing tables: {table_names}")

    if 'agent_sessions' not in table_names:
        print("[DEBUG] agent_sessions table does not exist, skipping migration")
        return

    # 获取现有列
    existing_columns = {col['name'] for col in inspector.get_columns('agent_sessions')}
    print(f"[DEBUG] Existing columns in agent_sessions: {existing_columns}")

    # 定义需要添加的列 (name -> SQL type)
    # 参考 backend/models/agent.py 中 AgentSession 模型的定义
    columns_to_add = {
        'title': 'VARCHAR(200)',
        'pinned': 'INTEGER DEFAULT 0',
        'referenced_entities': 'JSON',
        'last_operations': 'JSON',
        'expires_at': 'DATETIME',
    }

    # 添加缺失的列
    migrated = False
    for column_name, column_type in columns_to_add.items():
        if column_name not in existing_columns:
            try:
                sql = text(f'ALTER TABLE agent_sessions ADD COLUMN {column_name} {column_type}')
                db.execute(sql)
                db.commit()
                print(f"[OK] Added column '{column_name}' to agent_sessions table")
                migrated = True
            except Exception as e:
                db.rollback()
                print(f"[WARN] Failed to add column '{column_name}': {e}")

    if migrated:
        print("[INFO] agent_sessions table migration completed")


def ensure_database_initialized(db: Session) -> bool:
    """
    确保数据库已初始化（自动创建新表并初始化默认数据）

    Returns:
        是否进行了初始化操作
    """
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()

    # 始终尝试创建所有表（SQLAlchemy 会跳过已存在的表）
    if len(existing_tables) == 0:
        print("[INFO] No database tables found. Initializing database...")
    else:
        print(f"[INFO] Found {len(existing_tables)} existing tables. Checking for new tables...")

    # 1. 创建所有表（包括新增的模型）
    Base.metadata.create_all(bind=engine)

    # 检查是否有新表被创建
    new_tables = [t for t in inspector.get_table_names() if t not in existing_tables]
    if new_tables:
        print(f"[OK] Created new tables: {new_tables}")

    # 1.5. 迁移现有表（添加缺失的列）
    _migrate_agent_sessions_table(db)

    # 2. 检查并创建默认用户
    user = db.query(User).first()
    if not user:
        print("[INFO] No default user found. Creating...")
        _create_default_user(db)
        _create_default_settings(db)
        _create_default_systems(db)
        return True

    # 3. 确保用户设置存在
    _create_default_settings(db)

    # 4. 确保8个系统存在
    _create_default_systems(db)

    return len(new_tables) > 0


def init_db(db: Session) -> None:
    """初始化数据库（完整版）"""
    # 1. 创建所有表
    print("[INFO] Creating database tables...")
    Base.metadata.create_all(bind=engine)

    # 1.5. 迁移现有表
    _migrate_agent_sessions_table(db)

    # 2. 初始化默认用户
    _create_default_user(db)

    # 3. 初始化用户设置
    _create_default_settings(db)

    # 4. 初始化 8 个系统
    _create_default_systems(db)

    print("\n[SUCCESS] Database initialization completed!")


def _create_default_user(db: Session) -> User:
    """创建默认用户"""
    user = db.query(User).first()
    if not user:
        user = User(
            username="Owner",
            display_name="用户",
            preferences={"theme": "dark"}
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"[OK] Created default user: {user.username}")
    return user


def _create_default_settings(db: Session) -> None:
    """创建默认用户设置"""
    user = db.query(User).first()
    if not user:
        return

    settings = db.query(UserSettings).filter(UserSettings.user_id == user.id).first()
    if not settings:
        settings = UserSettings(user_id=user.id)
        db.add(settings)
        db.commit()
        print(f"[OK] Created default user settings")


def _create_default_systems(db: Session) -> None:
    """创建默认的 8 个系统"""
    from backend.models.dimension import SystemType

    user = db.query(User).first()
    if not user:
        return

    existing_systems = db.query(System).filter(System.user_id == user.id).count()
    if existing_systems == 0:
        for system_type in SystemType.list():
            system = System(
                user_id=user.id,
                type=system_type,
                score=100,
                details=DEFAULT_SYSTEM_DETAILS.get(system_type, {})
            )
            db.add(system)
        db.commit()
        print(f"[OK] Initialized 8 life balance systems: {', '.join(SystemType.list())}")


def is_database_empty() -> bool:
    """检查数据库是否为空（无数据）"""
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    return len(tables) == 0


if __name__ == "__main__":
    print("Starting database initialization...")
    db = SessionLocal()
    try:
        init_db(db)
    except Exception as e:
        print(f"Initialization failed: {e}")
        db.rollback()
        raise
    finally:
        db.close()
