import uuid

from fastapi import HTTPException

from app.dao.profile import ProfileDAO
from app.dao.admission import AdmissionDAO
from app.dao.recommend import RecommendDAO
from app.models.recommendation import Recommendation
from app.services.recommendation_engine import RecommendationEngine
from app.services.adapter_scorer import AdapterScorer
from app.schemas.recommendation import RecommendRequest, RecommendResult, RecommendItem


class RecommendService:
    """推荐相关业务逻辑"""

    async def get_latest_recommendation_summary(self, user_id: uuid.UUID) -> str:
        """获取用户最近一次推荐结果摘要（供 LLM 上下文使用）"""
        rec = await RecommendDAO().get_latest_by_user(user_id)
        return str(rec.result) if rec else ""

    async def get_recommendation(self, user, request: RecommendRequest) -> RecommendResult:
        """完整推荐流程：画像 → 录取数据 → 筛选 → 分类 → 评分 → 持久化"""
        # 1. 获取画像
        profile = await ProfileDAO().get_by_user_id(user.id)
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

        # 2. 查询录取数据
        raw_records = await AdmissionDAO().query_records_with_details(province, subject_type)
        records = []
        for admission, uni, major in raw_records:
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

        # 3. 筛选
        engine = RecommendationEngine()
        tuition_max = None
        family = profile_dict.get("family_info")
        if family:
            tuition_max = family.get("tuition_max")
        filtered = engine.filter_records(
            records=records, province=province, subject_type=subject_type, tuition_max=tuition_max,
        )

        # 4. 分类
        categorized = engine.categorize(equivalent_rank=rank, records=filtered)

        # 5. 会员限制
        tier = user.membership_tier
        categorized = engine.limit_for_tier(categorized, tier=tier, max_per_group=1 if tier == "free" else 999)

        # 6. 评分
        scorer = AdapterScorer()
        for group in ["rush", "stable", "safe"]:
            for item in categorized[group]:
                score = scorer.score(profile=profile_dict, record=item)
                item["adapter_score"] = score["total"]

        # 7. 持久化
        rec = Recommendation(
            id=uuid.uuid4(),
            user_id=user.id,
            input_snapshot={"rank": rank, "province": province, "subject_type": subject_type},
            result={k: [{"university_name": i["university_name"], "major_name": i["major_name"],
                          "adapter_score": i.get("adapter_score")} for i in v]
                    for k, v in categorized.items()},
            tier=tier,
        )
        await RecommendDAO().create_recommendation(rec)

        # 8. 构建响应
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
