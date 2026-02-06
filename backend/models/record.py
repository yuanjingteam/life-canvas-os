from sqlalchemy import Column, Integer, Date, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import relationship
from backend.db.base import Base

class DailyRecord(Base):
    __tablename__ = "daily_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    dimension_id = Column(Integer, ForeignKey("dimensions.id"))

    date = Column(Date, index=True)
    score = Column(Integer)  # 1-10 分
    note = Column(String, nullable=True) # 简短备注

    # 关系属性，方便查询
    user = relationship("User")
    dimension = relationship("Dimension")

    # 联合唯一约束：同一个用户、同一天、同一个维度只能有一条记录
    __table_args__ = (
        UniqueConstraint('user_id', 'dimension_id', 'date', name='uq_user_dim_date'),
    )
