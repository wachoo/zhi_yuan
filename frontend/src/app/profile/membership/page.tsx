"use client";

import { useEffect, useState, useCallback } from "react";
import {
  Card,
  Button,
  Space,
  Row,
  Col,
  Typography,
  Table,
  Tag,
  Tooltip,
} from "antd";
import {
  CrownOutlined,
  CheckOutlined,
  ClockCircleOutlined,
  AlipayCircleOutlined,
  WechatOutlined,
} from "@ant-design/icons";
import api from "@/lib/api";
import PaymentModal from "@/components/PaymentModal";
import {
  TierListResponse,
  OrderInfo,
  MembershipInfo,
  MembershipTier,
} from "@/types";

const { Text, Title } = Typography;

const TIER_COLORS: Record<string, string> = {
  free: "#94A3B8",
  standard: "#2563EB",
  deep: "#7C3AED",
  vip: "#D97706",
};

const TIER_GRADIENTS: Record<string, string> = {
  free: "linear-gradient(135deg, #94A3B8, #CBD5E1)",
  standard: "linear-gradient(135deg, #2563EB, #60A5FA)",
  deep: "linear-gradient(135deg, #7C3AED, #A78BFA)",
  vip: "linear-gradient(135deg, #D97706, #FBBF24)",
};

const TIER_NAME_MAP: Record<string, string> = {
  free: "免费版",
  standard: "标准版",
  deep: "深度版",
  vip: "尊享版",
};

const PAYMENT_METHOD_MAP: Record<
  string,
  { label: string; color: string; icon: React.ReactNode }
> = {
  alipay: { label: "支付宝", color: "#1677FF", icon: <AlipayCircleOutlined /> },
  wechat: { label: "微信支付", color: "#07C160", icon: <WechatOutlined /> },
};

const STATUS_MAP: Record<string, { label: string; color: string }> = {
  pending: { label: "待支付", color: "orange" },
  paid: { label: "已支付", color: "blue" },
  activated: { label: "已激活", color: "green" },
  expired: { label: "已过期", color: "default" },
  cancelled: { label: "已取消", color: "default" },
};

const orderColumns = [
  {
    title: "订单号",
    dataIndex: "order_no",
    key: "order_no",
    render: (v: string) => (
      <Text code style={{ fontSize: 12 }}>
        {v}
      </Text>
    ),
  },
  {
    title: "会员",
    dataIndex: "tier",
    key: "tier",
    render: (v: string) => (
      <Tag color={TIER_COLORS[v]}>{TIER_NAME_MAP[v] || v}</Tag>
    ),
  },
  {
    title: "金额",
    dataIndex: "amount",
    key: "amount",
    render: (v: number) => <Text strong>¥{Number(v).toFixed(2)}</Text>,
  },
  {
    title: "支付方式",
    dataIndex: "payment_method",
    key: "payment_method",
    render: (v: string | null) => {
      if (!v) return "-";
      const pm = PAYMENT_METHOD_MAP[v];
      return pm ? (
        <Space>
          <span style={{ color: pm.color }}>{pm.icon}</span>
          <span>{pm.label}</span>
        </Space>
      ) : (
        v
      );
    },
  },
  {
    title: "状态",
    dataIndex: "status",
    key: "status",
    render: (v: string) => {
      const s = STATUS_MAP[v];
      return s ? <Tag color={s.color}>{s.label}</Tag> : v;
    },
  },
  {
    title: "创建时间",
    dataIndex: "created_at",
    key: "created_at",
    render: (v: string) => (v ? new Date(v).toLocaleString("zh-CN") : "-"),
  },
];

