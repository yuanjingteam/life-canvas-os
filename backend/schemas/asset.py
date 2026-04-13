"""资产系统 Schema"""
from typing import Optional, List, Literal
from datetime import datetime, date
from pydantic import BaseModel, Field, ConfigDict


CategoryKind = Literal["asset", "liability"]


class AssetCategoryBase(BaseModel):
    name: str = Field(..., max_length=100, description="分类名称")
    emoji: str = Field("💼", max_length=20, description="分类图标")
    color: str = Field("amber", max_length=30, description="颜色标识")
    kind: CategoryKind = Field("asset", description="分类类型")


class AssetCategoryCreate(AssetCategoryBase):
    pass


class AssetCategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    emoji: Optional[str] = Field(None, max_length=20)
    color: Optional[str] = Field(None, max_length=30)
    kind: Optional[CategoryKind] = None


class AssetCategoryResponse(AssetCategoryBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class AssetItemBase(BaseModel):
    name: str = Field(..., max_length=200, description="资产名称")
    amount: float = Field(..., description="金额")
    note: Optional[str] = Field(None, max_length=500, description="备注")


class AssetItemCreate(AssetItemBase):
    pass


class AssetItemUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=200)
    amount: Optional[float] = None
    note: Optional[str] = Field(None, max_length=500)


class AssetItemResponse(AssetItemBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    category_id: int
    created_at: datetime
    updated_at: datetime


class AssetCategorySummary(BaseModel):
    id: int
    name: str
    emoji: str
    color: str
    kind: CategoryKind
    total: float
    items_count: int


class AssetSummaryResponse(BaseModel):
    total_assets: float
    total_liabilities: float
    net_assets: float
    categories: List[AssetCategorySummary]


class AssetSnapshotCreate(BaseModel):
    snapshot_date: Optional[date] = Field(None, description="快照日期")
    note: Optional[str] = Field(None, max_length=500, description="备注")


class AssetSnapshotResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    snapshot_date: date
    total_assets: float
    total_liabilities: float
    net_assets: float
    note: Optional[str]
    created_at: datetime


