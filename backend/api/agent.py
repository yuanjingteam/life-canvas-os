"""
Agent API 路由
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import asyncio
import json

from backend.db.session import get_db
from backend.models.user import User
from backend.services.user_service import UserService
from backend.services.agent_service import AgentService
from backend.schemas.agent import (
    AgentChatRequest,
    AgentConfirmRequest,
    AgentChatResponse,
    AgentHistoryResponse
)
from backend.schemas.agent_context import (
    AgentSessionListResponse,
    AgentSessionListItem,
    AgentSessionResponse,
    MessageResponse
)
from backend.schemas.common import success_response, error_response
from backend.agent.langgraph import AgentExecutor
from backend.agent.core.context import get_context_manager_with_db
from backend.agent.langgraph.tools import get_tool_schemas
from backend.agent.utils.logger import get_logger

logger = get_logger("api")

router = APIRouter(prefix="/api/agent", tags=["agent"])


def get_user_ai_config(db: Session) -> Optional[dict]:
    """获取用户的 AI 配置"""
    user = db.query(User).first()
    if not user or not user.ai_config:
        return None

    ai_config = user.ai_config.copy()
    # 解密 API Key
    encrypted_key = ai_config.get("api_key")
    if encrypted_key:
        try:
            ai_config["api_key"] = UserService.decrypt_api_key(encrypted_key)
        except Exception:
            pass

    return ai_config


def get_current_user_id(db: Session) -> Optional[int]:
    """获取当前用户ID（单用户模式）"""
    user = db.query(User).first()
    return user.id if user else None


@router.post("/chat", response_model=AgentChatResponse)
async def chat(
    request: AgentChatRequest,
    db: Session = Depends(get_db)
):
    """
    Agent 聊天接口

    处理用户消息并返回响应
    """
    # 获取用户 AI 配置
    user_config = get_user_ai_config(db)
    if not user_config:
        raise HTTPException(
            status_code=424,
            detail=error_response(
                message="AI 服务未配置",
                code=424,
                data={"hint": "请先在设置中配置 AI 服务"}
            )
        )

    try:
        user_id = get_current_user_id(db)
        executor = AgentExecutor(db)
        response = await executor.chat(
            message=request.message,
            session_id=request.session_id,
            user_config=user_config,
            user_id=user_id
        )
        return response
    except Exception as e:
        logger.error(f"Agent chat failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=error_response(
                message=f"处理失败: {str(e)}",
                code=500
            )
        )


@router.post("/chat/stream")
async def chat_stream(
    request: AgentChatRequest,
    db: Session = Depends(get_db)
):
    """
    Agent 流式聊天接口

    以 SSE 流式返回响应
    """
    # 获取用户 AI 配置
    user_config = get_user_ai_config(db)
    if not user_config:
        raise HTTPException(
            status_code=424,
            detail=error_response(
                message="AI 服务未配置",
                code=424
            )
        )

    user_id = get_current_user_id(db)

    async def generate():
        """生成 SSE 流"""
        executor = AgentExecutor(db)
        try:
            async for event in executor.stream_chat(
                message=request.message,
                session_id=request.session_id,
                user_config=user_config,
                user_id=user_id
            ):
                # 调试：打印事件类型
                event_type = event.get('type', 'unknown') if isinstance(event, dict) else 'unknown'
                print(f"[DEBUG] Event type: {event_type}", flush=True)

                # 确保 event 中的所有值都可以被序列化
                try:
                    event_str = json.dumps(event, ensure_ascii=False, default=str)
                except Exception as serialize_err:
                    # 如果序列化失败，记录错误并发送错误事件
                    print(f"[DEBUG] Serialize error: {serialize_err}", flush=True)
                    import traceback
                    traceback.print_exc()
                    yield f"data: {json.dumps({'type': 'error', 'message': f'序列化错误: {str(serialize_err)}'}, ensure_ascii=False, default=str)}\n\n"
                    continue
                yield f"data: {event_str}\n\n"
        except Exception as e:
            import traceback
            traceback.print_exc()
            logger.error(f"Stream chat failed: {e}")
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)}, ensure_ascii=False, default=str)}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@router.post("/confirm", response_model=AgentChatResponse)
async def confirm_action(
    request: AgentConfirmRequest,
    db: Session = Depends(get_db)
):
    """
    确认操作接口

    用于确认高风险操作
    """
    try:
        executor = AgentExecutor(db)
        response = await executor.confirm_action(
            session_id=request.session_id,
            confirmation_id=request.confirmation_id,
            confirmed=request.confirmed,
            user_reason=request.user_reason
        )
        return response
    except Exception as e:
        logger.error(f"Confirm action failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=error_response(
                message=f"确认失败: {str(e)}",
                code=500
            )
        )


@router.get("/history/{session_id}", response_model=AgentSessionResponse)
async def get_history(
    session_id: str,
    db: Session = Depends(get_db)
):
    """
    获取会话历史

    返回指定会话的对话历史（从持久化存储加载）
    """
    from datetime import datetime

    service = AgentService(db)
    context = service.get_session(session_id)

    if not context:
        raise HTTPException(
            status_code=404,
            detail=error_response(
                message="会话不存在或已过期",
                code=404
            )
        )

    # 构建消息响应列表
    messages = []
    for i, m in enumerate(context["messages"]):
        # 处理 timestamp 字段（可能是字符串或 datetime）
        ts = m.get("timestamp")
        if isinstance(ts, str):
            created_at = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        elif isinstance(ts, datetime):
            created_at = ts
        else:
            created_at = datetime.now()

        messages.append(MessageResponse(
            id=i,
            role=m["role"],
            content=m["content"],
            actions=m.get("actions", []),
            created_at=created_at
        ))

    # 处理时间字段
    def parse_datetime(dt):
        if isinstance(dt, str):
            return datetime.fromisoformat(dt.replace("Z", "+00:00"))
        return dt

    return AgentSessionResponse(
        session_id=context["session_id"],
        title=context["title"],
        messages=messages,
        referenced_entities=context["referenced_entities"],
        last_operations=context["last_operations"],
        created_at=parse_datetime(context["created_at"]),
        updated_at=parse_datetime(context["updated_at"])
    )


@router.get("/sessions", response_model=AgentSessionListResponse)
async def list_sessions(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    列出所有会话

    返回会话列表（固定会话在前，按更新时间倒序）
    """
    service = AgentService(db)
    sessions, total = service.list_sessions(limit=limit, offset=offset)

    session_items = [
        AgentSessionListItem(**session)
        for session in sessions
    ]

    return AgentSessionListResponse(
        sessions=session_items,
        total=total
    )


