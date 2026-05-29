from app.dao.major import MajorDAO


class MajorService:
    """专业查询业务逻辑"""

    async def search_majors(self, name: str) -> dict:
        """搜索专业并格式化为工具返回结构"""
        rows = await MajorDAO().search_by_name(name)
        if not rows:
            return {"message": f"未找到包含「{name}」的专业"}

        return {
            "majors": [
                {
                    "name": m.name,
                    "category": m.category,
                    "degree": m.degree,
                    "duration": m.duration,
                    "description": m.description,
                    "courses": m.courses,
                    "career_directions": m.career_directions,
                    "avg_salary": m.avg_salary,
                }
                for m in rows
            ]
        }
