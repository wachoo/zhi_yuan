from datetime import datetime
from urllib.parse import quote

from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.responses import StreamingResponse
import io

from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.recommendation import RecommendRequest, RecommendResult
from app.services.recommend_service import RecommendService
from app.services.export_service import ExportService
from app.dao.recommend import RecommendDAO

router = APIRouter(prefix="/api/recommend", tags=["推荐"])


@router.post("", response_model=RecommendResult)
async def get_recommendation(
    request: RecommendRequest,
    user: User = Depends(get_current_user),
):
    return await RecommendService().get_recommendation(user, request)


@router.get("/export")
async def export_recommendation(
    user: User = Depends(get_current_user),
):
    """Export the latest recommendation result as Excel file"""
    # Fetch latest recommendation from database (same data as shown on page)
    rec = await RecommendDAO().get_latest_by_user(user.id)
    if not rec:
        raise HTTPException(status_code=404, detail="暂无推荐记录，请先生成推荐方案")

    # Generate Excel from stored data
    excel_bytes = ExportService().export_recommendation(
        result=rec.result,
        input_snapshot=rec.input_snapshot,
    )

    # Return as file download
    date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"志愿推荐方案_{date_str}.xlsx"
    encoded_filename = quote(filename)

    return StreamingResponse(
        io.BytesIO(excel_bytes),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"
        },
    )
