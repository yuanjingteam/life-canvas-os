"""资产快照服务"""
from typing import Tuple, Optional
from datetime import date
from sqlalchemy.orm import Session

from backend.models.asset import AssetSnapshot
from backend.models.user import User
from backend.schemas.asset import AssetSnapshotCreate, AssetSnapshotResponse
from backend.schemas.common import error_response
from backend.services.asset_summary_service import AssetSummaryService


class AssetSnapshotService:
    """资产快照服务类"""

    @staticmethod
    def get_user(db: Session) -> User:
        user = db.query(User).first()
        if not user:
            from backend.services.auth_service import AuthService
            user = AuthService.create_default_user(db)
        return user

    @staticmethod
    def get_snapshots(
        db: Session,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> Tuple[dict, int]:
        user = AssetSnapshotService.get_user(db)
        query = db.query(AssetSnapshot).filter(AssetSnapshot.user_id == user.id)

        if start_date:
            query = query.filter(AssetSnapshot.snapshot_date >= start_date)
        if end_date:
            query = query.filter(AssetSnapshot.snapshot_date <= end_date)

        snapshots = query.order_by(AssetSnapshot.snapshot_date.desc()).all()
        items = [AssetSnapshotResponse.model_validate(s).model_dump() for s in snapshots]
        return {"items": items}, 200

    @staticmethod
    def create_snapshot(
        db: Session,
        request: AssetSnapshotCreate,
    ) -> Tuple[dict, int]:
        user = AssetSnapshotService.get_user(db)
        summary_data, status_code = AssetSummaryService.get_summary(db)
        if status_code >= 400:
            return error_response(message="获取汇总失败", code=status_code), status_code

        snapshot_data = {
            "user_id": user.id,
            "total_assets": summary_data["total_assets"],
            "total_liabilities": summary_data["total_liabilities"],
            "net_assets": summary_data["net_assets"],
            "note": request.note,
        }
        if request.snapshot_date:
            snapshot_data["snapshot_date"] = request.snapshot_date

        snapshot = AssetSnapshot(**snapshot_data)
        db.add(snapshot)
        db.commit()
        db.refresh(snapshot)

        return AssetSnapshotResponse.model_validate(snapshot).model_dump(), 201

