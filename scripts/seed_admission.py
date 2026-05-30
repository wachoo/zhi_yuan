"""种子数据：院校录取记录（admission_records）+ 一分一段表（score_segments）

为推荐引擎生成模拟录取数据，覆盖 物理类/历史类/综合改革 三种科类。
"""
import asyncio
import random
import uuid
import sys
sys.path.insert(0, "backend")

from sqlalchemy import select, delete, text
from app.database import async_session
from app.models.admission import AdmissionRecord, ScoreSegment
from app.models.university import University
from app.models.major import Major
from app.constants import SubjectType

# ── 覆盖的主要省份 ──────────────────────────────────────────────
PROVINCES = [
    "北京", "天津", "上海", "重庆", "河北", "山西", "辽宁", "吉林", "黑龙江",
    "江苏", "浙江", "安徽", "福建", "江西", "山东", "河南", "湖北", "湖南",
    "广东", "海南", "四川", "贵州", "云南", "陕西", "甘肃", "青海", "内蒙古",
    "广西", "西藏", "宁夏", "新疆",
]

# 新高考省份 → 综合改革；传统理综省份 → 物理类 + 历史类
COMPREHENSIVE_REFORM_PROVINCES = {"北京", "天津", "上海", "浙江", "山东", "海南", "江苏", "福建", "广东", "湖南", "湖北", "河北", "辽宁", "重庆"}

# 年份覆盖
YEARS = [2023, 2024, 2025]

# 录取批次
BATCHES = ["本科一批", "本科批"]

# 按 ranking 划分的基础位次范围 (min_rank, max_rank)
# ranking 越小学校越好，位次数字越小越好
def rank_range_for_university(ranking: int | None, level: str | None) -> tuple[int, int]:
    """根据排名和层次返回位次范围 (min_rank 下限, max_rank 上限)"""
    if ranking and ranking <= 10:
        return (50, 800)        # 清北等顶尖
    if ranking and ranking <= 40:
        return (500, 8000)      # 985 前段
    if ranking and ranking <= 120:
        return (5000, 25000)    # 985 后段 / 强 211
    if level == "985":
        return (3000, 15000)
    if level == "211":
        return (10000, 40000)
    if level == "双一流":
        return (20000, 70000)
    return (40000, 150000)      # 普通本科


def generate_score_from_rank(min_rank: int, province: str) -> int:
    """粗略根据位次反推分数（仅供模拟）"""
    # 高分段（位次低）→ 分数高
    if min_rank < 1000:
        return random.randint(670, 700)
    if min_rank < 5000:
        return random.randint(640, 680)
    if min_rank < 15000:
        return random.randint(600, 650)
    if min_rank < 40000:
        return random.randint(550, 620)
    if min_rank < 80000:
        return random.randint(480, 570)
    return random.randint(400, 520)


async def seed_admission_records():
    async with async_session() as db:
        # 清空旧数据
        await db.execute(delete(AdmissionRecord))

        # 加载院校和专业
        uni_rows = (await db.execute(select(University))).scalars().all()
        major_rows = (await db.execute(select(Major))).scalars().all()

        # 按类别分组专业
        sci_majors = [m for m in major_rows if m.category in ("工学", "理学", "医学")]
        art_majors = [m for m in major_rows if m.category in ("文学", "法学", "历史学", "教育学", "管理学", "经济学", "哲学")]
        all_majors = major_rows or [None]

        if not sci_majors:
            sci_majors = all_majors
        if not art_majors:
            art_majors = all_majors

        records = []
        for uni in uni_rows:
            low, high = rank_range_for_university(uni.ranking, uni.level)

            for province in PROVINCES:
                # 根据省份决定科类
                if province in COMPREHENSIVE_REFORM_PROVINCES:
                    subject_types = [SubjectType.COMPREHENSIVE_REFORM.value]
                    majors_pool = all_majors
                else:
                    subject_types = [SubjectType.PHYSICS.value, SubjectType.HISTORY.value]
                    majors_pool = all_majors

                for subject_type in subject_types:
                    # 选专业：物理类偏理工，历史类偏文史，综合改革随机
                    if subject_type == SubjectType.PHYSICS.value:
                        pool = sci_majors if sci_majors else majors_pool
                    elif subject_type == SubjectType.HISTORY.value:
                        pool = art_majors if art_majors else majors_pool
                    else:
                        pool = majors_pool

                    # 每所大学每省选 2-4 个专业
                    n_majors = min(random.randint(2, 4), len(pool))
                    selected_majors = random.sample(pool, n_majors)

                    for major in selected_majors:
                        for year in YEARS:
                            base_rank = random.randint(low, high)
                            # 不同年份有波动 ±15%
                            min_rank = max(1, int(base_rank * random.uniform(0.85, 1.15)))
                            avg_rank = max(1, min_rank - random.randint(50, 500))

                            min_score = generate_score_from_rank(min_rank, province)
                            avg_score = min_score + random.randint(1, 8)
                            max_score = avg_score + random.randint(1, 15)

                            plan_count = random.randint(5, 80)
                            actual_count = plan_count + random.randint(-3, 3)

                            records.append(AdmissionRecord(
                                id=uuid.uuid4(),
                                university_id=uni.id,
                                major_id=major.id if major else None,
                                province=province,
                                year=year,
                                batch=random.choice(BATCHES),
                                subject_type=subject_type,
                                min_score=min_score,
                                avg_score=avg_score,
                                max_score=max_score,
                                min_rank=min_rank,
                                avg_rank=avg_rank,
                                plan_count=plan_count,
                                actual_count=max(1, actual_count),
                            ))

        # 批量插入
        db.add_all(records)
        await db.commit()
        print(f"[admission_records] 已插入 {len(records)} 条录取记录")


async def seed_score_segments():
    """为每个省份 × 年份 × 科类生成一分一段表"""
    async with async_session() as db:
        await db.execute(delete(ScoreSegment))

        segments = []
        for province in PROVINCES:
            if province in COMPREHENSIVE_REFORM_PROVINCES:
                subject_types = [SubjectType.COMPREHENSIVE_REFORM.value]
            else:
                subject_types = [SubjectType.PHYSICS.value, SubjectType.HISTORY.value]

            for subject_type in subject_types:
                for year in YEARS:
                    cumulative = 0
                    # 从 750 分往下到 200 分
                    for score in range(750, 199, -1):
                        # 高分段人少，中间段人多，低分段人少（正态分布近似）
                        center = 500
                        dist = abs(score - center)
                        base_count = max(1, int(3000 * (2.718 ** (-dist ** 2 / 18000))))
                        count = max(0, base_count + random.randint(-50, 50))
                        cumulative += count
                        segments.append(ScoreSegment(
                            id=uuid.uuid4(),
                            province=province,
                            year=year,
                            subject_type=subject_type,
                            score=score,
                            count=count,
                            cumulative_count=cumulative,
                        ))

        db.add_all(segments)
        await db.commit()
        print(f"[score_segments] 已插入 {len(segments)} 条一分一段数据")


async def main():
    await seed_admission_records()
    await seed_score_segments()
    print("种子数据导入完成!")


if __name__ == "__main__":
    asyncio.run(main())
