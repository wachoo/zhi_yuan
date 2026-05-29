import uuid

from app.models.user import User
from app.dao.message import MessageDAO
from app.services.llm_service import LLMService
from app.services.user_service import UserService
from app.services.recommend_service import RecommendService


class ChatService:
    """封装对话相关业务逻辑：画像、推荐、历史、消息持久化、LLM 调用。"""

    def __init__(
        self,
        user: User,
        session_id: str | None = None,
        user_svc: UserService | None = None,
        rec_svc: RecommendService | None = None,
        msg_dao: MessageDAO | None = None,
        llm: LLMService | None = None,
        llm_provider: str = "qwen",
    ):
        self.user = user
        self.session_id = session_id or str(uuid.uuid4())
        self.user_svc = user_svc or UserService()
        self.rec_svc = rec_svc or RecommendService()
        self.msg_dao = msg_dao or MessageDAO()
        self.llm = llm or LLMService(llm_provider, user_id=user.id)

    @staticmethod
    async def list_sessions(user_id: uuid.UUID) -> list[dict]:
        """获取用户的所有会话列表"""
        return await MessageDAO().list_sessions(user_id)

    @staticmethod
    async def get_session_messages(user_id: uuid.UUID, session_id: str) -> list:
        """获取指定会话的消息列表"""
        return await MessageDAO().get_session_messages(user_id, session_id)

    async def _gather_context(self) -> tuple[str, str]:
        profile_summary = await self.user_svc.get_profile_summary(self.user.id)
        recommendation_summary = await self.rec_svc.get_latest_recommendation_summary(self.user.id)
        return profile_summary, recommendation_summary

    async def _build_messages(self, message: str) -> list[dict]:
        history_msgs = await self.msg_dao.get_chat_history(self.user.id, self.session_id)
        history = [{"role": m.role, "content": m.content} for m in history_msgs]
        return history + [{"role": "user", "content": message}]

    async def chat(self, message: str) -> dict:
        await self.user_svc.update_daily_chat(self.user, self.session_id)

        profile_summary, recommendation_summary = await self._gather_context()
        messages = await self._build_messages(message)

        await self.msg_dao.save_message(self.user.id, self.session_id, "user", message)

        reply = await self.llm.chat(messages, profile_summary, recommendation_summary)

        await self.msg_dao.save_message(self.user.id, self.session_id, "assistant", reply)

        return {"session_id": self.session_id, "reply": reply}

    async def chat_stream(self, message: str):
        await self.user_svc.update_daily_chat(self.user, self.session_id)

        profile_summary, recommendation_summary = await self._gather_context()
        messages = await self._build_messages(message)

        await self.msg_dao.save_message(self.user.id, self.session_id, "user", message)

        full_reply = []
        async for chunk in self.llm.chat_stream(messages, profile_summary, recommendation_summary):
            full_reply.append(chunk)
            yield chunk

        await self.msg_dao.save_message(self.user.id, self.session_id, "assistant", "".join(full_reply))