"use client";

import { useState } from "react";
import { Card, Form, InputNumber, Select, Button, Typography, Space, Row, Col } from "antd";
import { RocketOutlined } from "@ant-design/icons";
import { useRouter } from "next/navigation";
import api from "@/lib/api";
import AppLayout from "@/components/Layout";
import { SUBJECT_TYPE_OPTIONS } from "@/types";

const { Title, Paragraph } = Typography;

const provinces = [
  "北京", "天津", "上海", "重庆", "河北", "山西", "辽宁", "吉林", "黑龙江",
  "江苏", "浙江", "安徽", "福建", "江西", "山东", "河南", "湖北", "湖南",
  "广东", "海南", "四川", "贵州", "云南", "陕西", "甘肃", "青海", "内蒙古",
  "广西", "西藏", "宁夏", "新疆",
];

export default function Home() {
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const onFinish = async (values: { score: number; rank: number; province: string; subject_type: string }) => {
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
      router.push(`/recommend?score=${values.score}&rank=${values.rank}&province=${values.province}&subject_type=${values.subject_type}`);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <AppLayout>
      <Row justify="center" style={{ marginTop: 60 }}>
        <Col xs={24} md={16} lg={12}>
          <Card>
            <Space direction="vertical" size="large" style={{ width: "100%" }}>
              <Title level={2} style={{ textAlign: "center" }}>
                <RocketOutlined /> 智愿 — 你的AI高考志愿助手
              </Title>
              <Paragraph style={{ textAlign: "center", fontSize: 16 }}>
                输入你的高考信息，立即获取冲/稳/保院校推荐方案
              </Paragraph>

              <Form layout="vertical" onFinish={onFinish} size="large">
                <Form.Item name="score" label="高考分数" rules={[{ required: true, message: "请输入分数" }]}>
                  <InputNumber min={0} max={750} style={{ width: "100%" }} placeholder="满分750" />
                </Form.Item>
                <Form.Item name="rank" label="省排名（位次）" rules={[{ required: true, message: "请输入位次" }]}>
                  <InputNumber min={1} style={{ width: "100%" }} placeholder="如：5000" />
                </Form.Item>
                <Form.Item name="province" label="所在省份" rules={[{ required: true, message: "请选择省份" }]}>
                  <Select placeholder="选择省份" options={provinces.map((p) => ({ value: p, label: p }))} />
                </Form.Item>
                <Form.Item name="subject_type" label="科类" rules={[{ required: true, message: "请选择科类" }]}>
                  <Select placeholder="选择科类" options={SUBJECT_TYPE_OPTIONS} />
                </Form.Item>
                <Form.Item>
                  <Button type="primary" htmlType="submit" block loading={loading} size="large">
                    获取推荐方案
                  </Button>
                </Form.Item>
              </Form>
            </Space>
          </Card>
        </Col>
      </Row>
    </AppLayout>
  );
}
