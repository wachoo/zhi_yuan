import uuid

from sqlalchemy import select

from app.models.recommendation import Recommendation
from app.database import async_session


class RecommendDAO:

    async def get_latest_by_user(self, user_id: uuid.UUID) -> Recommendation | None:
        """获取用户最近一次推荐记录"""
        async with async_session() as db:
            result = await db.execute(
                select(Recommendation)
                .where(Recommendation.user_id == user_id)
                .order_by(Recommendation.created_at.desc())
                .limit(1)
            )
            return result.scalar_one_or_none()

    async def create_recommendation(self, rec: Recommendation) -> Recommendation:
        """创建推荐记录"""
        async with async_session() as db:
            db.add(rec)
            await db.commit()
            await db.refresh(rec)
            return rec
