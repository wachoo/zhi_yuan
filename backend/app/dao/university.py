from sqlalchemy import select

from app.models.university import University
from app.database import async_session


class UniversityDAO:

    async def search_by_name(
        self, name: str, province: str | None = None, limit: int = 5
    ) -> list[University]:
        """按名称模糊搜索院校，可选按省份筛选"""
        async with async_session() as db:
            stmt = select(University).where(University.name.contains(name))
            if province:
                stmt = stmt.where(University.province == province)
            stmt = stmt.limit(limit)
            result = await db.execute(stmt)
            return list(result.scalars().all())

    async def list_with_filters(
        self,
        province: str | None = None,
        level: str | None = None,
        type: str | None = None,
        keyword: str | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> list[University]:
        """按条件筛选并分页查询院校列表"""
        async with async_session() as db:
            stmt = select(University)
            if province:
                stmt = stmt.where(University.province == province)
            if level:
                stmt = stmt.where(University.level == level)
            if type:
                stmt = stmt.where(University.type == type)
            if keyword:
                stmt = stmt.where(University.name.ilike(f"%{keyword}%"))
            stmt = stmt.offset(offset).limit(limit)
            result = await db.execute(stmt)
            return list(result.scalars().all())

    async def get_by_id(self, university_id: str) -> University | None:
        """按 ID 查询单个院校"""
        async with async_session() as db:
            result = await db.execute(
                select(University).where(University.id == university_id)
            )
            return result.scalar_one_or_none()