@router.delete("/sessions/{session_id}")
async def delete_session(
    session_id: str,
    db: Session = Depends(get_db)
):
    """
    删除会话

    删除指定会话及其所有消息
    """
    service = AgentService(db)
    success = service.delete_session(session_id)

    if not success:
        raise HTTPException(
            status_code=500,
            detail=error_response(message="删除失败", code=500)
        )

    return success_response(
        data={"session_id": session_id},
        message="会话已删除"
    )


@router.patch("/sessions/{session_id}/pin")
async def toggle_pin_session(
    session_id: str,
    pinned: int = Query(..., ge=0, le=1),
    db: Session = Depends(get_db)
):
    """
    切换会话固定状态

    Args:
        session_id: 会话ID
        pinned: 固定状态 (0: 取消固定, 1: 固定)
    """
    service = AgentService(db)
    result = service.toggle_pin(session_id, pinned)

    if result is None:
        raise HTTPException(
            status_code=404,
            detail=error_response(message="会话不存在", code=404)
        )

    return success_response(
        data=result,
        message="操作成功"
    )


@router.get("/skills")
async def list_skills():
    """
    列出所有可用技能

    返回所有已注册的技能列表
    """
    skills = get_tool_schemas()
    return success_response(
        data=skills,
        message=f"共 {len(skills)} 个可用技能"
    )


