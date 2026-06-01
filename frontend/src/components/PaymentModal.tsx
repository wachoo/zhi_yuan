"use client";

import { useState, useEffect } from "react";
import {
  Modal, Steps, Button, Radio, QRCode, Typography, Space, Result, message,
} from "antd";
import {
  AlipayCircleOutlined,
  WechatOutlined,
  CheckCircleFilled,
  ClockCircleOutlined,
} from "@ant-design/icons";
import api from "@/lib/api";
import { PaymentMethod, CreateOrderResponse } from "@/types";

const { Text, Title } = Typography;

interface PaymentModalProps {
  open: boolean;
  tier: string;
  tierName: string;
  amount: number;
  onClose: () => void;
  onSuccess: () => void;
}

export default function PaymentModal({
  open, tier, tierName, amount, onClose, onSuccess,
}: PaymentModalProps) {
  const [step, setStep] = useState(0);
  const [method, setMethod] = useState<PaymentMethod>(PaymentMethod.ALIPAY);
  const [order, setOrder] = useState<CreateOrderResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [countdown, setCountdown] = useState(1800);

  // 倒计时
  useEffect(() => {
    if (step !== 1 || !order) return;
    const timer = setInterval(() => {
      setCountdown((prev) => {
        if (prev <= 1) {
          clearInterval(timer);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
    return () => clearInterval(timer);
  }, [step, order]);

  const formatCountdown = (seconds: number) => {
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return `${m.toString().padStart(2, "0")}:${s.toString().padStart(2, "0")}`;
  };

  const handleCreateOrder = async () => {
    setLoading(true);
    try {
      const res = await api.post("/api/payment/orders", {
        tier,
        payment_method: method,
      });
      setOrder(res.data);
      setCountdown(1800);
      setStep(1);
    } catch {
      message.error("创建订单失败");
    } finally {
      setLoading(false);
    }
  };

  const handleSimulatePayment = async () => {
    if (!order) return;
    setLoading(true);
    try {
      await api.post("/api/payment/simulate", { order_id: order.order_id });
      setStep(2);
      message.success("支付成功！会员已激活");
    } catch {
      message.error("模拟支付失败");
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    setStep(0);
    setOrder(null);
    setCountdown(1800);
    onClose();
  };

  const handleSuccessClose = () => {
    setStep(0);
    setOrder(null);
    setCountdown(1800);
    onSuccess();
  };

  return (
    <Modal
      open={open}
      onCancel={handleClose}
      footer={null}
      title={null}
      width={480}
      centered
      destroyOnClose
    >
      <div style={{ padding: "16px 0" }}>
        <Steps
          current={step}
          size="small"
          items={[
            { title: "选择支付方式" },
            { title: "扫码支付" },
            { title: "完成" },
          ]}
          style={{ marginBottom: 32 }}
        />

        {/* Step 0: 选择支付方式 */}
        {step === 0 && (
          <Space orientation="vertical" size={24} style={{ width: "100%" }}>
            <div>
              <Text type="secondary">购买会员</Text>
              <Title level={4} style={{ margin: "4px 0" }}>
                {tierName} <span style={{ color: "var(--zy-rush)", fontSize: 24 }}>¥{amount}</span>
                <Text type="secondary" style={{ fontSize: 14 }}>/月</Text>
              </Title>
            </div>

            <Radio.Group
              value={method}
              onChange={(e) => setMethod(e.target.value)}
              style={{ width: "100%" }}
            >
              <Space orientation="vertical" style={{ width: "100%" }} size={12}>
                <Radio.Button
                  value={PaymentMethod.ALIPAY}
                  style={{
                    height: 56, borderRadius: 10, display: "flex", alignItems: "center",
                    padding: "0 16px", border: method === PaymentMethod.ALIPAY
                      ? "2px solid #1677FF" : "1px solid var(--zy-border)",
                  }}
                >
                  <Space size={12}>
                    <AlipayCircleOutlined style={{ fontSize: 28, color: "#1677FF" }} />
                    <div>
                      <div style={{ fontWeight: 500 }}>支付宝</div>
                      <Text type="secondary" style={{ fontSize: 12 }}>推荐 · 即时到账</Text>
                    </div>
                  </Space>
                </Radio.Button>

                <Radio.Button
                  value={PaymentMethod.WECHAT}
                  style={{
                    height: 56, borderRadius: 10, display: "flex", alignItems: "center",
                    padding: "0 16px", border: method === PaymentMethod.WECHAT
                      ? "2px solid #07C160" : "1px solid var(--zy-border)",
                  }}
                >
                  <Space size={12}>
                    <WechatOutlined style={{ fontSize: 28, color: "#07C160" }} />
                    <div>
                      <div style={{ fontWeight: 500 }}>微信支付</div>
                      <Text type="secondary" style={{ fontSize: 12 }}>扫码支付</Text>
                    </div>
                  </Space>
                </Radio.Button>
              </Space>
            </Radio.Group>

            <Button
              type="primary"
              block
              size="large"
              loading={loading}
              onClick={handleCreateOrder}
              style={{ height: 48, borderRadius: 10, fontWeight: 500 }}
            >
              确认支付
            </Button>
          </Space>
        )}

        {/* Step 1: 扫码支付 */}
        {step === 1 && order && (
          <Space orientation="vertical" size={20} style={{ width: "100%" }} align="center">
            <div style={{ textAlign: "center" }}>
              <Text type="secondary">请使用{method === PaymentMethod.ALIPAY ? "支付宝" : "微信"}扫码支付</Text>
              <Title level={3} style={{ margin: "4px 0", color: "var(--zy-rush)" }}>
                ¥{Number(order.amount).toFixed(2)}
              </Title>
            </div>

            <div style={{
              padding: 20,
              background: "var(--zy-muted)",
              borderRadius: 12,
              textAlign: "center",
            }}>
              <QRCode
                value={order.qr_content}
                size={200}
                icon={method === PaymentMethod.ALIPAY ? undefined : undefined}
                color="#0F172A"
                style={{ margin: "0 auto" }}
              />
              <div style={{ marginTop: 12 }}>
                {method === PaymentMethod.ALIPAY ? (
                  <Space>
                    <AlipayCircleOutlined style={{ color: "#1677FF", fontSize: 18 }} />
                    <Text style={{ color: "#1677FF" }}>支付宝扫一扫</Text>
                  </Space>
                ) : (
                  <Space>
                    <WechatOutlined style={{ color: "#07C160", fontSize: 18 }} />
                    <Text style={{ color: "#07C160" }}>微信扫一扫</Text>
                  </Space>
                )}
              </div>
            </div>

            <Space>
              <ClockCircleOutlined style={{ color: "var(--zy-text-secondary)" }} />
              <Text type="secondary">
                支付剩余时间：{formatCountdown(countdown)}
              </Text>
            </Space>

            <Button
              type="primary"
              block
              size="large"
              loading={loading}
              onClick={handleSimulatePayment}
              style={{ height: 48, borderRadius: 10, fontWeight: 500 }}
            >
              <CheckCircleFilled style={{ marginRight: 8 }} />
              模拟支付成功（演示用）
            </Button>

            <Button type="link" onClick={handleClose}>取消支付</Button>
          </Space>
        )}

        {/* Step 2: 完成 */}
        {step === 2 && (
          <Result
            status="success"
            icon={<CheckCircleFilled style={{ color: "var(--zy-accent)" }} />}
            title="支付成功！"
            subTitle={`${tierName}已激活，有效期 30 天`}
            extra={[
              <Button type="primary" key="done" onClick={handleSuccessClose} style={{ borderRadius: 8 }}>
                开始使用
              </Button>,
            ]}
          />
        )}
      </div>
    </Modal>
  );
}
