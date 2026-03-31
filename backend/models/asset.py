"""资产系统模型"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Date, ForeignKey, text
from sqlalchemy.orm import relationship

from backend.db.base import Base
from backend.db.session import localnow_func


class AssetCategory(Base):
    __tablename__ = "asset_categories"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), default=1)

    name = Column(String(100), nullable=False)
    emoji = Column(String(20), default="💼")
    color = Column(String(30), default="amber")
    kind = Column(String(20), default="asset")

    created_at = Column(DateTime, server_default=localnow_func())
    updated_at = Column(DateTime, server_default=localnow_func(), onupdate=localnow_func())

    items = relationship(
        "AssetItem",
        back_populates="category",
        cascade="all, delete-orphan",
    )


class AssetItem(Base):
    __tablename__ = "asset_items"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), default=1)
    category_id = Column(Integer, ForeignKey("asset_categories.id"), nullable=False)

    name = Column(String(200), nullable=False)
    amount = Column(Float, nullable=False)
    note = Column(String(500), nullable=True)

    created_at = Column(DateTime, server_default=localnow_func())
    updated_at = Column(DateTime, server_default=localnow_func(), onupdate=localnow_func())

    category = relationship("AssetCategory", back_populates="items")


class AssetSnapshot(Base):
    __tablename__ = "asset_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), default=1)
    snapshot_date = Column(Date, server_default=text("CURRENT_DATE"))

    total_assets = Column(Float, nullable=False)
    total_liabilities = Column(Float, nullable=False)
    net_assets = Column(Float, nullable=False)
    note = Column(String(500), nullable=True)

    created_at = Column(DateTime, server_default=localnow_func())



