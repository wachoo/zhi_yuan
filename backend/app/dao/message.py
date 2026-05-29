import uuid

from sqlalchemy import select, func

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

    async def list_sessions(self, user_id: uuid.UUID) -> list[dict]:
        """按 session_id 分组，返回每个会话的摘要信息（按最后消息时间倒序）"""
        async with async_session() as db:
            # 子查询：获取每个 session 的首条用户消息 content 作为标题
            first_msg = (
                select(
                    ChatMessage.session_id,
                    func.min(ChatMessage.created_at).label("first_at"),
                )
                .where(
                    ChatMessage.user_id == user_id,
                    ChatMessage.role == "user",
                )
                .group_by(ChatMessage.session_id)
                .subquery()
            )

            # 主查询：按 session 聚合
            result = await db.execute(
                select(
                    ChatMessage.session_id,
                    func.count(ChatMessage.id).label("message_count"),
                    func.max(ChatMessage.created_at).label("last_message_at"),
                )
                .where(ChatMessage.user_id == user_id)
                .group_by(ChatMessage.session_id)
                .order_by(func.max(ChatMessage.created_at).desc())
            )
            sessions = result.all()

            # 获取每个会话的首条用户消息作为标题
            titles = {}
            for row in sessions:
                title_result = await db.execute(
                    select(ChatMessage.content)
                    .where(
                        ChatMessage.user_id == user_id,
                        ChatMessage.session_id == row.session_id,
                        ChatMessage.role == "user",
                    )
                    .order_by(ChatMessage.created_at.asc())
                    .limit(1)
                )
                first_content = title_result.scalar()
                titles[row.session_id] = (first_content or "新对话")[:30]

            return [
                {
                    "session_id": row.session_id,
                    "title": titles.get(row.session_id, "新对话"),
                    "message_count": row.message_count,
                    "last_message_at": row.last_message_at,
                }
                for row in sessions
            ]

    async def get_session_messages(
        self, user_id: uuid.UUID, session_id: str, limit: int = 100
    ) -> list[ChatMessage]:
        """获取指定会话的所有消息（按时间正序）"""
        async with async_session() as db:
            result = await db.execute(
                select(ChatMessage)
                .where(
                    ChatMessage.user_id == user_id,
                    ChatMessage.session_id == session_id,
                )
                .order_by(ChatMessage.created_at.asc())
                .limit(limit)
            )
            return list(result.scalars().all())
