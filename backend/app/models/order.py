import uuid
from datetime import datetime
from decimal import Decimal
from sqlalchemy import String, DateTime, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base
from app.models.enums import MembershipTier, OrderStatus, PaymentMethod


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    order_no: Mapped[str] = mapped_column(String(32), unique=True, nullable=False, index=True)
    tier: Mapped[str] = mapped_column(String(20), nullable=False)  # MembershipTier value
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    payment_method: Mapped[str] = mapped_column(String(20), nullable=True)  # PaymentMethod value
    status: Mapped[str] = mapped_column(String(20), default=OrderStatus.pending, nullable=False)
    paid_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    membership_start: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    membership_end: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
