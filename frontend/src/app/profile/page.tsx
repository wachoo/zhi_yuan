"use client";

import { useEffect, useState } from "react";
import { Card, Form, Select, Button, Progress, message, Space, Row, Col, InputNumber, Checkbox, Input } from "antd";
import api from "@/lib/api";
import AppLayout from "@/components/Layout";
import { UserProfile } from "@/types";

const interests = [
  "计算机", "编程", "设计", "音乐", "运动", "阅读", "数学", "物理",
  "化学", "生物", "经济", "法律", "医学", "教育", "艺术", "机械",
];

const cities = ["北京", "上海", "广州", "深圳", "杭州", "南京", "成都", "武汉", "西安", "长沙"];

export default function ProfilePage() {
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const res = await api.get("/api/profile");
        setProfile(res.data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchProfile();
  }, []);

  const onSave = async (values: Record<string, unknown>) => {
    setSaving(true);
    try {
      const updateData: Record<string, unknown> = {};
      if (values.interests || values.prefer_city || values.tuition_max) {
        updateData.family_info = {
          tuition_max: values.tuition_max,
          prefer_city: values.prefer_city,
        };
        updateData.personality = {
          interests: values.interests,
        };
      }
      if (values.career_values || values.distance_preference || values.plan) {
        updateData.values_info = {
          career_values: values.career_values,
          distance_preference: values.distance_preference,
          plan: values.plan,
        };
      }
      const res = await api.put("/api/profile", updateData);
      message.success(`画像已更新，完整度: ${Math.round(res.data.completeness * 100)}%`);
      setProfile((prev) => prev ? { ...prev, completeness: res.data.completeness } : prev);
    } catch (err) {
      message.error("保存失败");
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <AppLayout><Card loading /></AppLayout>;

  return (
    <AppLayout>
      <Space direction="vertical" size="large" style={{ width: "100%" }}>
        <Card title="画像完整度">
          <Progress percent={Math.round((profile?.completeness || 0) * 100)} />
          <p>完善更多维度的信息，获得更精准的推荐</p>
        </Card>

        <Card title="兴趣与偏好">
          <Form layout="vertical" onFinish={onSave}>
            <Form.Item name="interests" label="兴趣爱好">
              <Checkbox.Group>
                <Row>
                  {interests.map((i) => (
                    <Col span={6} key={i}><Checkbox value={i}>{i}</Checkbox></Col>
                  ))}
                </Row>
              </Checkbox.Group>
            </Form.Item>
            <Form.Item name="prefer_city" label="偏好城市">
              <Select mode="multiple" placeholder="选择你偏好的城市（可多选）"
                options={cities.map((c) => ({ value: c, label: c }))} />
            </Form.Item>
            <Form.Item name="tuition_max" label="可接受最高学费（元/年）">
              <InputNumber min={0} max={200000} style={{ width: "100%" }} placeholder="如：10000" />
            </Form.Item>
            <Form.Item name="career_values" label="职业价值观">
              <Checkbox.Group options={["高薪", "稳定", "社会价值", "自由", "创造力"]} />
            </Form.Item>
            <Form.Item name="distance_preference" label="是否接受外地求学">
              <Select options={[
                { value: "接受外地", label: "接受外地" },
                { value: "尽量省内", label: "尽量省内" },
                { value: "只看省内", label: "只看省内" },
              ]} />
            </Form.Item>
            <Form.Item name="plan" label="未来规划">
              <Select options={[
                { value: "直接就业", label: "直接就业" },
                { value: "考研", label: "考研" },
                { value: "出国", label: "出国" },
                { value: "考公", label: "考公" },
                { value: "还没想好", label: "还没想好" },
              ]} />
            </Form.Item>
            <Form.Item>
              <Button type="primary" htmlType="submit" loading={saving}>保存</Button>
            </Form.Item>
          </Form>
        </Card>
      </Space>
    </AppLayout>
  );
}
