from sqlalchemy import select

from app.models.major import Major
from app.database import async_session


class MajorDAO:

    async def search_by_name(self, name: str, limit: int = 5) -> list[Major]:
        """按名称模糊搜索专业"""
        async with async_session() as db:
            result = await db.execute(
                select(Major).where(Major.name.contains(name)).limit(limit)
            )
            return list(result.scalars().all())

    async def get_all_names(self) -> list[str]:
        """获取所有专业名称"""
        async with async_session() as db:
            result = await db.execute(select(Major.name))
            return [row[0] for row in result.all()]
