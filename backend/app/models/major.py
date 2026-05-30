import uuid
from sqlalchemy import String, Text, Integer, Float, Boolean, ARRAY, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Major(Base):
    __tablename__ = "majors"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(50), nullable=False)  # 工学/理学/文学...
    degree: Mapped[str] = mapped_column(String(10), default="本科")
    duration: Mapped[int] = mapped_column(Integer, default=4)  # 学制年限
    description: Mapped[str] = mapped_column(Text, nullable=True)
    courses: Mapped[list] = mapped_column(ARRAY(String), default=list)
    career_directions: Mapped[list] = mapped_column(ARRAY(String), default=list)
    avg_salary: Mapped[int] = mapped_column(Integer, nullable=True)  # 参考月薪(元)
    subject_requirements: Mapped[dict] = mapped_column(JSONB, nullable=True)  # 新高考选科要求

    # 考试科类标记：标记该专业可通过哪些考试科类报考
    is_normal: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")   # 普通类
    is_art: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")    # 艺术类
    is_sports: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false") # 体育类

    university_majors = relationship("UniversityMajor", back_populates="major")


class UniversityMajor(Base):
    __tablename__ = "university_majors"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    university_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("universities.id"), index=True)
    major_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("majors.id"), index=True)
    ranking: Mapped[str] = mapped_column(String(10), nullable=True)  # 学科评估等级 A+/A/A-...

    university = relationship("University")
    major = relationship("Major", back_populates="university_majors")