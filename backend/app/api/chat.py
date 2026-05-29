from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.api.deps import get_current_user
from app.models.user import User
from app.services.chat_service import ChatService

router = APIRouter(prefix="/api/chat", tags=["AI对话"])


@router.post("")
async def chat(
    message: str,
    session_id: str | None = None,
    user: User = Depends(get_current_user),
):
    svc = ChatService(user, session_id)
    return await svc.chat(message)


@router.post("/stream")
async def chat_stream(
    message: str,
    session_id: str | None = None,
    user: User = Depends(get_current_user),
):
    svc = ChatService(user, session_id)

    async def generate():
        async for chunk in svc.chat_stream(message):
            yield f"data: {chunk}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")
