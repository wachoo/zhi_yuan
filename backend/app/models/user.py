import uuid
from datetime import datetime
from sqlalchemy import String, Text, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    phone: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(200), nullable=False)
    nickname: Mapped[str] = mapped_column(String(50), nullable=True)
    membership_tier: Mapped[str] = mapped_column(String(20), default="free")  # free/standard/deep/vip
    membership_expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    daily_chat_count: Mapped[int] = mapped_column(default=0)
    last_chat_date: Mapped[str] = mapped_column(String(10), nullable=True)  # YYYY-MM-DD
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), unique=True, index=True)
    basic_info: Mapped[dict] = mapped_column(JSONB, nullable=True)
    family_info: Mapped[dict] = mapped_column(JSONB, nullable=True)
    personality: Mapped[dict] = mapped_column(JSONB, nullable=True)
    ability: Mapped[dict] = mapped_column(JSONB, nullable=True)
    values_info: Mapped[dict] = mapped_column(JSONB, nullable=True)
    completeness: Mapped[float] = mapped_column(Float, default=0.0)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)