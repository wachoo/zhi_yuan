from sqlalchemy import select

from app.models.admission import AdmissionRecord, ScoreSegment
from app.models.university import University
from app.models.major import Major
from app.database import async_session


class AdmissionDAO:

    async def query_records_with_details(
        self, province: str, subject_type: str
    ) -> list[tuple[AdmissionRecord, University, Major | None]]:
        """查询录取记录，关联院校和专业信息"""
        async with async_session() as db:
            result = await db.execute(
                select(AdmissionRecord, University, Major)
                .join(University, AdmissionRecord.university_id == University.id)
                .outerjoin(Major, AdmissionRecord.major_id == Major.id)
                .where(AdmissionRecord.province == province)
                .where(AdmissionRecord.subject_type == subject_type)
            )
            return list(result.all())

    async def get_admission_scores(
        self,
        university_name: str,
        province: str,
        subject_type: str | None = None,
        major_name: str | None = None,
        years: int = 3,
    ) -> list[dict]:
        """查询某院校在指定省份的历年录取分数"""
        async with async_session() as db:
            # 先找院校 ID
            uni_result = await db.execute(
                select(University).where(University.name.contains(university_name))
            )
            universities = uni_result.scalars().all()
            if not universities:
                return []

            uni_ids = [u.id for u in universities]
            stmt = (
                select(AdmissionRecord, University, Major)
                .join(University, AdmissionRecord.university_id == University.id)
                .outerjoin(Major, AdmissionRecord.major_id == Major.id)
                .where(AdmissionRecord.university_id.in_(uni_ids))
                .where(AdmissionRecord.province == province)
            )
            if subject_type:
                stmt = stmt.where(AdmissionRecord.subject_type == subject_type)
            if major_name:
                stmt = stmt.where(Major.name.contains(major_name))

            stmt = stmt.order_by(AdmissionRecord.year.desc())
            result = await db.execute(stmt)
            rows = result.all()

            # 只取最近 N 年
            records = []
            seen_years = set()
            for admission, uni, major in rows:
                if admission.year not in seen_years or major_name:
                    records.append({
                        "university_name": uni.name,
                        "major_name": major.name if major else "未分专业",
                        "year": admission.year,
                        "batch": admission.batch,
                        "subject_type": admission.subject_type,
                        "min_score": admission.min_score,
                        "avg_score": admission.avg_score,
                        "max_score": admission.max_score,
                        "min_rank": admission.min_rank,
                        "avg_rank": admission.avg_rank,
                        "plan_count": admission.plan_count,
                        "actual_count": admission.actual_count,
                    })
                    seen_years.add(admission.year)
                if not major_name and len(seen_years) > years:
                    break

            return records

    async def get_score_segments(
        self, province: str, year: int, subject_type: str,
        score_min: int | None = None, score_max: int | None = None,
    ) -> list[dict]:
        """查询一分一段表"""
        async with async_session() as db:
            stmt = (
                select(ScoreSegment)
                .where(ScoreSegment.province == province)
                .where(ScoreSegment.year == year)
                .where(ScoreSegment.subject_type == subject_type)
            )
            if score_min is not None:
                stmt = stmt.where(ScoreSegment.score >= score_min)
            if score_max is not None:
                stmt = stmt.where(ScoreSegment.score <= score_max)

            stmt = stmt.order_by(ScoreSegment.score.desc())
            result = await db.execute(stmt)
            rows = result.scalars().all()
            return [
                {
                    "score": r.score,
                    "count": r.count,
                    "cumulative_count": r.cumulative_count,
                }
                for r in rows
            ]
