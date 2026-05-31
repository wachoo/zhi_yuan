from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field
from app.models.enums import MembershipTier, PaymentMethod, OrderStatus


class CreateOrderRequest(BaseModel):
    tier: MembershipTier = Field(..., description="目标会员等级")
    payment_method: PaymentMethod = Field(default=PaymentMethod.alipay, description="支付方式")


class CreateOrderResponse(BaseModel):
    order_id: str
    order_no: str
    amount: Decimal
    payment_method: str
    qr_content: str
    expires_in: int = Field(default=1800, description="支付超时秒数")


class TierFeature(BaseModel):
    name: str
    free: str
    standard: str
    deep: str
    vip: str


class TierInfo(BaseModel):
    tier: str
    name: str
    price: Decimal
    period: str = "月"
    features: list[str]
    recommended: bool = False
    current: bool = False


class TierListResponse(BaseModel):
    tiers: list[TierInfo]
    current_tier: str | None = None
    expires_at: str | None = None


class OrderInfo(BaseModel):
    order_id: str
    order_no: str
    tier: str
    amount: Decimal
    payment_method: str | None = None
    status: str
    paid_at: str | None = None
    created_at: str


class SimulatePaymentRequest(BaseModel):
    order_id: str = Field(..., description="订单ID")


class MembershipInfo(BaseModel):
    tier: str
    name: str
    expires_at: str | None = None
    days_remaining: int | None = None
