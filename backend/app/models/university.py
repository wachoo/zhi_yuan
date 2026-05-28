import uuid
from sqlalchemy import String, Text, Float, ARRAY
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class University(Base):
    __tablename__ = "universities"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    province: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    city: Mapped[str] = mapped_column(String(50), nullable=False)
    level: Mapped[str] = mapped_column(String(20), nullable=True)  # 985/211/双一流/普通本科/民办
    type: Mapped[str] = mapped_column(String(20), nullable=True)   # 综合/理工/师范/医药/财经
    tags: Mapped[list] = mapped_column(ARRAY(String), default=list)
    tuition_min: Mapped[int] = mapped_column(nullable=True)
    tuition_max: Mapped[int] = mapped_column(nullable=True)
    website: Mapped[str] = mapped_column(String(500), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    latitude: Mapped[float] = mapped_column(Float, nullable=True)
    longitude: Mapped[float] = mapped_column(Float, nullable=True)
    logo_url: Mapped[str] = mapped_column(String(500), nullable=True)

    admission_records = relationship("AdmissionRecord", back_populates="university")