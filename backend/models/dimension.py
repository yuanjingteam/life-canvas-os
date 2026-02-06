from sqlalchemy import Column, Integer, String
from backend.db.base import Base

class Dimension(Base):
    __tablename__ = "dimensions"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, index=True)  # 例如: "fuel", "physical"
    name = Column(String)              # 例如: "饮食系统", "运动系统"
    icon = Column(String)              # 前端图标名称
    color = Column(String)             # HEX 颜色代码
    description = Column(String, nullable=True)
    sort_order = Column(Integer, default=0)
