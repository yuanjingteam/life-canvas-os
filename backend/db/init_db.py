"""数据库初始化脚本（增强版）"""
from sqlalchemy.orm import Session
from sqlalchemy import inspect
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
from backend.models.asset import AssetCategory, AssetItem, AssetSnapshot
from backend.models.session import AgentSession, AgentMessage


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

    # 5. 确保资产系统默认数据存在
    _create_default_assets(db)

    return len(new_tables) > 0


def init_db(db: Session) -> None:
    """初始化数据库（完整版）"""
    # 1. 创建所有表
    print("[INFO] Creating database tables...")
    Base.metadata.create_all(bind=engine)

    # 2. 初始化默认用户
    _create_default_user(db)

    # 3. 初始化用户设置
    _create_default_settings(db)

    # 4. 初始化 8 个系统
    _create_default_systems(db)

    # 5. 初始化资产系统默认数据
    _create_default_assets(db)

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
    user = db.query(User).first()
    if not user:
        return

    existing_systems = db.query(System).filter(System.user_id == user.id).count()
    if existing_systems == 0:
        for system_type in SYSTEM_TYPES:
            system = System(
                user_id=user.id,
                type=system_type,
                score=100,
                details=DEFAULT_SYSTEM_DETAILS.get(system_type, {})
            )
            db.add(system)
        db.commit()
        print(f"[OK] Initialized 8 life balance systems: {', '.join(SYSTEM_TYPES)}")


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


def _create_default_assets(db: Session) -> None:
    """初始化资产系统默认数据"""
    user = db.query(User).first()
    if not user:
        return

    # 1. 检查是否已经有分类，如果有则跳过
    if db.query(AssetCategory).filter(AssetCategory.user_id == user.id).first():
        return

    print("[INFO] Seeding default asset data...")

    # 2. 创建默认分类
    default_categories = [
        {"name": "现金", "emoji": "💵", "color": "amber", "kind": "asset"},
        {"name": "活期/储蓄", "emoji": "🏦", "color": "sky", "kind": "asset"},
        {"name": "投资理财", "emoji": "📈", "color": "emerald", "kind": "asset"},
        {"name": "固定资产", "emoji": "🏠", "color": "orange", "kind": "asset"},
        {"name": "应收款", "emoji": "🤝", "color": "indigo", "kind": "asset"},
        {"name": "负债", "emoji": "🧾", "color": "rose", "kind": "liability"},
        {"name": "保险/公积金/养老金", "emoji": "🛡️", "color": "violet", "kind": "asset"},
        {"name": "其他", "emoji": "📦", "color": "slate", "kind": "asset"},
    ]

    cat_map = {}
    for cat_data in default_categories:
        cat = AssetCategory(user_id=user.id, **cat_data)
        db.add(cat)
        db.flush()  # 获取 ID
        cat_map[cat_data["name"]] = cat.id

    # 3. 添加一些初始资产项
    initial_items = [
        {"name": "钱包现金", "amount": 500.0, "category_id": cat_map["现金"]},
        {"name": "招商银行储蓄卡", "amount": 12000.0, "category_id": cat_map["活期/储蓄"]},
        {"name": "沪深300指数基金", "amount": 50000.0, "category_id": cat_map["投资理财"]},
        {"name": "自住房产", "amount": 1500000.0, "category_id": cat_map["固定资产"]},
        {"name": "信用卡欠款", "amount": 3500.0, "category_id": cat_map["负债"]},
    ]

    for item_data in initial_items:
        item = AssetItem(user_id=user.id, **item_data)
        db.add(item)

    # 4. 生成过去 12 个月的模拟快照（用于趋势图）
    from datetime import date, timedelta
    today = date.today()
    for i in range(12, 0, -1):
        # 模拟每月 1 号的快照
        snap_date = date(today.year, today.month, 1) - timedelta(days=i * 30)
        # 模拟资产缓慢增长
        base_assets = 1500000 + (12 - i) * 5000
        base_liabilities = 5000 - (12 - i) * 200

        snapshot = AssetSnapshot(
            user_id=user.id,
            snapshot_date=snap_date,
            total_assets=float(base_assets),
            total_liabilities=float(base_liabilities),
            net_assets=float(base_assets - base_liabilities),
            note="系统初始化生成的模拟数据"
        )
        db.add(snapshot)

    db.commit()
    print("[OK] Created default asset categories, items and snapshots")
