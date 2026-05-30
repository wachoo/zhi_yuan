import uuid
import logging

from fastapi import HTTPException

from app.dao.profile import ProfileDAO
from app.dao.admission import AdmissionDAO
from app.dao.recommend import RecommendDAO
from app.models.enums import MembershipTier
from app.models.recommendation import Recommendation
from app.services.recommendation_engine import RecommendationEngine, _expand_dislikes
from app.services.adapter_scorer import AdapterScorer
from app.schemas.recommendation import RecommendRequest, RecommendResult, RecommendItem

logger = logging.getLogger(__name__)


class RecommendService:
    """推荐相关业务逻辑"""

    async def get_latest_recommendation_summary(self, user_id: uuid.UUID) -> str:
        """获取用户最近一次推荐结果摘要（供 LLM 上下文使用）"""
        rec = await RecommendDAO().get_latest_by_user(user_id)
        return str(rec.result) if rec else ""

    async def get_latest_recommendation_detail(self, user_id: uuid.UUID) -> dict:
        """获取用户最近一次推荐结果详情（供工具调用）"""
        rec = await RecommendDAO().get_latest_by_user(user_id)
        if not rec:
            return {"message": "该用户暂无推荐记录，请先使用「智能推荐」功能生成推荐"}
        return {
            "input": rec.input_snapshot,
            "result": rec.result,
            "tier": rec.tier,
            "created_at": rec.created_at.isoformat() if rec.created_at else None,
        }

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
        rank = request.rank if request.rank is not None else basic.get("rank", 0)
        province = request.province if request.province is not None else basic.get("province", "")
        subject_type = request.subject_type if request.subject_type is not None else basic.get("subject_type", "")
        exam_type = request.exam_type if request.exam_type is not None else basic.get("exam_type", "普通类")

        if not rank or not province or not subject_type:
            raise HTTPException(status_code=400, detail="请至少提供位次、省份和科类")

        # 2. 查询录取数据
        raw_records = await AdmissionDAO().query_records_with_details(province, subject_type, exam_type)
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
        personality = profile_dict.get("personality")
        dislikes = personality.get("dislikes") if personality else None
        interests = personality.get("interests") if personality else None

        # LLM 语义扩展厌恶/兴趣关键词，失败时降级到硬编码
        expanded_dislikes = None
        if dislikes:
            try:
                from app.services.llm_service import LLMService
                from app.dao.major import MajorDAO
                # 获取所有专业名称，传给 LLM 做筛选
                major_names = await MajorDAO().get_all_names()
                llm_result = await LLMService().semantic_expand(
                    dislikes=dislikes, interests=interests, major_names=major_names
                )
                llm_dislikes = llm_result.get("dislikes", [])
                expanded_set = set(dislikes)
                # 新格式：LLM 直接返回专业名称列表
                if isinstance(llm_dislikes, list):
                    expanded_set.update(llm_dislikes)
                # 兼容旧格式：字典格式
                elif isinstance(llm_dislikes, dict):
                    for keywords in llm_dislikes.values():
                        expanded_set.update(keywords)
                expanded_dislikes = list(expanded_set)
                logger.info(f"LLM expanded dislikes: {expanded_dislikes}")
            except Exception as e:
                logger.warning(f"LLM semantic expansion failed, using fallback: {e}")
                expanded_dislikes = _expand_dislikes(dislikes)

        filtered = engine.filter_records(
            records=records, province=province, subject_type=subject_type, tuition_max=tuition_max,
            dislikes=dislikes, expanded_dislikes=expanded_dislikes,
        )

        # 4. 分类
        categorized = engine.categorize(equivalent_rank=rank, records=filtered)

        # 5. 会员限制
        tier = user.membership_tier
        categorized = engine.limit_for_tier(categorized, tier=tier, max_per_group=1 if tier == MembershipTier.free else 999)

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
            input_snapshot={"rank": rank, "province": province, "subject_type": subject_type, "exam_type": exam_type},
            result={k: [{"university_name": i["university_name"], "major_name": i["major_name"],
                          "min_rank": i.get("min_rank"), "rank_ratio": i.get("rank_ratio"),
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
