import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.api.deps import get_current_user
from app.models.user import User, UserProfile
from app.schemas.user import ProfileUpdate

router = APIRouter(prefix="/api/profile", tags=["用户画像"])


def _calc_completeness(profile: UserProfile) -> float:
    filled = 0
    total = 5
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
    return filled / total


@router.get("")
async def get_profile(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(UserProfile).where(UserProfile.user_id == user.id))
    profile = result.scalar_one_or_none()
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


@router.put("")
async def update_profile(
    data: ProfileUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(UserProfile).where(UserProfile.user_id == user.id))
    profile = result.scalar_one_or_none()
    if not profile:
        profile = UserProfile(id=uuid.uuid4(), user_id=user.id)
        db.add(profile)

    if data.basic_info is not None:
        profile.basic_info = data.basic_info.model_dump(exclude_none=True)
    if data.family_info is not None:
        profile.family_info = data.family_info.model_dump(exclude_none=True)
    if data.personality is not None:
        profile.personality = data.personality.model_dump(exclude_none=True)
    if data.ability is not None:
        profile.ability = data.ability.model_dump(exclude_none=True)
    if data.values_info is not None:
        profile.values_info = data.values_info.model_dump(exclude_none=True)

    profile.completeness = _calc_completeness(profile)
    profile.updated_at = datetime.utcnow()

    await db.flush()
    return {"completeness": profile.completeness, "message": "画像已更新"}
