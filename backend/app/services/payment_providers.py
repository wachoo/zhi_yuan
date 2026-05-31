"""Mock 支付提供方 — 模拟支付宝/微信支付接口"""
import json
from datetime import datetime


class AlipayStub:
    """支付宝沙箱模拟（无需真实 API 密钥）"""

    @staticmethod
    def generate_qr_content(order_no: str, amount: float) -> str:
        """生成模拟的支付宝支付链接（用于 QR 码展示）"""
        payload = {
            "app_id": "2026000000000001",
            "method": "alipay.trade.precreate",
            "out_trade_no": order_no,
            "total_amount": str(amount),
            "subject": "智愿会员",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        return f"https://qr.alipay.com/mock?data={json.dumps(payload, ensure_ascii=False)}"

    @staticmethod
    async def verify_payment(order_no: str) -> bool:
        """模拟验证支付结果 — 始终返回成功"""
        return True


class WechatPayStub:
    """微信支付沙箱模拟（无需真实商户号）"""

    @staticmethod
    def generate_qr_content(order_no: str, amount: float) -> str:
        """生成模拟的微信支付链接（用于 QR 码展示）"""
        payload = {
            "appid": "wx2026000000000001",
            "mch_id": "1600000001",
            "out_trade_no": order_no,
            "total_fee": int(amount * 100),  # 微信支付以分为单位
            "body": "智愿会员",
            "time_stamp": str(int(datetime.now().timestamp())),
        }
        return f"weixin://wxpay/bizpayurl?mock={json.dumps(payload, ensure_ascii=False)}"

    @staticmethod
    async def verify_payment(order_no: str) -> bool:
        """模拟验证支付结果 — 始终返回成功"""
        return True


def get_payment_provider(method: str):
    """根据支付方式获取对应的 mock provider"""
    if method == "alipay":
        return AlipayStub()
    elif method == "wechat":
        return WechatPayStub()
    else:
        raise ValueError(f"Unsupported payment method: {method}")
