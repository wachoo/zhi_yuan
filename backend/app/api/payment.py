from fastapi import APIRouter, Depends

from app.api.deps import get_current_user, get_optional_user
from app.models.user import User
from app.schemas.payment import (
    CreateOrderRequest, CreateOrderResponse,
    TierListResponse, OrderInfo,
    SimulatePaymentRequest, MembershipInfo,
)
from app.services.payment_service import PaymentService

router = APIRouter(prefix="/api/payment", tags=["支付"])


@router.get("/tiers", response_model=TierListResponse, summary="获取会员定价")
async def get_tiers(user: User | None = Depends(get_optional_user)):
    """获取所有会员等级的定价和权益列表（可选登录）"""
    return PaymentService.get_tiers(current_user=user)


@router.get("/membership", response_model=MembershipInfo, summary="当前会员状态")
async def get_membership(user: User = Depends(get_current_user)):
    """获取当前用户的会员状态"""
    return await PaymentService.get_membership(user)


@router.post("/orders", response_model=CreateOrderResponse, summary="创建订单")
async def create_order(req: CreateOrderRequest, user: User = Depends(get_current_user)):
    """创建会员订单，返回支付二维码内容"""
    return await PaymentService.create_order(user, req.tier, req.payment_method)


@router.post("/simulate", response_model=OrderInfo, summary="模拟支付")
async def simulate_payment(req: SimulatePaymentRequest, user: User = Depends(get_current_user)):
    """模拟支付成功，激活会员（仅用于演示）"""
    return await PaymentService.simulate_payment(req.order_id, user)


@router.get("/orders", response_model=list[OrderInfo], summary="订单列表")
async def list_orders(user: User = Depends(get_current_user)):
    """获取当前用户的订单历史"""
    return await PaymentService.list_orders(user)
