"use client";

import { useState } from "react";
import {
  Card,
  Form,
  InputNumber,
  Select,
  Button,
  Typography,
  Row,
  Col,
  Divider,
} from "antd";
import {
  ArrowRightOutlined,
  AimOutlined,
  BarChartOutlined,
  TeamOutlined,
  SafetyCertificateOutlined,
  RobotOutlined,
  DatabaseOutlined,
  ThunderboltOutlined,
} from "@ant-design/icons";
import { useRouter } from "next/navigation";
import api from "@/lib/api";
import AppLayout from "@/components/Layout";
import { SUBJECT_TYPE_OPTIONS, EXAM_TYPE_OPTIONS } from "@/types";

const { Title, Text, Paragraph } = Typography;

const provinces = [
  "北京",
  "天津",
  "上海",
  "重庆",
  "河北",
  "山西",
  "辽宁",
  "吉林",
  "黑龙江",
  "江苏",
  "浙江",
  "安徽",
  "福建",
  "江西",
  "山东",
  "河南",
  "湖北",
  "湖南",
  "广东",
  "海南",
  "四川",
  "贵州",
  "云南",
  "陕西",
  "甘肃",
  "青海",
  "内蒙古",
  "广西",
  "西藏",
  "宁夏",
  "新疆",
];

const stats = [
  { value: "37万+", label: "历年录取数据" },
  { value: "3000+", label: "覆盖院校" },
  { value: "6维", label: "画像分析" },
  { value: "95%", label: "推荐准确率" },
];

const features = [
  {
    icon: (
      <DatabaseOutlined
        style={{ fontSize: 22, color: "var(--zy-secondary)" }}
      />
    ),
    bg: "rgba(37, 99, 235, 0.08)",
    title: "海量数据支撑",
    desc: "整合全国 3000+ 院校历年录取分数线、位次数据，数据驱动精准匹配",
  },
  {
    icon: (
      <BarChartOutlined style={{ fontSize: 22, color: "var(--zy-accent)" }} />
    ),
    bg: "rgba(5, 150, 105, 0.08)",
    title: "六维画像评估",
    desc: "基础·家庭·城市·兴趣·能力·价值观，全方位评估院校适配度",
  },
  {
    icon: (
      <SafetyCertificateOutlined
        style={{ fontSize: 22, color: "var(--zy-rush)" }}
      />
    ),
    bg: "rgba(239, 68, 68, 0.08)",
    title: "冲/稳/保梯度",
    desc: "科学划分冲刺、稳妥、保底三档，降低志愿填报滑档风险",
  },
  {
    icon: <RobotOutlined style={{ fontSize: 22, color: "#7C3AED" }} />,
    bg: "rgba(124, 58, 237, 0.08)",
    title: "AI志愿顾问",
    desc: "多风格 AI 顾问随时在线，智能问答院校、专业、就业等信息",
  },
  {
    icon: <TeamOutlined style={{ fontSize: 22, color: "#D97706" }} />,
    bg: "rgba(217, 119, 6, 0.08)",
    title: "家庭因素融合",
    desc: "综合学费承受力、城市偏好、赡养需求等家庭因素智能推荐",
  },
  {
    icon: (
      <ThunderboltOutlined
        style={{ fontSize: 22, color: "var(--zy-primary)" }}
      />
    ),
    bg: "rgba(30, 58, 95, 0.08)",
    title: "极速生成方案",
    desc: "输入基本信息即可秒级生成个性化志愿方案，支持在线调整优化",
  },
];

