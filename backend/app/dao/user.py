import uuid
from datetime import date, datetime

from sqlalchemy import select

from app.models.user import User
from app.database import async_session


class UserDAO:

    async def get_by_id(self, user_id: uuid.UUID) -> User | None:
        async with async_session() as db:
            result = await db.execute(select(User).where(User.id == user_id))
            return result.scalar_one_or_none()

    async def get_by_phone(self, phone: str) -> User | None:
        async with async_session() as db:
            result = await db.execute(select(User).where(User.phone == phone))
            return result.scalar_one_or_none()

    async def create_user(self, user: User) -> User:
        async with async_session() as db:
            db.add(user)
            await db.commit()
            await db.refresh(user)
            return user

    async def update_password(self, user_id: uuid.UUID, new_hash: str):
        """更新用户密码"""
        async with async_session() as db:
            result = await db.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()
            if not user:
                return
            user.password_hash = new_hash
            await db.commit()

    async def update_daily_chat(self, user_id: uuid.UUID, session_id: str):
        """重置/递增每日对话计数"""
        today = date.today().isoformat()
        async with async_session() as db:
            result = await db.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()
            if not user:
                return
            if user.last_chat_date != today:
                user.daily_chat_count = 1
                user.last_chat_date = today
            else:
                user.daily_chat_count += 1
            await db.commit()

    async def update_membership(self, user_id: uuid.UUID, tier: str, expires_at: datetime):
        """更新用户会员等级和到期时间"""
        async with async_session() as db:
            result = await db.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()
            if not user:
                return
            user.membership_tier = tier
            user.membership_expires_at = expires_at
            await db.commit()
