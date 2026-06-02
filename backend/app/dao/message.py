import uuid

from sqlalchemy import select, func, delete

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
        skill_id: str | None = None,
    ) -> ChatMessage:
        """创建并持久化一条聊天消息"""
        msg = ChatMessage(
            id=uuid.uuid4(),
            user_id=user_id,
            session_id=session_id,
            role=role,
            content=content,
            skill_id=skill_id,
        )
        async with async_session() as db:
            db.add(msg)
            await db.commit()
            await db.refresh(msg)
            return msg

    async def list_sessions(self, user_id: uuid.UUID) -> list[dict]:
        """按 session_id 分组，返回每个会话的摘要信息（按最后消息时间倒序）"""
        async with async_session() as db:
            # 主查询：按 session 聚合，LEFT JOIN chat_sessions 获取 skill_id
            result = await db.execute(
                select(
                    ChatMessage.session_id,
                    func.count(ChatMessage.id).label("message_count"),
                    func.max(ChatMessage.created_at).label("last_message_at"),
                    ChatSession.custom_title,
                    ChatSession.skill_id,
                )
                .outerjoin(
                    ChatSession,
                    (ChatSession.session_id == ChatMessage.session_id) & (ChatSession.user_id == ChatMessage.user_id),
                )
                .where(ChatMessage.user_id == user_id)
                .group_by(ChatMessage.session_id, ChatSession.custom_title, ChatSession.skill_id)
                .order_by(func.max(ChatMessage.created_at).desc())
            )
            sessions = result.all()

            # 获取每个会话的标题：优先 chat_sessions.custom_title，其次首条用户消息
            titles = {}
            for row in sessions:
                if row.custom_title:
                    titles[row.session_id] = row.custom_title
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
                    "skill_id": row.skill_id,
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

    async def get_session_skill_id(self, user_id: uuid.UUID, session_id: str) -> str | None:
        """获取会话的 skill_id（如果 ChatSession 记录存在）"""
        async with async_session() as db:
            result = await db.execute(
                select(ChatSession.skill_id).where(
                    ChatSession.user_id == user_id,
                    ChatSession.session_id == session_id,
                )
            )
            return result.scalar()

    async def ensure_session(self, user_id: uuid.UUID, session_id: str, skill_id: str | None = None):
        """确保 ChatSession 记录存在，首次设置 skill_id"""
        async with async_session() as db:
            result = await db.execute(
                select(ChatSession).where(
                    ChatSession.user_id == user_id,
                    ChatSession.session_id == session_id,
                )
            )
            session = result.scalar_one_or_none()
            if session:
                # 已有记录但 skill_id 为空时补填
                if session.skill_id is None and skill_id:
                    session.skill_id = skill_id
            else:
                session = ChatSession(
                    id=uuid.uuid4(),
                    user_id=user_id,
                    session_id=session_id,
                    skill_id=skill_id,
                )
                db.add(session)
            await db.commit()

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

    async def delete_qa_pair(
        self, user_id: uuid.UUID, session_id: str, message_id: uuid.UUID
    ) -> bool:
        """删除一个 QA 对（用户问题 + 中间所有消息 + AI 回复），并清理空会话"""
        async with async_session() as db:
            # 1. 查找用户消息
            result = await db.execute(
                select(ChatMessage).where(
                    ChatMessage.id == message_id,
                    ChatMessage.user_id == user_id,
                    ChatMessage.session_id == session_id,
                    ChatMessage.role == "user",
                )
            )
            user_msg = result.scalar_one_or_none()
            if not user_msg:
                return False

            # 2. 查找下一条 user 消息的时间边界
            next_user_result = await db.execute(
                select(ChatMessage.created_at).where(
                    ChatMessage.user_id == user_id,
                    ChatMessage.session_id == session_id,
                    ChatMessage.role == "user",
                    ChatMessage.created_at > user_msg.created_at,
                ).order_by(ChatMessage.created_at.asc()).limit(1)
            )
            next_user_time = next_user_result.scalar()

            # 3. 查找该 QA 对的所有消息（从 user_msg 到 next_user_time 之间）
            if next_user_time:
                qa_messages_result = await db.execute(
                    select(ChatMessage).where(
                        ChatMessage.user_id == user_id,
                        ChatMessage.session_id == session_id,
                        ChatMessage.created_at >= user_msg.created_at,
                        ChatMessage.created_at < next_user_time,
                    )
                )
            else:
                # 没有后续 user 消息，删除从 user_msg 开始的所有消息
                qa_messages_result = await db.execute(
                    select(ChatMessage).where(
                        ChatMessage.user_id == user_id,
                        ChatMessage.session_id == session_id,
                        ChatMessage.created_at >= user_msg.created_at,
                    )
                )

            qa_messages = qa_messages_result.scalars().all()

            # 4. 删除所有 QA 相关消息（user + tool + system + assistant）
            for msg in qa_messages:
                await db.delete(msg)

            await db.commit()

            # 5. 检查会话是否为空，如果为空则删除 chat_sessions 记录
            remaining_result = await db.execute(
                select(func.count(ChatMessage.id)).where(
                    ChatMessage.user_id == user_id,
                    ChatMessage.session_id == session_id,
                )
            )
            remaining_count = remaining_result.scalar()

            if remaining_count == 0:
                # 删除 chat_sessions 表中的记录
                await db.execute(
                    delete(ChatSession).where(
                        ChatSession.user_id == user_id,
                        ChatSession.session_id == session_id,
                    )
                )
                await db.commit()

            return True

    async def delete_session(
        self, user_id: uuid.UUID, session_id: str
    ) -> bool:
        """删除整个会话：所有 chat_messages + chat_sessions 记录"""
        async with async_session() as db:
            # 验证该 session 属于该用户（检查 chat_messages 或 chat_sessions）
            msg_result = await db.execute(
                select(ChatMessage.id).where(
                    ChatMessage.user_id == user_id,
                    ChatMessage.session_id == session_id,
                ).limit(1)
            )
            session_result = await db.execute(
                select(ChatSession).where(
                    ChatSession.user_id == user_id,
                    ChatSession.session_id == session_id,
                )
            )
            if not msg_result.scalar_one_or_none() and not session_result.scalar_one_or_none():
                return False

            # 删除所有 chat_messages
            await db.execute(
                delete(ChatMessage).where(
                    ChatMessage.user_id == user_id,
                    ChatMessage.session_id == session_id,
                )
            )

            # 删除 chat_sessions 记录
            await db.execute(
                delete(ChatSession).where(
                    ChatSession.user_id == user_id,
                    ChatSession.session_id == session_id,
                )
            )

            await db.commit()
            return True

