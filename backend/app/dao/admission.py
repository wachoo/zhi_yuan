from sqlalchemy import select

from app.models.admission import AdmissionRecord
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
