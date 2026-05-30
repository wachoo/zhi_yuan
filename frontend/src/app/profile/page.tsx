"use client";

import { useEffect, useState } from "react";
import {
  Card, Form, Select, Button, Progress, message, Space, Row, Col,
  InputNumber, Checkbox, Slider, Divider,
} from "antd";
import api from "@/lib/api";
import AppLayout from "@/components/Layout";
import { UserProfile, SUBJECT_TYPE_OPTIONS, EXAM_TYPE_OPTIONS } from "@/types";

const interests = [
  "计算机", "编程", "设计", "音乐", "运动", "阅读", "数学", "物理",
  "化学", "生物", "经济", "法律", "医学", "教育", "艺术", "机械",
  "表演", "体育", "手工",
];

const dislikes = [
  "编程", "数学", "物理", "化学", "生物", "设计", "绘画", "音乐",
  "背诵", "写作", "实验", "解剖", "户外工作", "出差", "加班", "夜班",
  "机械操作", "手工", "表演", "体育", "销售", "会计",
];

const cities = ["北京", "上海", "广州", "深圳", "杭州", "南京", "成都", "武汉", "西安", "长沙"];

const provinces = [
  "北京", "天津", "上海", "重庆", "河北", "山西", "辽宁", "吉林", "黑龙江",
  "江苏", "浙江", "安徽", "福建", "江西", "山东", "河南", "湖北", "湖南",
  "广东", "海南", "四川", "贵州", "云南", "陕西", "甘肃", "青海", "台湾",
  "内蒙古", "广西", "西藏", "宁夏", "新疆", "香港", "澳门",
];

