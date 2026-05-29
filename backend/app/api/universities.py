from fastapi import APIRouter, Query

from app.schemas.university import UniversityOut
from app.services.university_service import UniversityService

router = APIRouter(prefix="/api/universities", tags=["院校"])


@router.get("", response_model=list[UniversityOut])
async def list_universities(
    province: str | None = None,
    level: str | None = None,
    type: str | None = None,
    keyword: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
):
    return await UniversityService().list_universities(
        province=province, level=level, type=type,
        keyword=keyword, page=page, page_size=page_size,
    )


@router.get("/{university_id}", response_model=UniversityOut)
async def get_university(university_id: str):
    return await UniversityService().get_university(university_id)
