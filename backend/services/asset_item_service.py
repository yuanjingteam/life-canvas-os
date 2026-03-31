"""资产项服务"""
from typing import Tuple
from sqlalchemy.orm import Session

from backend.models.asset import AssetCategory, AssetItem
from backend.models.user import User
from backend.schemas.asset import (
    AssetItemCreate,
    AssetItemUpdate,
    AssetItemResponse,
)
from backend.schemas.common import error_response


class AssetItemService:
    """资产项服务类"""

    @staticmethod
    def get_user(db: Session) -> User:
        user = db.query(User).first()
        if not user:
            from backend.services.auth_service import AuthService
            user = AuthService.create_default_user(db)
        return user

    @staticmethod
    def get_items(db: Session, category_id: int) -> Tuple[dict, int]:
        user = AssetItemService.get_user(db)
        category = (
            db.query(AssetCategory)
            .filter(AssetCategory.id == category_id, AssetCategory.user_id == user.id)
            .first()
        )
        if not category:
            return error_response(message="分类不存在", code=404), 404

        items = (
            db.query(AssetItem)
            .filter(
                AssetItem.user_id == user.id,
                AssetItem.category_id == category_id,
            )
            .order_by(AssetItem.created_at.desc())
            .all()
        )
        payload = [AssetItemResponse.model_validate(i).model_dump() for i in items]
        return {"items": payload}, 200

    @staticmethod
    def create_item(
        db: Session,
        category_id: int,
        request: AssetItemCreate,
    ) -> Tuple[dict, int]:
        user = AssetItemService.get_user(db)
        category = (
            db.query(AssetCategory)
            .filter(AssetCategory.id == category_id, AssetCategory.user_id == user.id)
            .first()
        )
        if not category:
            return error_response(message="分类不存在", code=404), 404

        item = AssetItem(
            user_id=user.id,
            category_id=category_id,
            name=request.name,
            amount=request.amount,
            note=request.note,
        )
        db.add(item)
        db.commit()
        db.refresh(item)
        return AssetItemResponse.model_validate(item).model_dump(), 201

    @staticmethod
    def update_item(
        db: Session,
        item_id: int,
        request: AssetItemUpdate,
    ) -> Tuple[dict, int]:
        user = AssetItemService.get_user(db)
        item = (
            db.query(AssetItem)
            .filter(AssetItem.id == item_id, AssetItem.user_id == user.id)
            .first()
        )
        if not item:
            return error_response(message="资产不存在", code=404), 404

        for field, value in request.model_dump(exclude_unset=True).items():
            setattr(item, field, value)

        db.commit()
        db.refresh(item)
        return AssetItemResponse.model_validate(item).model_dump(), 200

    @staticmethod
    def delete_item(db: Session, item_id: int) -> Tuple[dict, int]:
        user = AssetItemService.get_user(db)
        item = (
            db.query(AssetItem)
            .filter(AssetItem.id == item_id, AssetItem.user_id == user.id)
            .first()
        )
        if not item:
            return error_response(message="资产不存在", code=404), 404

        db.delete(item)
        db.commit()
        return {"id": item_id}, 200

