from app.dao.university import UniversityDAO


class UniversityService:
    """院校查询业务逻辑"""

    async def search_universities(self, name: str, province: str | None = None) -> dict:
        """搜索院校并格式化为工具返回结构（供 LLM 使用）"""
        rows = await UniversityDAO().search_by_name(name, province)
        if not rows:
            return {"message": f"未找到包含「{name}」的院校"}

        return {
            "universities": [
                {
                    "name": u.name,
                    "province": u.province,
                    "city": u.city,
                    "level": u.level,
                    "type": u.type,
                    "tags": u.tags,
                    "tuition": f"{u.tuition_min}-{u.tuition_max}" if u.tuition_min else None,
                    "website": u.website,
                    "description": u.description,
                }
                for u in rows
            ]
        }

    async def list_universities(
        self,
        province: str | None = None,
        level: str | None = None,
        type: str | None = None,
        keyword: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> list:
        """按条件筛选并分页查询院校"""
        offset = (page - 1) * page_size
        return await UniversityDAO().list_with_filters(
            province=province, level=level, type=type,
            keyword=keyword, offset=offset, limit=page_size,
        )

    async def get_university(self, university_id: str):
        """按 ID 查询单个院校"""
        from fastapi import HTTPException
        uni = await UniversityDAO().get_by_id(university_id)
        if not uni:
            raise HTTPException(status_code=404, detail="院校不存在")
        return uni
