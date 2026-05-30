import json

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.chat import ChatSessionOut, ChatMessageOut
from app.services.chat_service import ChatService
from app.skills import SkillRegistry

router = APIRouter(prefix="/api/chat", tags=["AI对话"])


@router.get("/skills")
async def list_skills():
    """获取可用的对话风格列表"""
    return SkillRegistry.list()


@router.get("/sessions", response_model=list[ChatSessionOut])
async def list_sessions(user: User = Depends(get_current_user)):
    """获取当前用户的所有会话列表"""
    return await ChatService.list_sessions(user.id)


@router.get("/sessions/{session_id}/messages", response_model=list[ChatMessageOut])
async def get_session_messages(
    session_id: str,
    user: User = Depends(get_current_user),
):
    """获取指定会话的消息列表"""
    return await ChatService.get_session_messages(user.id, session_id)


@router.post("")
async def chat(
    message: str,
    session_id: str | None = None,
    skill_id: str = "default",
    user: User = Depends(get_current_user),
):
    svc = ChatService(user, session_id, skill_id=skill_id)
    return await svc.chat(message)


@router.post("/stream")
async def chat_stream(
    message: str,
    session_id: str | None = None,
    skill_id: str = "default",
    user: User = Depends(get_current_user),
):
    svc = ChatService(user, session_id, skill_id=skill_id)

    async def generate():
        yield f"data: {json.dumps({'session_id': svc.session_id})}\n\n"
        async for chunk in svc.chat_stream(message):
            yield f"data: {chunk}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
