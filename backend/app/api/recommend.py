from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.recommendation import RecommendRequest, RecommendResult
from app.services.recommend_service import RecommendService

router = APIRouter(prefix="/api/recommend", tags=["推荐"])


@router.post("", response_model=RecommendResult)
async def get_recommendation(
    request: RecommendRequest,
    user: User = Depends(get_current_user),
):
    return await RecommendService().get_recommendation(user, request)
