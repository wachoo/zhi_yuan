import uuid
from datetime import datetime

from sqlalchemy import select

from app.models.user import UserProfile
from app.database import async_session


class ProfileDAO:

    async def get_by_user_id(self, user_id: uuid.UUID) -> UserProfile | None:
        async with async_session() as db:
            result = await db.execute(
                select(UserProfile).where(UserProfile.user_id == user_id)
            )
            return result.scalar_one_or_none()

    async def create_profile(self, profile: UserProfile) -> UserProfile:
        async with async_session() as db:
            db.add(profile)
            await db.commit()
            await db.refresh(profile)
            return profile

    async def update_fields(self, profile: UserProfile, completeness: float, **fields) -> UserProfile:
        """更新画像字段并设置完整度"""
        async with async_session() as db:
            result = await db.execute(
                select(UserProfile).where(UserProfile.id == profile.id)
            )
            db_profile = result.scalar_one()
            for key, value in fields.items():
                if value is not None:
                    setattr(db_profile, key, value)
            db_profile.completeness = completeness
            db_profile.updated_at = datetime.utcnow()
            await db.commit()
            await db.refresh(db_profile)
            return db_profile
