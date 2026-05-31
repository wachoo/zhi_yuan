import uuid
from datetime import datetime, timedelta
from decimal import Decimal

from fastapi import HTTPException

from app.dao.order import OrderDAO
from app.dao.user import UserDAO
from app.models.order import Order
from app.models.user import User
from app.models.enums import MembershipTier, OrderStatus, PaymentMethod
from app.services.payment_providers import get_payment_provider
from app.schemas.payment import (
    CreateOrderResponse, TierInfo, TierListResponse,
    OrderInfo, MembershipInfo,
)

# 定价配置
TIER_PRICING = {
    MembershipTier.standard: Decimal("29.90"),
    MembershipTier.deep: Decimal("59.90"),
    MembershipTier.vip: Decimal("99.90"),
}

TIER_NAMES = {
    MembershipTier.free: "免费版",
    MembershipTier.standard: "标准版",
    MembershipTier.deep: "深度版",
    MembershipTier.vip: "尊享版",
}

TIER_FEATURES = {
    MembershipTier.free: [
        "每日 3 次 AI 对话",
        "基础推荐（每档 8 所）",
        "院校信息查询",
    ],
    MembershipTier.standard: [
        "每日 20 次 AI 对话",
        "完整推荐（每档不限）",
        "志愿表 PDF 导出",
        "院校信息查询",
    ],
    MembershipTier.deep: [
        "无限 AI 对话",
        "完整推荐（每档不限）",
        "志愿表 Excel 导出",
        "深度专业分析",
        "优先客服支持",
    ],
    MembershipTier.vip: [
        "无限 AI 对话",
        "完整推荐（每档不限）",
        "志愿表 Excel 导出",
        "深度专业分析",
        "一对一咨询报告",
        "家庭账号（3人共享）",
        "新功能优先体验",
    ],
}


class PaymentService:
    """支付相关业务逻辑"""

    @staticmethod
    def get_tiers(current_user: User | None = None) -> TierListResponse:
        """获取所有会员等级定价和权益"""
        tiers = []
        current_tier = current_user.membership_tier if current_user else MembershipTier.free.value
        expires_at = None

        if current_user and current_user.membership_expires_at:
            expires_at = current_user.membership_expires_at.isoformat()

        for tier in [MembershipTier.free, MembershipTier.standard, MembershipTier.deep, MembershipTier.vip]:
            price = TIER_PRICING.get(tier, Decimal("0"))
            tiers.append(TierInfo(
                tier=tier.value,
                name=TIER_NAMES[tier],
                price=price,
                features=TIER_FEATURES[tier],
                recommended=(tier == MembershipTier.deep),
                current=(tier.value == current_tier),
            ))

        return TierListResponse(
            tiers=tiers,
            current_tier=current_tier,
            expires_at=expires_at,
        )

    @staticmethod
    async def create_order(user: User, tier: MembershipTier, payment_method: PaymentMethod) -> CreateOrderResponse:
        """创建订单并生成 mock 支付二维码"""
        if tier == MembershipTier.free:
            raise HTTPException(status_code=400, detail="免费版无需购买")

        amount = TIER_PRICING.get(tier)
        if not amount:
            raise HTTPException(status_code=400, detail="无效的会员等级")

        # 生成订单号：ZY + 时间戳 + 随机后缀
        order_no = f"ZY{datetime.now().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:8]}"

        order = Order(
            id=uuid.uuid4(),
            user_id=user.id,
            order_no=order_no,
            tier=tier.value,
            amount=amount,
            payment_method=payment_method.value,
            status=OrderStatus.pending.value,
        )
        order = await OrderDAO().create_order(order)

        # 生成 mock QR 内容
        provider = get_payment_provider(payment_method.value)
        qr_content = provider.generate_qr_content(order_no, float(amount))

        return CreateOrderResponse(
            order_id=str(order.id),
            order_no=order_no,
            amount=amount,
            payment_method=payment_method.value,
            qr_content=qr_content,
            expires_in=1800,  # 30 分钟
        )

    @staticmethod
    async def simulate_payment(order_id: str, user: User) -> OrderInfo:
        """模拟支付成功 → 更新订单状态 → 激活会员"""
        order = await OrderDAO().get_by_id(uuid.UUID(order_id))
        if not order:
            raise HTTPException(status_code=404, detail="订单不存在")
        if order.user_id != user.id:
            raise HTTPException(status_code=403, detail="无权操作此订单")
        if order.status != OrderStatus.pending.value:
            raise HTTPException(status_code=400, detail=f"订单状态不允许支付：{order.status}")

        # 模拟验证支付成功
        provider = get_payment_provider(order.payment_method)
        verified = await provider.verify_payment(order.order_no)
        if not verified:
            raise HTTPException(status_code=400, detail="支付验证失败")

        # 更新订单状态
        now = datetime.utcnow()
        membership_end = now + timedelta(days=30)

        order.status = OrderStatus.activated.value
        order.paid_at = now
        order.membership_start = now
        order.membership_end = membership_end
        order = await OrderDAO().update_order(order)

        # 激活用户会员
        await UserDAO().update_membership(user.id, order.tier, membership_end)

        return OrderInfo(
            order_id=str(order.id),
            order_no=order.order_no,
            tier=order.tier,
            amount=order.amount,
            payment_method=order.payment_method,
            status=order.status,
            paid_at=order.paid_at.isoformat() if order.paid_at else None,
            created_at=order.created_at.isoformat() if order.created_at else None,
        )

    @staticmethod
    async def get_membership(user: User) -> MembershipInfo:
        """获取当前会员状态"""
        tier = user.membership_tier or MembershipTier.free.value
        name = TIER_NAMES.get(MembershipTier(tier), "免费版") if tier in [t.value for t in MembershipTier] else "免费版"

        expires_at = None
        days_remaining = None

        if user.membership_expires_at:
            expires_at = user.membership_expires_at.isoformat()
            remaining = user.membership_expires_at - datetime.utcnow()
            days_remaining = max(0, remaining.days)

        return MembershipInfo(
            tier=tier,
            name=name,
            expires_at=expires_at,
            days_remaining=days_remaining,
        )

    @staticmethod
    async def list_orders(user: User) -> list[OrderInfo]:
        """获取用户的订单历史"""
        orders = await OrderDAO().list_by_user(user.id)
        return [
            OrderInfo(
                order_id=str(o.id),
                order_no=o.order_no,
                tier=o.tier,
                amount=o.amount,
                payment_method=o.payment_method,
                status=o.status,
                paid_at=o.paid_at.isoformat() if o.paid_at else None,
                created_at=o.created_at.isoformat() if o.created_at else None,
            )
            for o in orders
        ]
