from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.university import University
from app.schemas.university import UniversityOut

router = APIRouter(prefix="/api/universities", tags=["院校"])


@router.get("", response_model=list[UniversityOut])
async def list_universities(
    province: str | None = None,
    level: str | None = None,
    type: str | None = None,
    keyword: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    query = select(University)
    if province:
        query = query.where(University.province == province)
    if level:
        query = query.where(University.level == level)
    if type:
        query = query.where(University.type == type)
    if keyword:
        query = query.where(University.name.ilike(f"%{keyword}%"))
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{university_id}", response_model=UniversityOut)
async def get_university(university_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(University).where(University.id == university_id))
    uni = result.scalar_one_or_none()
    if not uni:
        raise HTTPException(status_code=404, detail="院校不存在")
    return uni
