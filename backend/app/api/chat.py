import json

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.chat import ChatSessionOut, ChatMessageOut
from app.services.chat_service import ChatService
from app.skills import SkillRegistry

router = APIRouter(prefix="/api/chat", tags=["AI对话"])


class ChatSessionRename(BaseModel):
    title: str


@router.get("/skills")
async def list_skills():
    """获取可用的对话风格列表"""
    return SkillRegistry.list()


@router.get("/sessions", response_model=list[ChatSessionOut])
async def list_sessions(user: User = Depends(get_current_user)):
    """获取当前用户的所有会话列表"""
    return await ChatService.list_sessions(user.id)


@router.put("/sessions/{session_id}")
async def rename_session(
    session_id: str,
    body: ChatSessionRename,
    user: User = Depends(get_current_user),
):
    """重命名会话标题"""
    title = body.title.strip()
    if not title:
        raise HTTPException(status_code=400, detail="标题不能为空")
    if len(title) > 100:
        raise HTTPException(status_code=400, detail="标题不能超过100个字符")
    success = await ChatService.rename_session(user.id, session_id, title)
    if not success:
        raise HTTPException(status_code=404, detail="会话不存在")
    return {"ok": True}


@router.delete("/sessions/{session_id}")
async def delete_session(
    session_id: str,
    user: User = Depends(get_current_user),
):
    """删除整个会话及其所有消息"""
    from app.dao.message import MessageDAO
    success = await MessageDAO().delete_session(user.id, session_id)
    if not success:
        raise HTTPException(status_code=404, detail="会话不存在")
    return {"ok": True}


@router.get("/sessions/{session_id}/messages", response_model=list[ChatMessageOut])
async def get_session_messages(
    session_id: str,
    user: User = Depends(get_current_user),
):
    """获取指定会话的消息列表"""
    messages = await ChatService.get_session_messages(user.id, session_id)
    # 为 assistant 消息补充 skill_name 显示名
    for msg in messages:
        if msg.skill_id:
            skill = SkillRegistry.get(msg.skill_id)
            if skill:
                msg.skill_name = skill.name
    return messages


@router.delete("/sessions/{session_id}/messages/{message_id}")
async def delete_message(
    session_id: str,
    message_id: str,
    user: User = Depends(get_current_user),
):
    """删除一条消息及其对应的 AI 回复（QA 对）"""
    from app.dao.message import MessageDAO
    import uuid as uuid_mod
    try:
        msg_uuid = uuid_mod.UUID(message_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="无效的消息 ID")

    success = await MessageDAO().delete_qa_pair(user.id, session_id, msg_uuid)
    if not success:
        raise HTTPException(status_code=404, detail="消息不存在或无权删除")
    return {"ok": True}


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
    skill = SkillRegistry.get(skill_id)
    skill_name = skill.name if skill else None

    async def generate():
        yield f"data: {json.dumps({'session_id': svc.session_id, 'skill_name': skill_name})}\n\n"
        async for chunk in svc.chat_stream(message):
            yield f"data: {chunk}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
