from enum import Enum


class MembershipTier(str, Enum):
    free = "free"
    standard = "standard"
    deep = "deep"
    vip = "vip"


class OrderStatus(str, Enum):
    pending = "pending"
    paid = "paid"
    activated = "activated"
    expired = "expired"
    cancelled = "cancelled"


class PaymentMethod(str, Enum):
    alipay = "alipay"
    wechat = "wechat"