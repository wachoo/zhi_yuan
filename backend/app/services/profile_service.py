import uuid

from fastapi import HTTPException

from app.dao.profile import ProfileDAO
from app.models.user import UserProfile


class ProfileService:
    """用户画像业务逻辑：查询、更新"""

    # 各维度权重（与 AdapterScorer 对齐）
    DIMENSION_WEIGHTS = {
        "basic_info": 0.30,
        "family_info": 0.15,
        "personality": 0.25,
        "ability": 0.15,
        "values_info": 0.15,
    }

    # 各维度内的字段定义
    DIMENSION_FIELDS = {
        "basic_info": ["score", "rank", "province", "subject_type", "exam_type"],
        "family_info": [
            "income_range", "tuition_max", "prefer_city", "parent_industry",
            "parent_education", "hukou_type", "has_siblings", "has_elderly_care",
            "home_province", "home_city", "home_district",
        ],
        "personality": ["interests", "dislikes", "holland_code", "mbti", "introvert_extrovert"],
        "ability": ["strong_subjects", "social_ability", "english_level", "awards"],
        "values_info": ["career_values", "distance_preference", "plan", "industry_preference"],
    }

    @staticmethod
    def _is_field_filled(value) -> bool:
        """判断字段是否有效填充"""
        if value is None:
            return False
        if isinstance(value, (list, str)) and len(value) == 0:
            return False
        return True

    @classmethod
    def _calc_completeness(cls, profile: UserProfile) -> float:
        """计算画像完整度：按字段粒度加权求和"""
        total_score = 0.0

        for dim_name, weight in cls.DIMENSION_WEIGHTS.items():
            dim_data = getattr(profile, dim_name, None)
            if not dim_data:
                continue

            fields = cls.DIMENSION_FIELDS.get(dim_name, [])
            if not fields:
                continue

            filled_count = sum(
                1 for field in fields
                if cls._is_field_filled(dim_data.get(field))
            )
            # 维度内填充率 × 维度权重
            dim_score = (filled_count / len(fields)) * weight
            total_score += dim_score

        return round(total_score, 3)

    async def get_profile(self, user_id: uuid.UUID) -> dict:
        profile = await ProfileDAO().get_by_user_id(user_id)
        if not profile:
            raise HTTPException(status_code=404, detail="画像不存在")
        return {
            "basic_info": profile.basic_info,
            "family_info": profile.family_info,
            "personality": profile.personality,
            "ability": profile.ability,
            "values_info": profile.values_info,
            "completeness": profile.completeness,
        }

    async def update_profile(self, user_id: uuid.UUID, data) -> dict:
        dao = ProfileDAO()
        profile = await dao.get_by_user_id(user_id)
        if not profile:
            profile = UserProfile(id=uuid.uuid4(), user_id=user_id)
            await dao.create_profile(profile)

        updates = {}
        if data.basic_info is not None:
            updates["basic_info"] = data.basic_info.model_dump(exclude_none=True)
        if data.family_info is not None:
            updates["family_info"] = data.family_info.model_dump(exclude_none=True)
        if data.personality is not None:
            updates["personality"] = data.personality.model_dump(exclude_none=True)
        if data.ability is not None:
            updates["ability"] = data.ability.model_dump(exclude_none=True)
        if data.values_info is not None:
            updates["values_info"] = data.values_info.model_dump(exclude_none=True)

        # 计算完整度（基于内存中的 profile 对象预览）
        for key, value in updates.items():
            setattr(profile, key, value)
        completeness = self._calc_completeness(profile)

        await dao.update_fields(profile, completeness, **updates)
        return {"completeness": completeness, "message": "画像已更新"}
