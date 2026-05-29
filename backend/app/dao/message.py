import uuid

from sqlalchemy import select

from app.models.recommendation import ChatMessage
from app.database import async_session


class MessageDAO:

    async def get_chat_history(
        self, user_id: uuid.UUID, session_id: str, limit: int = 10
    ) -> list[ChatMessage]:
        """获取指定会话的聊天历史（按时间正序返回）"""
        async with async_session() as db:
            result = await db.execute(
                select(ChatMessage)
                .where(
                    ChatMessage.user_id == user_id,
                    ChatMessage.session_id == session_id,
                )
                .order_by(ChatMessage.created_at.desc())
                .limit(limit)
            )
            return list(reversed(result.scalars().all()))

    async def save_message(
        self,
        user_id: uuid.UUID,
        session_id: str,
        role: str,
        content: str,
    ) -> ChatMessage:
        """创建并持久化一条聊天消息"""
        msg = ChatMessage(
            id=uuid.uuid4(),
            user_id=user_id,
            session_id=session_id,
            role=role,
            content=content,
        )
        async with async_session() as db:
            db.add(msg)
            await db.commit()
            await db.refresh(msg)
            return msg
