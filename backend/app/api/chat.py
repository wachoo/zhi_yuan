import uuid
from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.api.deps import get_current_user
from app.models.user import User, UserProfile
from app.models.recommendation import ChatMessage, Recommendation
from app.services.llm_service import LLMService

router = APIRouter(prefix="/api/chat", tags=["AI对话"])

FREE_DAILY_LIMIT = 3


@router.post("")
async def chat(
    message: str,
    session_id: str | None = None,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    today = date.today().isoformat()
    if user.last_chat_date != today:
        user.daily_chat_count = 0
        user.last_chat_date = today

    if user.membership_tier == "free" and user.daily_chat_count >= FREE_DAILY_LIMIT:
        raise HTTPException(
            status_code=429,
            detail=f"今日免费对话次数已用完（{FREE_DAILY_LIMIT}次/天），升级会员可解锁无限对话"
        )

    if not session_id:
        session_id = str(uuid.uuid4())

    # Get profile summary
    result = await db.execute(select(UserProfile).where(UserProfile.user_id == user.id))
    profile = result.scalar_one_or_none()
    profile_summary = ""
    if profile and profile.basic_info:
        b = profile.basic_info
        profile_summary = f"分数: {b.get('score', '未知')}, 位次: {b.get('rank', '未知')}, 省份: {b.get('province', '未知')}, 科类: {b.get('subject_type', '未知')}"

    # Get latest recommendation
    rec_result = await db.execute(
        select(Recommendation).where(Recommendation.user_id == user.id)
        .order_by(Recommendation.created_at.desc()).limit(1)
    )
    rec = rec_result.scalar_one_or_none()
    recommendation_summary = str(rec.result) if rec else ""

    # Get chat history
    history_result = await db.execute(
        select(ChatMessage).where(ChatMessage.user_id == user.id, ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at.desc()).limit(10)
    )
    history = list(reversed(history_result.scalars().all()))
    messages = [{"role": m.role, "content": m.content} for m in history]
    messages.append({"role": "user", "content": message})

    # Save user message
    user_msg = ChatMessage(
        id=uuid.uuid4(), user_id=user.id, session_id=session_id,
        role="user", content=message,
    )
    db.add(user_msg)

    # Call LLM
    llm = LLMService("qwen")
    reply = await llm.chat(messages, profile_summary, recommendation_summary)

    # Save AI reply
    ai_msg = ChatMessage(
        id=uuid.uuid4(), user_id=user.id, session_id=session_id,
        role="assistant", content=reply,
    )
    db.add(ai_msg)

    user.daily_chat_count += 1
    await db.flush()

    return {"session_id": session_id, "reply": reply}


@router.post("/stream")
async def chat_stream(
    message: str,
    session_id: str | None = None,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not session_id:
        session_id = str(uuid.uuid4())
    llm = LLMService()

    async def generate():
        async for chunk in llm.chat_stream([{"role": "user", "content": message}]):
            yield f"data: {chunk}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")
