import uuid
from datetime import datetime

from fastapi import HTTPException

from app.dao.profile import ProfileDAO
from app.models.user import UserProfile


class ProfileService:
    """用户画像业务逻辑：查询、更新"""

    @staticmethod
    def _calc_completeness(profile: UserProfile) -> float:
        filled = 0
        if profile.basic_info:
            filled += 1
        if profile.family_info:
            filled += 1
        if profile.personality:
            filled += 1
        if profile.ability:
            filled += 1
        if profile.values_info:
            filled += 1
        return filled / 5

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
