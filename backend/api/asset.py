"""资产系统 API 接口"""
from datetime import date
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session

from backend.db.session import get_db
from backend.schemas.common import success_response
from backend.schemas.asset import (
    AssetCategoryCreate,
    AssetCategoryUpdate,
    AssetItemCreate,
    AssetItemUpdate,
    AssetSnapshotCreate,
)
from backend.services.asset_service import AssetService
from backend.services.asset_item_service import AssetItemService
from backend.services.asset_summary_service import AssetSummaryService
from backend.services.asset_snapshot_service import AssetSnapshotService


router = APIRouter(prefix="/api/assets", tags=["assets"])


@router.get("/summary")
async def get_summary(db: Session = Depends(get_db)):
    data, status_code = AssetSummaryService.get_summary(db)
    if status_code >= 400:
        raise HTTPException(status_code=status_code, detail=data)
    return success_response(data=data, message="获取资产汇总成功")


@router.get("/snapshots")
async def get_snapshots(
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
    db: Session = Depends(get_db),
):
    data, status_code = AssetSnapshotService.get_snapshots(db, start_date, end_date)
    if status_code >= 400:
        raise HTTPException(status_code=status_code, detail=data)
    return success_response(data=data, message="获取资产快照成功")


@router.post("/snapshots")
async def create_snapshot(
    request: AssetSnapshotCreate,
    db: Session = Depends(get_db),
):
    data, status_code = AssetSnapshotService.create_snapshot(db, request)
    if status_code >= 400:
        raise HTTPException(status_code=status_code, detail=data)
    return success_response(data=data, message="资产快照创建成功", code=status_code)


@router.get("/categories")
async def get_categories(db: Session = Depends(get_db)):
    data, status_code = AssetService.get_categories(db)
    if status_code >= 400:
        raise HTTPException(status_code=status_code, detail=data)
    return success_response(data=data, message="获取分类成功")


@router.post("/categories")
async def create_category(
    request: AssetCategoryCreate,
    db: Session = Depends(get_db),
):
    data, status_code = AssetService.create_category(db, request)
    if status_code >= 400:
        raise HTTPException(status_code=status_code, detail=data)
    return success_response(data=data, message="分类创建成功", code=status_code)


@router.put("/categories/{category_id}")
async def update_category(
    category_id: int,
    request: AssetCategoryUpdate,
    db: Session = Depends(get_db),
):
    data, status_code = AssetService.update_category(db, category_id, request)
    if status_code >= 400:
        raise HTTPException(status_code=status_code, detail=data)
    return success_response(data=data, message="分类更新成功")


@router.delete("/categories/{category_id}")
async def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
):
    data, status_code = AssetService.delete_category(db, category_id)
    if status_code >= 400:
        raise HTTPException(status_code=status_code, detail=data)
    return success_response(data=data, message="分类删除成功")


@router.get("/categories/{category_id}/items")
async def get_items(
    category_id: int,
    db: Session = Depends(get_db),
):
    data, status_code = AssetItemService.get_items(db, category_id)
    if status_code >= 400:
        raise HTTPException(status_code=status_code, detail=data)
    return success_response(data=data, message="获取资产列表成功")


@router.post("/categories/{category_id}/items")
async def create_item(
    category_id: int,
    request: AssetItemCreate,
    db: Session = Depends(get_db),
):
    data, status_code = AssetItemService.create_item(db, category_id, request)
    if status_code >= 400:
        raise HTTPException(status_code=status_code, detail=data)
    return success_response(data=data, message="资产创建成功", code=status_code)


@router.put("/items/{item_id}")
async def update_item(
    item_id: int,
    request: AssetItemUpdate,
    db: Session = Depends(get_db),
):
    data, status_code = AssetItemService.update_item(db, item_id, request)
    if status_code >= 400:
        raise HTTPException(status_code=status_code, detail=data)
    return success_response(data=data, message="资产更新成功")


@router.delete("/items/{item_id}")
async def delete_item(
    item_id: int,
    db: Session = Depends(get_db),
):
    data, status_code = AssetItemService.delete_item(db, item_id)
    if status_code >= 400:
        raise HTTPException(status_code=status_code, detail=data)
    return success_response(data=data, message="资产删除成功")

