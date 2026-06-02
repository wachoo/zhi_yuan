import uuid

from app.config import get_settings
from app.models.user import User
from app.dao.message import MessageDAO
from app.services.llm_service import LLMService
from app.services.user_service import UserService
from app.services.recommend_service import RecommendService

settings = get_settings()


class ChatService:
    """封装对话相关业务逻辑：画像、推荐、历史、消息持久化、LLM 调用。"""

    def __init__(
        self,
        user: User,
        session_id: str | None = None,
        skill_id: str = "default",
        user_svc: UserService | None = None,
        rec_svc: RecommendService | None = None,
        msg_dao: MessageDAO | None = None,
        llm: LLMService | None = None,
        llm_provider: str | None = None,
    ):
        self.user = user
        self.session_id = session_id or str(uuid.uuid4())
        self.skill_id = skill_id
        self.user_svc = user_svc or UserService()
        self.rec_svc = rec_svc or RecommendService()
        self.msg_dao = msg_dao or MessageDAO()
        self.llm = llm or LLMService(llm_provider or settings.LLM_CHAT_PROVIDER, user_id=user.id)

    @staticmethod
    async def list_sessions(user_id: uuid.UUID) -> list[dict]:
        """获取用户的所有会话列表"""
        return await MessageDAO().list_sessions(user_id)

    @staticmethod
    async def get_session_messages(user_id: uuid.UUID, session_id: str) -> list:
        """获取指定会话的消息列表"""
        return await MessageDAO().get_session_messages(user_id, session_id)

    @staticmethod
    async def rename_session(user_id: uuid.UUID, session_id: str, new_title: str) -> bool:
        """重命名会话标题"""
        return await MessageDAO().rename_session(user_id, session_id, new_title)

    async def _gather_context(self) -> tuple[str, str]:
        profile_summary = await self.user_svc.get_profile_summary(self.user.id)
        recommendation_summary = await self.rec_svc.get_latest_recommendation_summary(self.user.id)
        return profile_summary, recommendation_summary

    async def _build_messages(self, message: str) -> list[dict]:
        history_msgs = await self.msg_dao.get_chat_history(self.user.id, self.session_id)
        history = [{"role": m.role, "content": m.content} for m in history_msgs]
        return history + [{"role": "user", "content": message}]

    async def _resolve_skill_id(self):
        """如果会话已有 skill_id，使用会话的（覆盖客户端传入值）"""
        if self.session_id:
            session_skill = await self.msg_dao.get_session_skill_id(self.user.id, self.session_id)
            if session_skill:
                self.skill_id = session_skill

    async def _ensure_session(self):
        """确保 ChatSession 记录存在并写入 skill_id"""
        await self.msg_dao.ensure_session(self.user.id, self.session_id, self.skill_id)

    async def chat(self, message: str) -> dict:
        await self._resolve_skill_id()
        await self._ensure_session()
        await self.user_svc.update_daily_chat(self.user, self.session_id)

        profile_summary, recommendation_summary = await self._gather_context()
        messages = await self._build_messages(message)

        await self.msg_dao.save_message(self.user.id, self.session_id, "user", message)

        reply = await self.llm.chat(messages, profile_summary, recommendation_summary, self.skill_id)

        await self.msg_dao.save_message(self.user.id, self.session_id, "assistant", reply, self.skill_id)

        return {"session_id": self.session_id, "reply": reply}

    async def chat_stream(self, message: str):
        # skill_id 已由 API 层在流开始前解析完毕，此处直接执行业务逻辑
        await self.user_svc.update_daily_chat(self.user, self.session_id)

        profile_summary, recommendation_summary = await self._gather_context()
        messages = await self._build_messages(message)

        await self.msg_dao.save_message(self.user.id, self.session_id, "user", message)

        full_reply = []
        async for chunk in self.llm.chat_stream(messages, profile_summary, recommendation_summary, self.skill_id, max_tool_rounds=80):
            full_reply.append(chunk)
            yield chunk

        await self.msg_dao.save_message(self.user.id, self.session_id, "assistant", "".join(full_reply), self.skill_id)