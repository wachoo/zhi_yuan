import uuid

from app.models.user import User
from app.dao.message import MessageDAO
from app.services.llm_service import LLMService
from app.services.user_service import UserService
from app.services.recommend_service import RecommendService


class ChatService:
    """封装对话相关业务逻辑：画像、推荐、历史、消息持久化、LLM 调用。"""

    def __init__(self, user: User, session_id: str | None = None):
        self.user = user
        self.session_id = session_id or str(uuid.uuid4())

    async def chat(self, message: str) -> dict:
        """普通对话：限流 → 采集上下文 → 保存用户消息 → 调 LLM → 保存回复。"""
        user_svc = UserService()
        await user_svc.update_daily_chat(self.user, self.session_id)

        rec_svc = RecommendService()
        msg_dao = MessageDAO()

        profile_summary = await user_svc.get_profile_summary(self.user.id)
        recommendation_summary = await rec_svc.get_latest_recommendation_summary(self.user.id)
        history_msgs = await msg_dao.get_chat_history(self.user.id, self.session_id)
        history = [{"role": m.role, "content": m.content} for m in history_msgs]
        messages = history + [{"role": "user", "content": message}]

        await msg_dao.save_message(self.user.id, self.session_id, "user", message)

        llm = LLMService("qwen")
        reply = await llm.chat(messages, profile_summary, recommendation_summary)

        await msg_dao.save_message(self.user.id, self.session_id, "assistant", reply)

        return {"session_id": self.session_id, "reply": reply}

    async def chat_stream(self, message: str):
        """流式对话：采集上下文 → 调 LLM 流式输出。"""
        user_svc = UserService()
        rec_svc = RecommendService()

        profile_summary = await user_svc.get_profile_summary(self.user.id)
        recommendation_summary = await rec_svc.get_latest_recommendation_summary(self.user.id)
        messages = [{"role": "user", "content": message}]

        llm = LLMService("qwen")
        async for chunk in llm.chat_stream(messages, profile_summary, recommendation_summary):
            yield chunk
