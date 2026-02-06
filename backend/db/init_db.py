from sqlalchemy.orm import Session
from backend.db.base import Base
from backend.db.session import engine, SessionLocal
from backend.models.user import User
from backend.models.dimension import Dimension
from backend.models.record import DailyRecord
# 导入所有模型确保它们被 SQLAlchemy 注册

def init_db(db: Session):
    # 1. 创建所有表
    Base.metadata.create_all(bind=engine)

    # 2. 初始化默认用户
    user = db.query(User).first()
    if not user:
        user = User(username="Owner", preferences={"theme": "system"})
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"Created default user: {user.username}")

    # 3. 初始化 8 个子系统维度
    # 检查是否已存在，不存在则创建
    existing_dims = db.query(Dimension).count()
    if existing_dims == 0:
        default_dimensions = [
            {"key": "fuel", "name": "饮食系统", "icon": "utensils", "color": "#FF6B6B", "sort_order": 1},
            {"key": "physical", "name": "运动系统", "icon": "dumbbell", "color": "#4ECDC4", "sort_order": 2},
            {"key": "intellectual", "name": "读书系统", "icon": "book-open", "color": "#45B7D1", "sort_order": 3},
            {"key": "output", "name": "工作系统", "icon": "briefcase", "color": "#96CEB4", "sort_order": 4},
            {"key": "recovery", "name": "梦想系统", "icon": "moon", "color": "#FFEEAD", "sort_order": 5},
            {"key": "asset", "name": "财务系统", "icon": "wallet", "color": "#D4A5A5", "sort_order": 6},
            {"key": "connection", "name": "社交系统", "icon": "users", "color": "#9B59B6", "sort_order": 7},
            {"key": "environment", "name": "环境系统", "icon": "home", "color": "#34495E", "sort_order": 8},
        ]
        for dim_data in default_dimensions:
            dim = Dimension(**dim_data)
            db.add(dim)
        db.commit()
        print("初始化 8 个子系统维度.")

if __name__ == "__main__":
    print("创建数据库表...")
    db = SessionLocal()
    init_db(db)
    print("数据库初始化成功!")
