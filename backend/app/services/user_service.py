from datetime import date

from fastapi import HTTPException

from app.dao.profile import ProfileDAO
from app.dao.user import UserDAO

FREE_DAILY_LIMIT = 3


class UserService:
    """用户相关业务逻辑"""

    async def get_profile_summary(self, user_id) -> str:
        """获取用户画像摘要（供 LLM 上下文使用）"""
        profile = await ProfileDAO().get_by_user_id(user_id)
        if not profile or not profile.basic_info:
            return ""
        b = profile.basic_info
        return (
            f"分数: {b.get('score', '未知')}, "
            f"位次: {b.get('rank', '未知')}, "
            f"省份: {b.get('province', '未知')}, "
            f"科类: {b.get('subject_type', '未知')}"
        )

    async def update_daily_chat(self, user, session_id: str, free_daily_limit: int = FREE_DAILY_LIMIT):
        """限流检查 + 持久化每日对话计数"""
        today = date.today().isoformat()

        if getattr(user, "membership_tier", "free") == "free":
            current = getattr(user, "daily_chat_count", 0)
            last_date = getattr(user, "last_chat_date", None)
            if last_date == today and current >= free_daily_limit:
                raise HTTPException(
                    status_code=429,
                    detail=f"今日免费对话次数已用完（{free_daily_limit}次/天），升级会员可解锁无限对话",
                )

        await UserDAO().update_daily_chat(user.id, session_id)