export default function MembershipPage() {
  const [tierData, setTierData] = useState<TierListResponse | null>(null);
  const [membership, setMembership] = useState<MembershipInfo | null>(null);
  const [orders, setOrders] = useState<OrderInfo[]>([]);
  const [payModal, setPayModal] = useState<{
    open: boolean;
    tier: string;
    name: string;
    amount: number;
  }>({ open: false, tier: "", name: "", amount: 0 });

  const fetchMembership = useCallback(async () => {
    try {
      const [tiersRes, membershipRes, ordersRes] = await Promise.all([
        api.get("/api/payment/tiers"),
        api.get("/api/payment/membership"),
        api.get("/api/payment/orders"),
      ]);
      setTierData(tiersRes.data);
      setMembership(membershipRes.data);
      setOrders(ordersRes.data);
    } catch {
      // 静默失败
    }
  }, []);

  useEffect(() => {
    (async () => {
      try {
        const [tiersRes, membershipRes, ordersRes] = await Promise.all([
          api.get("/api/payment/tiers"),
          api.get("/api/payment/membership"),
          api.get("/api/payment/orders"),
        ]);
        setTierData(tiersRes.data);
        setMembership(membershipRes.data);
        setOrders(ordersRes.data);
      } catch {
        // 静默失败
      }
    })();
  }, []);

  return (
    <Space orientation="vertical" size={24} style={{ width: "100%" }}>
      <div>
        <Title level={3} style={{ margin: "0 0 4px" }}>
          会员中心
        </Title>
        <Text type="secondary">管理你的会员订阅，解锁更多功能</Text>
      </div>

      {/* 当前会员状态 */}
      <Card
        style={{
          borderRadius: 12,
          background:
            membership?.tier !== MembershipTier.FREE
              ? TIER_GRADIENTS[membership?.tier || "free"]
              : "var(--zy-muted)",
          border: "none",
          color: membership?.tier !== MembershipTier.FREE ? "white" : undefined,
        }}
      >
        <Row align="middle" gutter={24}>
          <Col>
            <div
              style={{
                width: 64,
                height: 64,
                borderRadius: 16,
                background: "rgba(255,255,255,0.2)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
              }}
            >
              <CrownOutlined style={{ fontSize: 32 }} />
            </div>
          </Col>
          <Col flex={1}>
            <Title
              level={4}
              style={{
                margin: 0,
                color:
                  membership?.tier !== MembershipTier.FREE
                    ? "white"
                    : "var(--zy-text)",
              }}
            >
              {membership?.name || "免费版"}
            </Title>
            {membership?.expires_at && membership.days_remaining !== null && (
              <Space style={{ marginTop: 4 }}>
                <ClockCircleOutlined />
                <Text
                  style={{
                    color:
                      membership.tier !== MembershipTier.FREE
                        ? "rgba(255,255,255,0.85)"
                        : "var(--zy-text-secondary)",
                  }}
                >
                  有效期至{" "}
                  {new Date(membership.expires_at).toLocaleDateString("zh-CN")}
                  {membership.days_remaining !== undefined && (
                    <>（剩余 {membership.days_remaining} 天）</>
                  )}
                </Text>
              </Space>
            )}
            {membership?.tier === MembershipTier.FREE && (
              <Text type="secondary" style={{ display: "block", marginTop: 4 }}>
                升级会员解锁更多功能
              </Text>
            )}
          </Col>
        </Row>
      </Card>

      {/* 定价卡片 */}
      <Row gutter={[16, 16]}>
        {tierData?.tiers.map((tier) => (
          <Col xs={24} sm={12} lg={6} key={tier.tier}>
            <Card
              className={
                tier.recommended
                  ? "zy-pricing-card zy-pricing-card-highlighted"
                  : "zy-pricing-card"
              }
              style={{
                borderRadius: 12,
                border: tier.recommended
                  ? "2px solid #7C3AED"
                  : "1px solid var(--zy-border)",
                height: "100%",
                position: "relative",
                overflow: "hidden",
              }}
            >
              {tier.recommended && (
                <div
                  style={{
                    position: "absolute",
                    top: 12,
                    right: -28,
                    background: "#7C3AED",
                    color: "white",
                    padding: "2px 32px",
                    fontSize: 12,
                    fontWeight: 500,
                    transform: "rotate(45deg)",
                  }}
                >
                  推荐
                </div>
              )}

              <div style={{ textAlign: "center", marginBottom: 16 }}>
                <Tag
                  color={TIER_COLORS[tier.tier]}
                  style={{ borderRadius: 4, marginBottom: 8 }}
                >
                  {tier.name}
                </Tag>
                <div>
                  {tier.price > 0 ? (
                    <>
                      <span
                        style={{
                          fontSize: 32,
                          fontWeight: 700,
                          color: "var(--zy-text)",
                        }}
                      >
                        ¥{tier.price}
                      </span>
                      <Text type="secondary">/{tier.period || "月"}</Text>
                    </>
                  ) : (
                    <span
                      style={{
                        fontSize: 32,
                        fontWeight: 700,
                        color: "var(--zy-text-secondary)",
                      }}
                    >
                      免费
                    </span>
                  )}
                </div>
              </div>

              <div
                style={{
                  borderTop: "1px solid var(--zy-border-light)",
                  paddingTop: 12,
                  marginBottom: 16,
                }}
              >
                <Space
                  orientation="vertical"
                  size={6}
                  style={{ width: "100%" }}
                >
                  {tier.features.map((f, i) => (
                    <div
                      key={i}
                      style={{
                        display: "flex",
                        alignItems: "flex-start",
                        gap: 8,
                      }}
                    >
                      <CheckOutlined
                        style={{
                          color: TIER_COLORS[tier.tier],
                          marginTop: 3,
                          flexShrink: 0,
                        }}
                      />
                      <Text style={{ fontSize: 13 }}>{f}</Text>
                    </div>
                  ))}
                </Space>
              </div>

              <div style={{ marginTop: "auto" }}>
                {tier.current ? (
                  <Button block disabled style={{ borderRadius: 8 }}>
                    当前方案
                  </Button>
                ) : tier.tier === MembershipTier.FREE ? (
                  <Tooltip title="免费版无需购买">
                    <Button block disabled style={{ borderRadius: 8 }}>
                      免费使用
                    </Button>
                  </Tooltip>
                ) : (
                  <Button
                    type={tier.recommended ? "primary" : "default"}
                    block
                    onClick={() =>
                      setPayModal({
                        open: true,
                        tier: tier.tier,
                        name: tier.name,
                        amount: Number(tier.price),
                      })
                    }
                    style={{
                      borderRadius: 8,
                      fontWeight: 500,
                      background: tier.recommended
                        ? TIER_GRADIENTS[tier.tier]
                        : undefined,
                      border: tier.recommended ? "none" : undefined,
                    }}
                  >
                    立即开通
                  </Button>
                )}
              </div>
            </Card>
          </Col>
        ))}
      </Row>

      {/* 订单历史 */}
      <Card
        title="订单记录"
        style={{ borderRadius: 12, border: "1px solid var(--zy-border)" }}
      >
        <Table
          dataSource={orders}
          columns={orderColumns}
          rowKey="order_id"
          pagination={{ pageSize: 5, size: "small" }}
          size="small"
          locale={{ emptyText: "暂无订单记录" }}
        />
      </Card>

      <PaymentModal
        open={payModal.open}
        tier={payModal.tier}
        tierName={payModal.name}
        amount={payModal.amount}
        onClose={() =>
          setPayModal({ open: false, tier: "", name: "", amount: 0 })
        }
        onSuccess={() => {
          setPayModal({ open: false, tier: "", name: "", amount: 0 });
          fetchMembership();
        }}
      />
    </Space>
  );
}