export default function ProfilePage() {
  const [form] = Form.useForm();
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const res = await api.get("/api/profile");
        const data = res.data as UserProfile;
        setProfile(data);

        // 回显表单数据
        const initialValues: Record<string, unknown> = {};

        if (data.basic_info) {
          initialValues.score = data.basic_info.score;
          initialValues.rank = data.basic_info.rank;
          initialValues.province = data.basic_info.province;
          initialValues.subject_type = data.basic_info.subject_type;
          initialValues.exam_type = data.basic_info.exam_type;
        }
        if (data.personality) {
          initialValues.interests = (data.personality as Record<string, unknown>).interests;
          initialValues.dislikes = (data.personality as Record<string, unknown>).dislikes;
        }
        if (data.family_info) {
          initialValues.tuition_max = (data.family_info as Record<string, unknown>).tuition_max;
          initialValues.prefer_city = (data.family_info as Record<string, unknown>).prefer_city;
        }
        if (data.ability) {
          initialValues.strong_subjects = (data.ability as Record<string, unknown>).strong_subjects;
          initialValues.social_ability = (data.ability as Record<string, unknown>).social_ability;
          initialValues.english_level = (data.ability as Record<string, unknown>).english_level;
        }
        if (data.values_info) {
          initialValues.career_values = (data.values_info as Record<string, unknown>).career_values;
          initialValues.distance_preference = (data.values_info as Record<string, unknown>).distance_preference;
          initialValues.plan = (data.values_info as Record<string, unknown>).plan;
        }

        form.setFieldsValue(initialValues);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchProfile();
  }, [form]);

  const onSave = async (values: Record<string, unknown>) => {
    setSaving(true);
    try {
      const updateData: Record<string, unknown> = {};

      // basic_info
      if (values.score != null || values.rank != null || values.province || values.subject_type || values.exam_type) {
        updateData.basic_info = {
          score: values.score,
          rank: values.rank,
          province: values.province,
          subject_type: values.subject_type,
          exam_type: values.exam_type,
        };
      }

      // family_info + personality
      updateData.family_info = {
        tuition_max: values.tuition_max,
        prefer_city: values.prefer_city,
      };
      updateData.personality = {
        interests: values.interests,
        dislikes: values.dislikes,
      };

      // ability
      updateData.ability = {
        strong_subjects: values.strong_subjects,
        social_ability: values.social_ability,
        english_level: values.english_level,
      };

      // values_info
      updateData.values_info = {
        career_values: values.career_values,
        distance_preference: values.distance_preference,
        plan: values.plan,
      };

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

        <Form form={form} layout="vertical" onFinish={onSave}>
          <Card title="基本信息">
            <Row gutter={16}>
              <Col span={6}>
                <Form.Item name="score" label="高考分数" rules={[{ required: true, message: "请输入分数" }]}>
                  <InputNumber min={0} max={750} style={{ width: "100%" }} placeholder="如：620" />
                </Form.Item>
              </Col>
              <Col span={6}>
                <Form.Item name="rank" label="省排名" rules={[{ required: true, message: "请输入排名" }]}>
                  <InputNumber min={0} style={{ width: "100%" }} placeholder="如：5000" />
                </Form.Item>
              </Col>
              <Col span={6}>
                <Form.Item name="province" label="省份" rules={[{ required: true, message: "请选择省份" }]}>
                  <Select
                    showSearch
                    placeholder="选择省份"
                    options={provinces.map((p) => ({ value: p, label: p }))}
                    filterOption={(input, option) =>
                      (option?.label as string)?.includes(input) ?? false
                    }
                  />
                </Form.Item>
              </Col>
              <Col span={6}>
                <Form.Item name="subject_type" label="科类" rules={[{ required: true, message: "请选择科类" }]}>
                  <Select
                    placeholder="选择科类"
                    options={SUBJECT_TYPE_OPTIONS}
                  />
                </Form.Item>
              </Col>
            </Row>
            <Row gutter={16}>
              <Col span={6}>
                <Form.Item name="exam_type" label="考试科类">
                  <Select
                    placeholder="选择考试科类"
                    options={EXAM_TYPE_OPTIONS}
                    allowClear
                  />
                </Form.Item>
              </Col>
            </Row>
          </Card>

          <Card title="兴趣与偏好" style={{ marginTop: 16 }}>
            <Form.Item name="interests" label="兴趣爱好">
              <Select
                mode="tags"
                placeholder="从列表选择，或输入自定义关键词后回车添加"
                style={{ width: "100%" }}
                options={interests.map((i) => ({ value: i, label: i }))}
              />
            </Form.Item>
            <Form.Item name="dislikes" label="厌恶领域">
              <Select
                mode="tags"
                placeholder="从列表选择，或输入自定义关键词后回车添加（如：编程、数学、实验等）"
                style={{ width: "100%" }}
                options={dislikes.map((d) => ({ value: d, label: d }))}
              />
            </Form.Item>
            <Row gutter={16}>
              <Col span={12}>
                <Form.Item name="prefer_city" label="偏好城市">
                  <Select
                    mode="multiple"
                    placeholder="选择你偏好的城市（可多选）"
                    options={cities.map((c) => ({ value: c, label: c }))}
                  />
                </Form.Item>
              </Col>
              <Col span={12}>
                <Form.Item name="tuition_max" label="可接受最高学费（元/年）">
                  <InputNumber min={0} max={200000} style={{ width: "100%" }} placeholder="如：10000" />
                </Form.Item>
              </Col>
            </Row>
          </Card>

          <Card title="能力评估" style={{ marginTop: 16 }}>
            <Form.Item name="strong_subjects" label="擅长科目">
              <Select
                mode="tags"
                placeholder="输入擅长科目后回车添加"
                style={{ width: "100%" }}
              />
            </Form.Item>
            <Row gutter={16}>
              <Col span={12}>
                <Form.Item name="social_ability" label="社交能力（1=内向，5=外向）">
                  <Slider min={1} max={5} marks={{ 1: "内向", 2: "", 3: "适中", 4: "", 5: "外向" }} />
                </Form.Item>
              </Col>
              <Col span={12}>
                <Form.Item name="english_level" label="英语水平（1=基础，6=精通）">
                  <Slider min={1} max={6} marks={{ 1: "基础", 2: "", 3: "中等", 4: "", 5: "良好", 6: "精通" }} />
                </Form.Item>
              </Col>
            </Row>
          </Card>

          <Card title="价值观与规划" style={{ marginTop: 16 }}>
            <Form.Item name="career_values" label="职业价值观">
              <Checkbox.Group options={["高薪", "稳定", "社会价值", "自由", "创造力"]} />
            </Form.Item>
            <Row gutter={16}>
              <Col span={12}>
                <Form.Item name="distance_preference" label="是否接受外地求学">
                  <Select options={[
                    { value: "接受外地", label: "接受外地" },
                    { value: "尽量省内", label: "尽量省内" },
                    { value: "只看省内", label: "只看省内" },
                  ]} />
                </Form.Item>
              </Col>
              <Col span={12}>
                <Form.Item name="plan" label="未来规划">
                  <Select options={[
                    { value: "直接就业", label: "直接就业" },
                    { value: "考研", label: "考研" },
                    { value: "出国", label: "出国" },
                    { value: "考公", label: "考公" },
                    { value: "还没想好", label: "还没想好" },
                  ]} />
                </Form.Item>
              </Col>
            </Row>
            <Divider />
            <Form.Item>
              <Button type="primary" htmlType="submit" loading={saving} size="large">保存</Button>
            </Form.Item>
          </Card>
        </Form>
      </Space>
    </AppLayout>
  );
}
