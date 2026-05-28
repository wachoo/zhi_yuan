import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.api.deps import get_current_user
from app.models.user import User, UserProfile
from app.models.admission import AdmissionRecord
from app.models.university import University
from app.models.major import Major
from app.services.recommendation_engine import RecommendationEngine
from app.services.adapter_scorer import AdapterScorer
from app.schemas.recommendation import RecommendRequest, RecommendResult, RecommendItem
from app.models.recommendation import Recommendation

router = APIRouter(prefix="/api/recommend", tags=["推荐"])


@router.post("", response_model=RecommendResult)
async def get_recommendation(
    request: RecommendRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # 1. Get user profile
    result = await db.execute(select(UserProfile).where(UserProfile.user_id == user.id))
    profile = result.scalar_one_or_none()

    profile_dict = {}
    if profile:
        profile_dict = {
            "basic_info": profile.basic_info or {},
            "family_info": profile.family_info,
            "personality": profile.personality,
            "ability": profile.ability,
            "values_info": profile.values_info,
        }

    basic = profile_dict.get("basic_info", {})
    rank = request.rank or basic.get("rank", 0)
    province = request.province or basic.get("province", "")
    subject_type = request.subject_type or basic.get("subject_type", "")

    if not rank or not province or not subject_type:
        raise HTTPException(status_code=400, detail="请至少提供位次、省份和科类")

    # 2. Query admission records
    records_result = await db.execute(
        select(AdmissionRecord, University, Major)
        .join(University, AdmissionRecord.university_id == University.id)
        .outerjoin(Major, AdmissionRecord.major_id == Major.id)
        .where(AdmissionRecord.province == province)
        .where(AdmissionRecord.subject_type == subject_type)
    )

    records = []
    for admission, uni, major in records_result:
        records.append({
            "university_name": uni.name,
            "university_province": uni.province,
            "major_name": major.name if major else "未分专业",
            "min_rank": admission.min_rank,
            "year": admission.year,
            "province": admission.province,
            "subject_type": admission.subject_type,
            "tuition_min": uni.tuition_min or 0,
            "tuition_max": uni.tuition_max or 999999,
            "level": uni.level or "",
            "city": uni.city,
            "career_directions": major.career_directions if major else [],
        })

    # 3. Filter
    engine = RecommendationEngine()
    tuition_max = None
    family = profile_dict.get("family_info")
    if family:
        tuition_max = family.get("tuition_max")

    filtered = engine.filter_records(
        records=records, province=province, subject_type=subject_type, tuition_max=tuition_max,
    )

    # 4. Categorize
    categorized = engine.categorize(equivalent_rank=rank, records=filtered)

    # 5. Tier limit
    tier = user.membership_tier
    categorized = engine.limit_for_tier(categorized, tier=tier, max_per_group=1 if tier == "free" else 999)

    # 6. Score
    scorer = AdapterScorer()
    for group in ["rush", "stable", "safe"]:
        for item in categorized[group]:
            score = scorer.score(profile=profile_dict, record=item)
            item["adapter_score"] = score["total"]

    # 7. Save recommendation
    rec = Recommendation(
        id=uuid.uuid4(),
        user_id=user.id,
        input_snapshot={"rank": rank, "province": province, "subject_type": subject_type},
        result={k: [{"university_name": i["university_name"], "major_name": i["major_name"],
                      "adapter_score": i.get("adapter_score")} for i in v]
                for k, v in categorized.items()},
        tier=tier,
    )
    db.add(rec)
    await db.flush()

    # 8. Build response
    def to_items(items):
        return [RecommendItem(
            university_name=i["university_name"],
            major_name=i["major_name"],
            min_rank=i.get("min_rank"),
            rank_ratio=i.get("rank_ratio"),
            adapter_score=i.get("adapter_score"),
        ) for i in items]

    return RecommendResult(
        rush=to_items(categorized["rush"]),
        stable=to_items(categorized["stable"]),
        safe=to_items(categorized["safe"]),
        profile_completeness=profile.completeness if profile else 0.0,
    )