export default function Home() {
  const [loading, setLoading] = useState(false);
  const [examType, setExamType] = useState("普通类");
  const router = useRouter();

  const onFinish = async (values: {
    score: number;
    rank: number;
    province: string;
    subject_type: string;
    exam_type: string;
    professional_score?: number;
  }) => {
    setLoading(true);
    try {
      const token = localStorage.getItem("token");
      if (!token) {
        const params = new URLSearchParams();
        params.set("score", String(values.score));
        params.set("rank", String(values.rank));
        params.set("province", values.province);
        params.set("subject_type", values.subject_type);
        params.set("exam_type", values.exam_type || "普通类");
        if (values.professional_score) {
          params.set("professional_score", String(values.professional_score));
        }
        router.push(
          `/login?redirect=/recommend?${encodeURIComponent(params.toString())}`,
        );
        return;
      }

      await api.put("/api/profile", { basic_info: values });
      const params = new URLSearchParams({
        score: String(values.score),
        rank: String(values.rank),
        province: values.province,
        subject_type: values.subject_type,
        exam_type: values.exam_type || "普通类",
      });
      if (values.professional_score) {
        params.set("professional_score", String(values.professional_score));
      }
      router.push(`/recommend?${params}`);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <AppLayout>
      {/* Hero Section */}
      <div style={{ textAlign: "center", padding: "16px 0 40px" }}>
        <div
          style={{
            display: "inline-flex",
            alignItems: "center",
            gap: 8,
            background: "rgba(37, 99, 235, 0.06)",
            border: "1px solid rgba(37, 99, 235, 0.12)",
            borderRadius: 20,
            padding: "6px 16px",
            marginBottom: 24,
          }}
        >
          <AimOutlined style={{ color: "var(--zy-secondary)", fontSize: 14 }} />
          <span
            style={{
              fontSize: 13,
              color: "var(--zy-secondary)",
              fontWeight: 500,
            }}
          >
            AI 驱动的高考志愿智能推荐平台
          </span>
        </div>
        <Title
          level={1}
          style={{
            fontSize: 40,
            fontWeight: 700,
            margin: "0 0 16px",
            lineHeight: 1.3,
            background:
              "linear-gradient(135deg, var(--zy-primary) 0%, var(--zy-secondary) 100%)",
            WebkitBackgroundClip: "text",
            WebkitTextFillColor: "transparent",
          }}
        >
          科学填报，精准定位理想院校
        </Title>
        <Paragraph
          style={{
            fontSize: 16,
            color: "var(--zy-text-secondary)",
            maxWidth: 560,
            margin: "0 auto 36px",
            lineHeight: 1.8,
          }}
        >
          基于 37 万+
          真实录取数据，结合六维画像分析，为你智能生成冲/稳/保梯度志愿方案
        </Paragraph>

        {/* Stats bar */}
        <div
          style={{
            display: "flex",
            justifyContent: "center",
            gap: 48,
            flexWrap: "wrap",
          }}
        >
          {stats.map((s) => (
            <div key={s.label} style={{ textAlign: "center" }}>
              <div
                style={{
                  fontSize: 26,
                  fontWeight: 700,
                  color: "var(--zy-primary)",
                  lineHeight: 1.2,
                }}
              >
                {s.value}
              </div>
              <div
                style={{
                  fontSize: 13,
                  color: "var(--zy-text-muted)",
                  marginTop: 4,
                }}
              >
                {s.label}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Form Section */}
      <div
        style={{
          maxWidth: 680,
          margin: "0 auto 48px",
          background: "var(--zy-surface)",
          borderRadius: 16,
          padding: "36px 40px",
          boxShadow:
            "0 4px 24px rgba(30, 58, 95, 0.08), 0 1px 3px rgba(15, 23, 42, 0.06)",
          border: "1px solid var(--zy-border-light)",
        }}
      >
        <div style={{ textAlign: "center", marginBottom: 28 }}>
          <Title level={4} style={{ margin: "0 0 6px" }}>
            快速获取推荐方案
          </Title>
          <Text style={{ color: "var(--zy-text-muted)", fontSize: 14 }}>
            填写高考信息，立即生成个性化志愿方案
          </Text>
        </div>

        <Form layout="vertical" onFinish={onFinish} size="large">
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="score"
                label="高考分数"
                rules={[{ required: true, message: "请输入分数" }]}
              >
                <InputNumber
                  min={0}
                  max={750}
                  style={{ width: "100%" }}
                  placeholder="满分750"
                />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="rank"
                label="省排名（位次）"
                rules={[{ required: true, message: "请输入位次" }]}
              >
                <InputNumber
                  min={1}
                  style={{ width: "100%" }}
                  placeholder="如：5000"
                />
              </Form.Item>
            </Col>
          </Row>
          <Form.Item
            name="province"
            label="所在省份"
            rules={[{ required: true, message: "请选择省份" }]}
          >
            <Select
              placeholder="选择省份"
              showSearch
              filterOption={(input, option) =>
                (option?.label ?? "")
                  .toLowerCase()
                  .includes(input.toLowerCase())
              }
              options={provinces.map((p) => ({ value: p, label: p }))}
            />
          </Form.Item>
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="subject_type"
                label="首选科目"
                initialValue="物理类"
                rules={[{ required: true, message: "请选择首选科目" }]}
              >
                <Select
                  placeholder="选择首选科目"
                  options={SUBJECT_TYPE_OPTIONS}
                />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="exam_type"
                label="报考科类"
                initialValue="普通类"
                rules={[{ required: true, message: "请选择报考科类" }]}
              >
                <Select
                  placeholder="选择报考科类"
                  options={EXAM_TYPE_OPTIONS}
                  onChange={(val) => setExamType(val)}
                />
              </Form.Item>
            </Col>
          </Row>
          {(examType === "艺术类" || examType === "体育类") && (
            <Form.Item
              name="professional_score"
              label={examType === "艺术类" ? "艺考专业分" : "体育术科分"}
              rules={[
                {
                  required: true,
                  message: `请输入${examType === "艺术类" ? "艺考" : "体育术科"}专业分`,
                },
              ]}
              extra={
                examType === "艺术类"
                  ? "省级艺术类专业统考成绩"
                  : "省级体育专业统考成绩"
              }
            >
              <InputNumber
                min={0}
                max={400}
                style={{ width: "100%" }}
                placeholder="如：260"
              />
            </Form.Item>
          )}
          <Form.Item style={{ marginBottom: 0 }}>
            <Button
              type="primary"
              htmlType="submit"
              block
              loading={loading}
              icon={<ArrowRightOutlined />}
              iconPlacement="end"
              style={{
                height: 48,
                fontSize: 16,
                fontWeight: 600,
                borderRadius: 10,
              }}
            >
              获取推荐方案
            </Button>
          </Form.Item>
        </Form>
      </div>

      {/* Divider with label */}
      <Divider style={{ margin: "0 0 40px" }}>
        <Text type="secondary" style={{ fontSize: 13 }}>
          平台能力
        </Text>
      </Divider>

      {/* Feature Grid */}
      <Row gutter={[20, 20]} style={{ marginBottom: 16 }}>
        {features.map((f) => (
          <Col xs={24} sm={12} md={8} key={f.title}>
            <Card
              style={{
                borderRadius: 12,
                border: "1px solid var(--zy-border)",
                height: "100%",
              }}
              styles={{ body: { padding: "24px" } }}
            >
              <div
                style={{
                  width: 44,
                  height: 44,
                  borderRadius: 10,
                  background: f.bg,
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  marginBottom: 16,
                }}
              >
                {f.icon}
              </div>
              <Title level={5} style={{ margin: "0 0 8px", fontSize: 15 }}>
                {f.title}
              </Title>
              <Text
                style={{
                  color: "var(--zy-text-secondary)",
                  fontSize: 13,
                  lineHeight: 1.7,
                }}
              >
                {f.desc}
              </Text>
            </Card>
          </Col>
        ))}
      </Row>
    </AppLayout>
  );
}
