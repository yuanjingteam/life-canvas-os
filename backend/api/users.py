"""用户配置 API 接口"""
from fastapi import APIRouter, HTTPException, Depends, status, Body
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel, Field

from backend.db.session import get_db
from backend.services.user_service import UserService
from backend.schemas.user import (
    UserUpdate,
    UserResponse,
    UserSettingsUpdate,
    UserSettingsResponse,
    AIConfigBase,
    AIConfigResponse,
)
from backend.schemas.common import success_response, error_response


router = APIRouter(prefix="/api/user", tags=["user"])


# ============ API Key 验证 Schema ============

class APIKeyVerifyRequest(BaseModel):
    """API Key 验证请求"""
    provider: str = Field(..., description="AI 提供商 (deepseek, doubao)")
    api_key: str = Field(..., description="API Key")
    model: Optional[str] = Field(None, description="可选的模型名称")


# ============ 用户信息 ============

@router.get("/profile")
async def get_user_profile(db: Session = Depends(get_db)):
    """
    获取用户信息
    """
    data, status_code = UserService.get_user_profile(db)

    if status_code >= 400:
        raise HTTPException(
            status_code=status_code,
            detail=data
        )

    return success_response(
        data=data,
        message="获取用户信息成功"
    )


@router.patch("/profile")
async def update_user_profile(
    request: UserUpdate,
    db: Session = Depends(get_db)
):
    """
    更新用户信息
    """
    data, status_code = UserService.update_user_profile_enhanced(db, request)

    if status_code >= 400:
        raise HTTPException(
            status_code=status_code,
            detail=data
        )

    return success_response(
        data=data,
        message="用户信息更新成功"
    )


# ============ 用户设置 ============

@router.get("/settings")
async def get_user_settings(db: Session = Depends(get_db)):
    """
    获取用户设置
    """
    data, status_code = UserService.get_user_settings(db)

    if status_code >= 400:
        raise HTTPException(
            status_code=status_code,
            detail=data
        )

    return success_response(
        data=data,
        message="获取用户设置成功"
    )


@router.patch("/settings")
async def update_user_settings(
    request: UserSettingsUpdate,
    db: Session = Depends(get_db)
):
    """
    更新用户设置
    """
    data, status_code = UserService.update_user_settings(db, request)

    if status_code >= 400:
        raise HTTPException(
            status_code=status_code,
            detail=data
        )

    return success_response(
        data=data,
        message="用户设置更新成功"
    )


# ============ AI 配置 ============

@router.post("/ai-config")
async def save_ai_config(
    request: AIConfigBase,
    db: Session = Depends(get_db)
):
    """
    保存 AI 配置（自动验证 API Key 有效性）

    流程：
    1. 先验证 API Key 是否有效
    2. 验证通过后才保存配置
    3. 验证失败则返回错误，不保存配置
    """
    # 步骤1：验证 API Key 有效性
    verify_data, verify_status = await UserService.verify_api_key(
        provider=request.provider,
        api_key=request.api_key,
        model=request.model_name
    )

    # 如果验证失败，直接返回错误（不保存配置）
    if verify_status >= 400:
        raise HTTPException(
            status_code=verify_status,
            detail=verify_data
        )

    # 步骤2：验证成功后才保存配置
    data, status_code = UserService.save_ai_config(
        db,
        request.provider,
        request.api_key,
        request.model_name or "deepseek-chat"
    )

    if status_code >= 400:
        raise HTTPException(
            status_code=status_code,
            detail=data
        )

    return success_response(
        data={
            "provider": data.get("provider"),
            "model_name": data.get("model"),
            "updated_at": data.get("updated_at") if isinstance(data, dict) else None,
            "verified": True  # 标识已验证过
        },
        message="AI 配置保存成功"
    )


@router.get("/ai-config")
async def get_ai_config(db: Session = Depends(get_db)):
    """
    获取 AI 配置（不返回完整 API Key）
    """
    import sys
    import traceback as tb

    try:
        data, status_code = UserService.get_ai_config_masked(db)

        # 验证返回数据的完整性
        if data is not None and not isinstance(data, dict):
            print(f"[DEBUG] Invalid data type: {type(data)}", file=sys.stderr)
            raise HTTPException(
                status_code=500,
                detail=error_response(
                    message="数据格式错误",
                    code=500,
                    data={"expected": "dict", "got": str(type(data))}
                )
            )

    except HTTPException:
        raise  # 重新抛出 HTTPException
    except Exception as e:
        print(f"[DEBUG] Error in get_ai_config: {type(e).__name__}: {e}", file=sys.stderr)
        print(f"[DEBUG] Traceback: {tb.format_exc()}", file=sys.stderr)
        raise HTTPException(
            status_code=500,
            detail=error_response(
                message=f"获取 AI 配置失败: {str(e)}",
                code=500,
                data={"error_type": type(e).__name__}
            )
        )

    if status_code == 404:
        raise HTTPException(
            status_code=status.HTTP_424_FAILED_DEPENDENCY,
            detail=error_response(
                message="AI 服务未配置",
                code=424,
                data={"hint": "请先配置 AI 服务"}
            )
        )

    return success_response(
        data=data,
        message="获取 AI 配置成功"
    )


@router.post("/ai-config/verify")
async def verify_api_key(
    request: APIKeyVerifyRequest,
    db: Session = Depends(get_db)
):
    """
    验证 API Key 有效性

    在保存前验证 API Key 是否有效，避免保存无效的 Key。
    仅支持 DeepSeek 和豆包两个提供商。
    """
    data, status_code = await UserService.verify_api_key(
        provider=request.provider,
        api_key=request.api_key,
        model=request.model
    )

    if status_code >= 400:
        raise HTTPException(
            status_code=status_code,
            detail=data
        )

    return success_response(
        data=data,
        message="API Key 验证成功"
    )