def handle_agent_action(action: str, params: dict) -> dict:
    """
    处理 Agent IPC action（用于生产模式）

    Args:
        action: action 名称
        params: 参数

    Returns:
        处理结果
    """
    from backend.db.session import SessionLocal

    if action == "agent_chat":
        # 同步调用异步函数
        loop = asyncio.new_event_loop()
        try:
            db = SessionLocal()
            try:
                user_config = get_user_ai_config(db)
                if not user_config:
                    return error_response(
                        message="AI 服务未配置",
                        code=424
                    )

                user_id = get_current_user_id(db)
                executor = AgentExecutor(db)
                response = loop.run_until_complete(
                    executor.chat(
                        message=params.get("message", ""),
                        session_id=params.get("session_id"),
                        user_config=user_config,
                        user_id=user_id
                    )
                )
                return response.model_dump()
            finally:
                db.close()
        finally:
            loop.close()

    elif action == "agent_confirm":
        loop = asyncio.new_event_loop()
        try:
            db = SessionLocal()
            try:
                executor = AgentExecutor(db)
                response = loop.run_until_complete(
                    executor.confirm_action(
                        session_id=params.get("session_id", ""),
                        confirmation_id=params.get("confirmation_id", ""),
                        confirmed=params.get("confirmed", False),
                        user_reason=params.get("user_reason")
                    )
                )
                return response.model_dump()
            finally:
                db.close()
        finally:
            loop.close()

    elif action == "agent_history":
        from datetime import datetime

        db = SessionLocal()
        try:
            service = AgentService(db)
            context = service.get_session(params.get("session_id", ""))

            if not context:
                return error_response(
                    message="会话不存在或已过期",
                    code=404
                )

            # 构建消息响应列表（与 HTTP 接口保持一致）
            messages = []
            for i, m in enumerate(context["messages"]):
                ts = m.get("timestamp")
                if isinstance(ts, str):
                    created_at = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                elif isinstance(ts, datetime):
                    created_at = ts
                else:
                    created_at = datetime.now()

                messages.append({
                    "id": i,
                    "role": m["role"],
                    "content": m["content"],
                    "actions": m.get("actions", []),
                    "created_at": created_at.isoformat()
                })

            # 处理时间字段
            def parse_datetime(dt):
                if isinstance(dt, str):
                    return datetime.fromisoformat(dt.replace("Z", "+00:00"))
                return dt

            # 返回格式化的响应（与 HTTP 接口一致）
            return {
                "session_id": context["session_id"],
                "title": context["title"],
                "messages": messages,
                "referenced_entities": context["referenced_entities"],
                "last_operations": context["last_operations"],
                "created_at": parse_datetime(context["created_at"]).isoformat(),
                "updated_at": parse_datetime(context["updated_at"]).isoformat()
            }
        finally:
            db.close()

    elif action == "agent_sessions":
        db = SessionLocal()
        try:
            service = AgentService(db)
            sessions, total = service.list_sessions(
                limit=params.get("limit", 20),
                offset=params.get("offset", 0)
            )

            return {
                "sessions": sessions,
                "total": total
            }
        finally:
            db.close()

    elif action == "agent_delete_session":
        db = SessionLocal()
        try:
            service = AgentService(db)
            success = service.delete_session(params.get("session_id", ""))

            if not success:
                return error_response(message="删除失败", code=500)

            return {
                "session_id": params.get("session_id"),
                "deleted": True
            }
        finally:
            db.close()

    elif action == "agent_skills":
        skills = get_tool_schemas()
        return {"skills": skills}

    elif action == "agent_toggle_pin":
        db = SessionLocal()
        try:
            service = AgentService(db)
            result = service.toggle_pin(
                params.get("session_id", ""),
                params.get("pinned", 0)
            )

            if result is None:
                return error_response(message="会话不存在", code=404)

            return result
        finally:
            db.close()

    return {"error": f"Unknown action: {action}"}