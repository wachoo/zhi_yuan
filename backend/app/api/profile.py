from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.user import ProfileUpdate
from app.services.profile_service import ProfileService

router = APIRouter(prefix="/api/profile", tags=["用户画像"])


@router.get("")
async def get_profile(user: User = Depends(get_current_user)):
    return await ProfileService().get_profile(user.id)


@router.put("")
async def update_profile(
    data: ProfileUpdate,
    user: User = Depends(get_current_user),
):
    return await ProfileService().update_profile(user.id, data)
