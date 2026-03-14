"""
Agent API 路由

处理 Agent 聊天、确认和历史记录请求。
"""

from fastapi import APIRouter, HTTPException
from typing import Optional, Dict, Any
import uuid
import asyncio

from backend.schemas.agent import (
    ChatRequest,
    ConfirmRequest,
    ConfirmResponse,
    HistoryResponse,
)
from backend.schemas.common import success_response, error_response
from backend.core.exceptions import AppException
from backend.agent.init import execute_chat, get_context_manager, get_pending_confirmations

router = APIRouter(prefix="/api/agent", tags=["agent"])


@router.post("/chat", response_model=Dict[str, Any])
async def chat(request: ChatRequest):
    """
    Agent 聊天接口

    处理用户的自然语言输入，返回 AI 回复和执行结果。
    """
    try:
        # 生成会话 ID
        session_id = request.session_id or f"sess_{uuid.uuid4().hex[:12]}"

        # 执行 Agent 聊天
        response_data = await execute_chat(
            message=request.message,
            session_id=session_id,
        )

        return success_response(
            data=response_data,
            message="聊天成功",
            code=200,
        )

    except AppException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        return error_response(message=f"聊天失败：{str(e)}", code=500)


@router.post("/confirm", response_model=Dict[str, Any])
async def confirm(request: ConfirmRequest):
    """
    Agent 确认接口

    处理用户对高风险操作的确认请求。
    """
    try:
        # 查找待确认请求
        _pending_confirmations = get_pending_confirmations()
        confirmation = _pending_confirmations.get(request.confirmation_id)

        if not confirmation:
            return error_response(message="确认 ID 不存在或已过期", code=404)

        if not request.confirmed:
            # 用户取消
            del _pending_confirmations[request.confirmation_id]
            return success_response(
                data={"response": "操作已取消"},
                message="取消成功",
                code=200,
            )

        # 验证验证码（如果是 CRITICAL 等级）
        if confirmation.get("risk_level") == "CRITICAL":
            if not request.code or request.code != confirmation.get("code"):
                return error_response(message="验证码错误", code=400)

        # 执行确认后的操作
        action_type = confirmation.get("action_type")
        action_data = confirmation.get("action_data", {})

        if action_type == "delete_journal":
            journal_id = action_data.get("id") or action_data.get("journal_id")
            if not journal_id:
                return error_response(message="无效的删除请求", code=400)

            from backend.services.journal_service import JournalService
            from backend.db.session import get_db_context

            with get_db_context() as db:
                result, status_code = JournalService.delete_diary(db, journal_id)
                if status_code != 200:
                    return error_response(message=result.get("message", "删除失败"), code=status_code)

                del _pending_confirmations[request.confirmation_id]
                return success_response(
                    data={"response": f"已删除日记 ID: {journal_id}"},
                    message="删除成功",
                    code=200,
                )

        # 未知操作类型
        del _pending_confirmations[request.confirmation_id]
        return success_response(
            data={"response": "操作已确认并执行"},
            message="确认成功",
            code=200,
        )

    except AppException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        return error_response(message=f"确认失败：{str(e)}", code=500)


@router.get("/history", response_model=Dict[str, Any])
async def get_history(session_id: str, limit: int = 10):
    """
    获取会话历史

    返回指定会话的对话历史记录。
    """
    try:
        ctx_manager = get_context_manager()
        if not ctx_manager:
            return error_response(message="上下文管理器未初始化", code=500)

        context = ctx_manager.get(session_id)
        if not context:
            return error_response(message="会话不存在", code=404)

        # 获取消息历史
        messages = context.messages[-limit:] if context.messages else []

        return success_response(
            data={"messages": messages, "session_id": session_id},
            message="获取历史成功",
            code=200,
        )

    except Exception as e:
        return error_response(message=f"获取历史失败：{str(e)}", code=500)


@router.delete("/session/{session_id}", response_model=Dict[str, Any])
async def delete_session(session_id: str):
    """
    删除会话

    清空指定会话的上下文和历史记录。
    """
    try:
        ctx_manager = get_context_manager()
        if ctx_manager:
            ctx_manager.delete(session_id)

        return success_response(
            data={"session_id": session_id},
            message="删除成功",
            code=200,
        )

    except Exception as e:
        return error_response(message=f"删除失败：{str(e)}", code=500)
