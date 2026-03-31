"""资产系统服务"""
from typing import Tuple
from sqlalchemy.orm import Session

from backend.models.asset import AssetCategory
from backend.models.user import User
from backend.schemas.asset import (
    AssetCategoryCreate,
    AssetCategoryUpdate,
    AssetCategoryResponse,
)
from backend.schemas.common import error_response


class AssetService:
    """资产系统服务类"""

    @staticmethod
    def get_user(db: Session) -> User:
        user = db.query(User).first()
        if not user:
            from backend.services.auth_service import AuthService
            user = AuthService.create_default_user(db)
        return user

    @staticmethod
    def get_categories(db: Session) -> Tuple[dict, int]:
        user = AssetService.get_user(db)
        categories = (
            db.query(AssetCategory)
            .filter(AssetCategory.user_id == user.id)
            .order_by(AssetCategory.created_at.desc())
            .all()
        )
        items = [AssetCategoryResponse.model_validate(c).model_dump() for c in categories]
        return {"items": items}, 200

    @staticmethod
    def create_category(db: Session, request: AssetCategoryCreate) -> Tuple[dict, int]:
        user = AssetService.get_user(db)
        category = AssetCategory(
            user_id=user.id,
            name=request.name,
            emoji=request.emoji or "💼",
            color=request.color or "amber",
            kind=request.kind,
        )
        db.add(category)
        db.commit()
        db.refresh(category)
        return AssetCategoryResponse.model_validate(category).model_dump(), 201

    @staticmethod
    def update_category(
        db: Session,
        category_id: int,
        request: AssetCategoryUpdate,
    ) -> Tuple[dict, int]:
        user = AssetService.get_user(db)
        category = (
            db.query(AssetCategory)
            .filter(AssetCategory.id == category_id, AssetCategory.user_id == user.id)
            .first()
        )
        if not category:
            return error_response(message="分类不存在", code=404), 404

        for field, value in request.model_dump(exclude_unset=True).items():
            setattr(category, field, value)

        db.commit()
        db.refresh(category)
        return AssetCategoryResponse.model_validate(category).model_dump(), 200

    @staticmethod
    def delete_category(db: Session, category_id: int) -> Tuple[dict, int]:
        user = AssetService.get_user(db)
        category = (
            db.query(AssetCategory)
            .filter(AssetCategory.id == category_id, AssetCategory.user_id == user.id)
            .first()
        )
        if not category:
            return error_response(message="分类不存在", code=404), 404

        db.delete(category)
        db.commit()
        return {"id": category_id}, 200

