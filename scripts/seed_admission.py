"""种子数据：院校录取记录（admission_records）+ 一分一段表（score_segments）

为推荐引擎生成模拟录取数据，覆盖 物理类/历史类/综合改革 三种科类。
31 个省份 × 6 年（2020-2025），按新高考改革批次自动切换科类。
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
from app.constants import SubjectType, ExamType

# ── 全部 31 个省份 ──────────────────────────────────────────────
PROVINCES = [
    "北京", "天津", "上海", "重庆", "河北", "山西", "辽宁", "吉林", "黑龙江",
    "江苏", "浙江", "安徽", "福建", "江西", "山东", "河南", "湖北", "湖南",
    "广东", "海南", "四川", "贵州", "云南", "陕西", "甘肃", "青海", "内蒙古",
    "广西", "西藏", "宁夏", "新疆",
]

# 新高考改革分 4 批，每批从对应年份起使用综合改革科类
# 第 1 批（2017 起）: 浙江、上海
# 第 2 批（2020 起）: 北京、天津、山东、海南
# 第 3 批（2021 起）: 河北、辽宁、江苏、福建、湖北、湖南、广东、重庆
# 第 4 批（2024 起）: 吉林、黑龙江、安徽、江西、广西、贵州、甘肃
# 第 5 批（2025 起）: 山西、河南、陕西、内蒙古、四川、云南、宁夏、青海
# 尚未改革: 西藏、新疆（仍用物理类+历史类）
COMPREHENSIVE_REFORM_YEAR = {
    "浙江": 2017, "上海": 2017,
    "北京": 2020, "天津": 2020, "山东": 2020, "海南": 2020,
    "河北": 2021, "辽宁": 2021, "江苏": 2021, "福建": 2021,
    "湖北": 2021, "湖南": 2021, "广东": 2021, "重庆": 2021,
    "吉林": 2024, "黑龙江": 2024, "安徽": 2024, "江西": 2024,
    "广西": 2024, "贵州": 2024, "甘肃": 2024,
    "山西": 2025, "河南": 2025, "陕西": 2025, "内蒙古": 2025,
    "四川": 2025, "云南": 2025, "宁夏": 2025, "青海": 2025,
}

# 年份覆盖
YEARS = [2020, 2021, 2022, 2023, 2024, 2025]

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


def get_subject_types(province: str, year: int) -> list[str]:
    """根据省份和年份确定该年使用的科类列表"""
    reform_year = COMPREHENSIVE_REFORM_YEAR.get(province)
    if reform_year and year >= reform_year:
        return [SubjectType.COMPREHENSIVE_REFORM.value]
    else:
        return [SubjectType.PHYSICS.value, SubjectType.HISTORY.value]


def generate_score_from_rank(min_rank: int) -> int:
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


def rank_range_for_art(ranking: int | None, level: str | None) -> tuple[int, int]:
    """艺术类位次范围 — 按院校层次分布（考生人数介于体育类和普通类之间）"""
    if ranking and ranking <= 10:
        return (100, 1000)
    if ranking and ranking <= 40:
        return (500, 5000)
    if ranking and ranking <= 120:
        return (2000, 12000)
    if level == "985":
        return (1000, 8000)
    if level == "211":
        return (5000, 20000)
    if level == "双一流":
        return (8000, 35000)
    return (15000, 80000)     # 普通本科


def rank_range_for_sports(ranking: int | None, level: str | None) -> tuple[int, int]:
    """体育类位次范围 — 按院校层次分布（考生少，范围比普通类窄）"""
    if ranking and ranking <= 10:
        return (50, 500)        # 顶尖院校
    if ranking and ranking <= 40:
        return (200, 2000)      # 985 前段
    if ranking and ranking <= 120:
        return (800, 5000)      # 985 后段 / 强 211
    if level == "985":
        return (500, 3000)
    if level == "211":
        return (1500, 8000)
    if level == "双一流":
        return (3000, 15000)
    return (5000, 25000)        # 普通本科


def generate_art_score_from_rank(min_rank: int) -> int:
    """艺术类分数生成（文化课分数线低于普通类，高于体育类）"""
    if min_rank < 1000:
        return random.randint(530, 600)
    if min_rank < 5000:
        return random.randint(450, 550)
    if min_rank < 15000:
        return random.randint(380, 480)
    if min_rank < 35000:
        return random.randint(320, 420)
    return random.randint(250, 380)


def generate_sports_score_from_rank(min_rank: int) -> int:
    """体育类分数生成（文化课分数线通常低于普通类）"""
    if min_rank < 500:
        return random.randint(550, 620)
    if min_rank < 1500:
        return random.randint(480, 560)
    if min_rank < 3000:
        return random.randint(420, 500)
    if min_rank < 5000:
        return random.randint(360, 440)
    if min_rank < 10000:
        return random.randint(300, 400)
    if min_rank < 15000:
        return random.randint(260, 360)
    return random.randint(200, 320)


async def seed_admission_records():
    async with async_session() as db:
        # 清空旧数据
        await db.execute(delete(AdmissionRecord))

        # 加载院校和专业
        uni_rows = (await db.execute(select(University))).scalars().all()
        major_rows = (await db.execute(select(Major))).scalars().all()

        # 按考试科类分组专业（使用 is_normal / is_art / is_sports 布尔字段）
        normal_majors = [m for m in major_rows if m.is_normal]
        art_exam_majors = [m for m in major_rows if m.is_art]
        sports_exam_majors = [m for m in major_rows if m.is_sports]

        # 普通类内部再按学科分：物理类偏理工，历史类偏文史
        sci_majors = [m for m in normal_majors if m.category in ("工学", "理学", "医学")]
        art_majors = [m for m in normal_majors if m.category in ("文学", "法学", "历史学", "教育学", "管理学", "经济学", "哲学")]
        all_majors = normal_majors or major_rows or [None]

        if not art_exam_majors:
            art_exam_majors = all_majors
        if not sports_exam_majors:
            sports_exam_majors = all_majors
        if not sci_majors:
            sci_majors = all_majors
        if not art_majors:
            art_majors = all_majors

        records = []
        for uni in uni_rows:
            low, high = rank_range_for_university(uni.ranking, uni.level)

            for province in PROVINCES:
                for year in YEARS:
                    subject_types = get_subject_types(province, year)

                    for subject_type in subject_types:
                        # 选专业：物理类偏理工，历史类偏文史，综合改革随机
                        if subject_type == SubjectType.PHYSICS.value:
                            pool = sci_majors if sci_majors else all_majors
                        elif subject_type == SubjectType.HISTORY.value:
                            pool = art_majors if art_majors else all_majors
                        else:
                            pool = all_majors

                        # 每所大学每省每科类选 2-4 个专业
                        n_majors = min(random.randint(2, 4), len(pool))
                        selected_majors = random.sample(pool, n_majors)

                        for major in selected_majors:
                            base_rank = random.randint(low, high)
                            # 不同年份有波动 ±15%
                            min_rank = max(1, int(base_rank * random.uniform(0.85, 1.15)))
                            avg_rank = max(1, min_rank - random.randint(50, 500))

                            min_score = generate_score_from_rank(min_rank)
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
                                exam_type=ExamType.NORMAL.value,
                                min_score=min_score,
                                avg_score=avg_score,
                                max_score=max_score,
                                min_rank=min_rank,
                                avg_rank=avg_rank,
                                plan_count=plan_count,
                                actual_count=max(1, actual_count),
                            ))

                            # 艺术类：约 20% 的普通类记录同时生成艺术类
                            # 位次按院校层次分布，只用艺术学专业
                            if random.random() < 0.2:
                                art_major = random.choice(art_exam_majors)
                                art_low, art_high = rank_range_for_art(uni.ranking, uni.level)
                                base_art_rank = random.randint(art_low, art_high)
                                # 不同年份有波动 ±15%
                                art_rank = max(1, int(base_art_rank * random.uniform(0.85, 1.15)))
                                art_avg_rank = max(1, art_rank - random.randint(50, 300))
                                records.append(AdmissionRecord(
                                    id=uuid.uuid4(),
                                    university_id=uni.id,
                                    major_id=art_major.id if art_major else None,
                                    province=province,
                                    year=year,
                                    batch=random.choice(BATCHES),
                                    subject_type=subject_type,
                                    exam_type=ExamType.ART.value,
                                    min_score=generate_art_score_from_rank(art_rank),
                                    avg_score=generate_art_score_from_rank(art_avg_rank),
                                    max_score=generate_art_score_from_rank(art_rank) + random.randint(1, 10),
                                    min_rank=art_rank,
                                    avg_rank=art_avg_rank,
                                    plan_count=random.randint(3, 30),
                                    actual_count=random.randint(3, 30),
                                ))

                            # 体育类：约 70% 的普通类记录同时生成体育类
                            # 位次按院校层次分布，覆盖 50-25000
                            if random.random() < 0.70:
                                sport_major = random.choice(sports_exam_majors)
                                sport_low, sport_high = rank_range_for_sports(uni.ranking, uni.level)
                                base_sport_rank = random.randint(sport_low, sport_high)
                                # 不同年份有波动 ±15%
                                sport_rank = max(1, int(base_sport_rank * random.uniform(0.85, 1.15)))
                                sport_avg_rank = max(1, sport_rank - random.randint(20, 200))
                                records.append(AdmissionRecord(
                                    id=uuid.uuid4(),
                                    university_id=uni.id,
                                    major_id=sport_major.id if sport_major else None,
                                    province=province,
                                    year=year,
                                    batch=random.choice(BATCHES),
                                    subject_type=subject_type,
                                    exam_type=ExamType.SPORTS.value,
                                    min_score=generate_sports_score_from_rank(sport_rank),
                                    avg_score=generate_sports_score_from_rank(sport_avg_rank),
                                    max_score=generate_sports_score_from_rank(sport_rank) + random.randint(1, 10),
                                    min_rank=sport_rank,
                                    avg_rank=sport_avg_rank,
                                    plan_count=random.randint(2, 20),
                                    actual_count=random.randint(2, 20),
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
            for year in YEARS:
                subject_types = get_subject_types(province, year)

                for subject_type in subject_types:
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
