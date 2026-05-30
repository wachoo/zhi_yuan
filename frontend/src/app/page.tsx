"use client";

import { useState } from "react";
import { Card, Form, InputNumber, Select, Button, Typography, Row, Col, Space } from "antd";
import { ArrowRightOutlined, AimOutlined, StarFilled, SafetyCertificateOutlined, RobotOutlined } from "@ant-design/icons";
import { useRouter } from "next/navigation";
import api from "@/lib/api";
import AppLayout from "@/components/Layout";
import { SUBJECT_TYPE_OPTIONS, EXAM_TYPE_OPTIONS } from "@/types";

const { Title, Text } = Typography;

const provinces = [
  "北京", "天津", "上海", "重庆", "河北", "山西", "辽宁", "吉林", "黑龙江",
  "江苏", "浙江", "安徽", "福建", "江西", "山东", "河南", "湖北", "湖南",
  "广东", "海南", "四川", "贵州", "云南", "陕西", "甘肃", "青海", "内蒙古",
  "广西", "西藏", "宁夏", "新疆",
];

export default function Home() {
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const onFinish = async (values: { score: number; rank: number; province: string; subject_type: string; exam_type: string }) => {
    setLoading(true);
    try {
      const token = localStorage.getItem("token");
      if (!token) {
        const res = await api.post("/api/auth/register", {
          phone: "13800138000",
          password: "test123",
        }).catch(() => api.post("/api/auth/login", { phone: "13800138000", password: "test123" }));
        localStorage.setItem("token", res.data.access_token);
      }

      await api.put("/api/profile", { basic_info: values });
      const params = new URLSearchParams({
        score: String(values.score),
        rank: String(values.rank),
        province: values.province,
        subject_type: values.subject_type,
        exam_type: values.exam_type || "普通类",
      });
      router.push(`/recommend?${params}`);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <AppLayout>
      <Space direction="vertical" size={32} style={{ width: "100%" }}>
        {/* Hero + Form */}
        <Row gutter={32} align="middle">
          <Col xs={24} lg={12}>
            <div className="zy-hero">
              <Title level={1} style={{ color: "white", fontSize: 32, margin: "0 0 16px" }}>
                你的AI高考志愿助手
              </Title>
              <Text style={{ color: "rgba(255,255,255,0.9)", fontSize: 16, lineHeight: 1.8, display: "block", marginBottom: 32 }}>
                基于 37 万+ 真实录取数据，结合六维画像分析，<br />
                为你精准定位冲/稳/保院校组合
              </Text>
              <div style={{ display: "flex", gap: 32, position: "relative", zIndex: 1 }}>
                {[
                  { icon: <AimOutlined />, text: "精准定位" },
                  { icon: <StarFilled />, text: "智能推荐" },
                  { icon: <RobotOutlined />, text: "AI顾问" },
                ].map((item) => (
                  <div key={item.text} style={{ display: "flex", alignItems: "center", gap: 8 }}>
                    <span style={{ fontSize: 18 }}>{item.icon}</span>
                    <span style={{ fontSize: 14 }}>{item.text}</span>
                  </div>
                ))}
              </div>
            </div>
          </Col>
          <Col xs={24} lg={12}>
            <div className="zy-form-card" style={{ marginTop: 24 }}>
              <Title level={4} style={{ margin: "0 0 4px" }}>快速获取推荐方案</Title>
              <Text style={{ color: "var(--zy-text-secondary)", display: "block", marginBottom: 24 }}>
                输入你的高考信息，立即生成个性化志愿方案
              </Text>

              <Form layout="vertical" onFinish={onFinish} size="large">
                <Row gutter={16}>
                  <Col span={12}>
                    <Form.Item name="score" label="高考分数" rules={[{ required: true, message: "请输入分数" }]}>
                      <InputNumber min={0} max={750} style={{ width: "100%" }} placeholder="满分750" />
                    </Form.Item>
                  </Col>
                  <Col span={12}>
                    <Form.Item name="rank" label="省排名（位次）" rules={[{ required: true, message: "请输入位次" }]}>
                      <InputNumber min={1} style={{ width: "100%" }} placeholder="如：5000" />
                    </Form.Item>
                  </Col>
                </Row>
                <Form.Item name="province" label="所在省份" rules={[{ required: true, message: "请选择省份" }]}>
                  <Select
                    placeholder="选择省份"
                    showSearch
                    filterOption={(input, option) =>
                      (option?.label ?? "").toLowerCase().includes(input.toLowerCase())
                    }
                    options={provinces.map((p) => ({ value: p, label: p }))}
                  />
                </Form.Item>
                <Row gutter={16}>
                  <Col span={12}>
                    <Form.Item name="subject_type" label="科类" rules={[{ required: true, message: "请选择科类" }]}>
                      <Select placeholder="选择科类" options={SUBJECT_TYPE_OPTIONS} />
                    </Form.Item>
                  </Col>
                  <Col span={12}>
                    <Form.Item name="exam_type" label="考试科类" initialValue="普通类">
                      <Select placeholder="选择考试科类" options={EXAM_TYPE_OPTIONS} />
                    </Form.Item>
                  </Col>
                </Row>
                <Form.Item style={{ marginBottom: 0 }}>
                  <Button
                    type="primary"
                    htmlType="submit"
                    block
                    loading={loading}
                    icon={<ArrowRightOutlined />}
                    iconPosition="end"
                    style={{ height: 48, fontSize: 16, fontWeight: 600, borderRadius: 10 }}
                  >
                    获取推荐方案
                  </Button>
                </Form.Item>
              </Form>
            </div>
          </Col>
        </Row>

        {/* Feature highlights */}
        <Row gutter={24}>
          {[
            {
              icon: <AimOutlined style={{ fontSize: 28, color: "var(--zy-primary)" }} />,
              title: "精准定位",
              desc: "基于 37 万+ 历年录取数据，位次换算精准匹配",
            },
            {
              icon: <StarFilled style={{ fontSize: 28, color: "var(--zy-accent)" }} />,
              title: "六维画像",
              desc: "基础·家庭·城市·性格·能力·价值观全面分析",
            },
            {
              icon: <SafetyCertificateOutlined style={{ fontSize: 28, color: "var(--zy-secondary)" }} />,
              title: "冲/稳/保",
              desc: "科学梯度分类，降低志愿填报风险",
            },
            {
              icon: <RobotOutlined style={{ fontSize: 28, color: "#7C3AED" }} />,
              title: "AI顾问",
              desc: "24小时在线，查询院校、专业、录取信息",
            },
          ].map((feature) => (
            <Col xs={12} sm={12} md={6} key={feature.title}>
              <Card
                style={{
                  borderRadius: 12,
                  border: "1px solid var(--zy-border)",
                  textAlign: "center",
                  height: "100%",
                }}
                styles={{ body: { padding: "28px 20px" } }}
              >
                <div style={{ marginBottom: 16 }}>{feature.icon}</div>
                <Title level={5} style={{ margin: "0 0 8px" }}>{feature.title}</Title>
                <Text style={{ color: "var(--zy-text-secondary)", fontSize: 13 }}>
                  {feature.desc}
                </Text>
              </Card>
            </Col>
          ))}
        </Row>
      </Space>
    </AppLayout>
  );
}
