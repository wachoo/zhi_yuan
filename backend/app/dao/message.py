import uuid

from sqlalchemy import select, func

from app.models.recommendation import ChatMessage
from app.models.chat_session import ChatSession
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

            # 获取每个会话的标题：优先 chat_sessions.custom_title，其次首条用户消息
            titles = {}
            for row in sessions:
                # 先查 chat_sessions 的 custom_title
                session_result = await db.execute(
                    select(ChatSession.custom_title).where(
                        ChatSession.user_id == user_id,
                        ChatSession.session_id == row.session_id,
                    )
                )
                custom_title = session_result.scalar()
                if custom_title:
                    titles[row.session_id] = custom_title
                else:
                    # 回退到首条用户消息
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

    async def rename_session(
        self, user_id: uuid.UUID, session_id: str, new_title: str
    ) -> bool:
        """重命名会话标题，返回是否成功"""
        async with async_session() as db:
            # 验证 session 属于该用户
            result = await db.execute(
                select(ChatMessage).where(
                    ChatMessage.user_id == user_id,
                    ChatMessage.session_id == session_id,
                ).limit(1)
            )
            if not result.scalar_one_or_none():
                return False

            # 查找或创建 chat_session 记录
            session_result = await db.execute(
                select(ChatSession).where(
                    ChatSession.user_id == user_id,
                    ChatSession.session_id == session_id,
                )
            )
            session = session_result.scalar_one_or_none()

            if session:
                session.custom_title = new_title
            else:
                session = ChatSession(
                    id=uuid.uuid4(),
                    user_id=user_id,
                    session_id=session_id,
                    custom_title=new_title,
                )
                db.add(session)

            await db.commit()
            return True

