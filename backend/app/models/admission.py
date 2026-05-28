import uuid
from sqlalchemy import String, Integer, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class AdmissionRecord(Base):
    __tablename__ = "admission_records"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    university_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("universities.id"), index=True)
    major_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("majors.id"), nullable=True)
    province: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    year: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    batch: Mapped[str] = mapped_column(String(30), nullable=True)  # 本科一批/二批/提前批
    subject_type: Mapped[str] = mapped_column(String(20), nullable=False)  # 文/理/物理类/历史类/综合改革
    min_score: Mapped[int] = mapped_column(Integer, nullable=True)
    avg_score: Mapped[int] = mapped_column(Integer, nullable=True)
    max_score: Mapped[int] = mapped_column(Integer, nullable=True)
    min_rank: Mapped[int] = mapped_column(Integer, nullable=True)
    avg_rank: Mapped[int] = mapped_column(Integer, nullable=True)
    plan_count: Mapped[int] = mapped_column(Integer, nullable=True)
    actual_count: Mapped[int] = mapped_column(Integer, nullable=True)

    university = relationship("University", back_populates="admission_records")


class ScoreSegment(Base):
    """一分一段表"""
    __tablename__ = "score_segments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    province: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    year: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    subject_type: Mapped[str] = mapped_column(String(20), nullable=False)
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    count: Mapped[int] = mapped_column(Integer, nullable=False)      # 本分人数
    cumulative_count: Mapped[int] = mapped_column(Integer, nullable=False)  # 累计人数（位次）