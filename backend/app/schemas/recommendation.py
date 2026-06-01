import uuid
from pydantic import BaseModel


class RecommendRequest(BaseModel):
    score: int | None = None
    rank: int | None = None
    province: str | None = None
    subject_type: str | None = None
    exam_type: str | None = None


class RecommendItem(BaseModel):
    university_name: str
    major_name: str
    min_rank: int | None
    rank_ratio: float | None
    adapter_score: float | None
    reason: str | None = None


class RecommendResult(BaseModel):
    rush: list[RecommendItem]
    stable: list[RecommendItem]
    safe: list[RecommendItem]
    profile_completeness: float = 0.0
