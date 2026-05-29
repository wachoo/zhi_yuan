from app.dao.admission import AdmissionDAO


class AdmissionService:
    """录取数据相关业务逻辑"""

    async def get_admission_scores(
        self,
        university_name: str,
        province: str,
        subject_type: str | None = None,
        major_name: str | None = None,
        years: int = 3,
    ) -> dict:
        """查询院校历年录取分数"""
        records = await AdmissionDAO().get_admission_scores(
            university_name=university_name,
            province=province,
            subject_type=subject_type,
            major_name=major_name,
            years=years,
        )
        if not records:
            return {"message": f"未找到「{university_name}」在{province}的录取数据"}
        return {"university_name": university_name, "province": province, "records": records}

    async def get_score_segments(
        self,
        province: str,
        year: int,
        subject_type: str,
        score: int | None = None,
        range_width: int = 20,
    ) -> dict:
        """查询一分一段表，可按分数范围过滤"""
        score_min = (score - range_width) if score else None
        score_max = (score + range_width) if score else None
        segments = await AdmissionDAO().get_score_segments(
            province=province, year=year, subject_type=subject_type,
            score_min=score_min, score_max=score_max,
        )
        if not segments:
            return {"message": f"未找到{province}{year}年{subject_type}的一分一段数据"}
        return {"province": province, "year": year, "subject_type": subject_type, "segments": segments}
