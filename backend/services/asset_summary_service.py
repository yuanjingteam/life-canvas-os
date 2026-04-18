"""资产汇总服务"""
from typing import Tuple
from sqlalchemy.orm import Session

from backend.models.asset import AssetCategory
from backend.models.user import User
from backend.schemas.asset import AssetSummaryResponse, AssetCategorySummary


class AssetSummaryService:
    """资产汇总服务类"""

    @staticmethod
    def get_user(db: Session) -> User:
        user = db.query(User).first()
        if not user:
            from backend.services.auth_service import AuthService
            user = AuthService.create_default_user(db)
        return user

    @staticmethod
    def get_summary(db: Session) -> Tuple[dict, int]:
        user = AssetSummaryService.get_user(db)
        categories = (
            db.query(AssetCategory)
            .filter(AssetCategory.user_id == user.id)
            .all()
        )

        summaries = []
        total_assets = 0.0
        total_liabilities = 0.0

        for category in categories:
            total = sum(item.amount for item in category.items)
            items_count = len(category.items)
            summaries.append(
                AssetCategorySummary(
                    id=category.id,
                    name=category.name,
                    emoji=category.emoji,
                    color=category.color,
                    kind=category.kind,
                    total=total,
                    items_count=items_count,
                    is_system=category.is_system or False,
                )
            )
            if category.kind == "liability":
                total_liabilities += total
            else:
                total_assets += total

        net_assets = total_assets - total_liabilities
        response = AssetSummaryResponse(
            total_assets=total_assets,
            total_liabilities=total_liabilities,
            net_assets=net_assets,
            categories=summaries,
        )
        return response.model_dump(), 200

