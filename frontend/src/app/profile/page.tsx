"use client";

import { useEffect, useState } from "react";
import {
  Card, Form, Select, Button, Progress, message, Space, Row, Col,
  InputNumber, Checkbox, Slider, Radio, Typography, Tabs,
  Input, Modal,
} from "antd";
import {
  LockOutlined,
  UserOutlined,
  HeartOutlined,
  TrophyOutlined,
  AimOutlined,
} from "@ant-design/icons";
import api, { logout } from "@/lib/api";
import AppLayout from "@/components/Layout";
import { UserProfile, SUBJECT_TYPE_OPTIONS, EXAM_TYPE_OPTIONS } from "@/types";

const { Text, Title } = Typography;
const { Password } = Input;

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
  const [pwdForm] = Form.useForm();
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [changingPwd, setChangingPwd] = useState(false);
  const [examType, setExamType] = useState<string | null>(null);

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const res = await api.get("/api/profile");
        const data = res.data as UserProfile;
        setProfile(data);

        const initialValues: Record<string, unknown> = {};

        if (data.basic_info) {
          initialValues.score = data.basic_info.score;
          initialValues.rank = data.basic_info.rank;
          initialValues.province = data.basic_info.province;
          initialValues.subject_type = data.basic_info.subject_type;
          initialValues.exam_type = data.basic_info.exam_type;
          setExamType(data.basic_info.exam_type);
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

  const doSave = async (values: Record<string, unknown>) => {
    setSaving(true);
    try {
      const updateData: Record<string, unknown> = {};

      if (values.score != null || values.rank != null || values.province || values.subject_type || values.exam_type) {
        updateData.basic_info = {
          score: values.score,
          rank: values.rank,
          province: values.province,
          subject_type: values.subject_type,
          exam_type: values.exam_type,
        };
      }

      updateData.family_info = {
        tuition_max: values.tuition_max,
        prefer_city: values.prefer_city,
      };
      updateData.personality = {
        interests: values.interests,
        dislikes: values.dislikes,
      };

      updateData.ability = {
        strong_subjects: values.strong_subjects,
        social_ability: values.social_ability,
        english_level: values.english_level,
      };

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

  const onSave = (values: Record<string, unknown>) => {
    Modal.confirm({
      title: "确认保存",
      content: "是否保存当前个人详情？",
      okText: "确认",
      cancelText: "取消",
      onOk: () => doSave(values),
    });
  };

  const onChangePassword = async (values: Record<string, unknown>) => {
    setChangingPwd(true);
    try {
      await api.put("/api/auth/password", {
        old_password: values.old_password,
        new_password: values.new_password,
      });
      message.success("密码修改成功，即将跳转到登录页...");
      pwdForm.resetFields();
      setTimeout(() => logout(), 1500);
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } } };
      message.error(error.response?.data?.detail || "密码修改失败");
    } finally {
      setChangingPwd(false);
    }
  };

  if (loading) return <AppLayout><Card loading style={{ borderRadius: 12 }} /></AppLayout>;

  const profileTab = (
    <Space direction="vertical" size={24} style={{ width: "100%" }}>
      {/* Completeness card */}
      <Card style={{ borderRadius: 12, border: "1px solid var(--zy-border)" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 20 }}>
          <Progress
            type="circle"
            percent={Math.round((profile?.completeness || 0) * 100)}
            size={80}
            strokeColor="var(--zy-primary)"
          />
          <div>
            <Title level={5} style={{ margin: "0 0 4px" }}>画像完整度</Title>
            <Text type="secondary">完善更多维度的信息，获得更精准的推荐</Text>
          </div>
        </div>
      </Card>

      <Form form={form} layout="vertical" onFinish={onSave}>
        {/* Basic Info */}
        <Card
          title={
            <Space>
              <UserOutlined style={{ color: "var(--zy-primary)" }} />
              <span>基本信息</span>
            </Space>
          }
          style={{ borderRadius: 12, border: "1px solid var(--zy-border)" }}
        >
          <Row gutter={16}>
            <Col xs={12} sm={6}>
              <Form.Item name="score" label="高考分数" rules={[{ required: true, message: "请输入分数" }]}>
                <InputNumber min={0} max={750} style={{ width: "100%" }} placeholder="如：620" />
              </Form.Item>
            </Col>
            <Col xs={12} sm={6}>
              <Form.Item name="rank" label="省排名" rules={[{ required: true, message: "请输入排名" }]}>
                <InputNumber min={0} style={{ width: "100%" }} placeholder="如：5000" />
              </Form.Item>
            </Col>
            <Col xs={12} sm={6}>
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
            <Col xs={12} sm={6}>
              <Form.Item name="subject_type" label="科类" rules={[{ required: true, message: "请选择科类" }]}>
                <Select placeholder="选择科类" options={SUBJECT_TYPE_OPTIONS} />
              </Form.Item>
            </Col>
          </Row>
          <Form.Item name="exam_type" label="考试科类" style={{ marginBottom: 0 }}>
            <Radio.Group
              onChange={(e) => setExamType(e.target.value)}
              style={{ display: "flex", flexDirection: "column", gap: 8 }}
            >
              {EXAM_TYPE_OPTIONS.map((opt) => (
                <Radio
                  key={opt.value}
                  value={opt.value}
                  style={{
                    padding: "12px 16px",
                    borderRadius: 10,
                    border: "1px solid var(--zy-border)",
                    alignItems: "flex-start",
                    transition: "all 0.2s",
                  }}
                >
                  <div>
                    <div style={{ fontWeight: 500 }}>{opt.label}</div>
                    <Text type="secondary" style={{ fontSize: 12, lineHeight: 1.6 }}>
                      {opt.description}
                    </Text>
                  </div>
                </Radio>
              ))}
            </Radio.Group>
          </Form.Item>
          {examType && (
            <div style={{
              marginTop: 12,
              padding: "12px 16px",
              background: "var(--zy-muted)",
              borderRadius: 8,
              fontSize: 13,
              color: "var(--zy-text-secondary)",
              borderLeft: "3px solid var(--zy-primary)",
            }}>
              {examType === "普通类" && <>普通类考生可报考工学、理学、医学、经济学、管理学、法学、文学、历史学、哲学、农学等学科门类的专业，覆盖大部分本科专业。</>}
              {examType === "艺术类" && <>艺术类考生需参加省统考或校考，可报考视觉传达设计、音乐学、美术学、表演、播音与主持艺术、舞蹈学、动画、广播电视编导等艺术类专业。</>}
              {examType === "体育类" && <>体育类考生需参加体育专业测试，可报考体育教育、运动训练、武术与民族传统体育等专业。部分院校体育教育也可通过普通类报考。</>}
            </div>
          )}
        </Card>

        {/* Interests & Preferences */}
        <Card
          title={
            <Space>
              <HeartOutlined style={{ color: "var(--zy-accent)" }} />
              <span>兴趣与偏好</span>
            </Space>
          }
          style={{ borderRadius: 12, border: "1px solid var(--zy-border)", marginTop: 16 }}
        >
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
            <Col xs={24} sm={12}>
              <Form.Item name="prefer_city" label="偏好城市">
                <Select
                  mode="multiple"
                  placeholder="选择你偏好的城市（可多选）"
                  options={cities.map((c) => ({ value: c, label: c }))}
                />
              </Form.Item>
            </Col>
            <Col xs={24} sm={12}>
              <Form.Item name="tuition_max" label="可接受最高学费（元/年）">
                <InputNumber min={0} max={200000} style={{ width: "100%" }} placeholder="如：10000" />
              </Form.Item>
            </Col>
          </Row>
        </Card>

        {/* Ability */}
        <Card
          title={
            <Space>
              <TrophyOutlined style={{ color: "#D97706" }} />
              <span>能力评估</span>
            </Space>
          }
          style={{ borderRadius: 12, border: "1px solid var(--zy-border)", marginTop: 16 }}
        >
          <Form.Item name="strong_subjects" label="擅长科目">
            <Select
              mode="tags"
              placeholder="输入擅长科目后回车添加"
              style={{ width: "100%" }}
            />
          </Form.Item>
          <Row gutter={24}>
            <Col xs={24} sm={12}>
              <Form.Item name="social_ability" label="社交能力（1=内向，5=外向）">
                <Slider min={1} max={5} marks={{ 1: "内向", 2: "", 3: "适中", 4: "", 5: "外向" }} />
              </Form.Item>
            </Col>
            <Col xs={24} sm={12}>
              <Form.Item name="english_level" label="英语水平（1=基础，6=精通）">
                <Slider min={1} max={6} marks={{ 1: "基础", 2: "", 3: "中等", 4: "", 5: "良好", 6: "精通" }} />
              </Form.Item>
            </Col>
          </Row>
        </Card>

        {/* Values */}
        <Card
          title={
            <Space>
              <AimOutlined style={{ color: "var(--zy-secondary)" }} />
              <span>价值观与规划</span>
            </Space>
          }
          style={{ borderRadius: 12, border: "1px solid var(--zy-border)", marginTop: 16 }}
        >
          <Form.Item name="career_values" label="职业价值观">
            <Checkbox.Group options={["高薪", "稳定", "社会价值", "自由", "创造力"]} />
          </Form.Item>
          <Row gutter={16}>
            <Col xs={24} sm={12}>
              <Form.Item name="distance_preference" label="是否接受外地求学">
                <Select options={[
                  { value: "接受外地", label: "接受外地" },
                  { value: "尽量省内", label: "尽量省内" },
                  { value: "只看省内", label: "只看省内" },
                ]} />
              </Form.Item>
            </Col>
            <Col xs={24} sm={12}>
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
          <div style={{ paddingTop: 16, borderTop: "1px solid var(--zy-border)" }}>
            <Button type="primary" htmlType="submit" loading={saving} size="large" style={{ borderRadius: 8, fontWeight: 500 }}>
              保存画像
            </Button>
          </div>
        </Card>
      </Form>
    </Space>
  );

  const securityTab = (
    <Card
      title={
        <Space>
          <LockOutlined style={{ color: "var(--zy-primary)" }} />
          <span>修改密码</span>
        </Space>
      }
      style={{ maxWidth: 480, borderRadius: 12, border: "1px solid var(--zy-border)" }}
    >
      <Form form={pwdForm} layout="vertical" onFinish={onChangePassword}>
        <Form.Item
          name="old_password"
          label="当前密码"
          rules={[{ required: true, message: "请输入当前密码" }]}
        >
          <Password prefix={<LockOutlined />} placeholder="请输入当前密码" />
        </Form.Item>
        <Form.Item
          name="new_password"
          label="新密码"
          rules={[
            { required: true, message: "请输入新密码" },
            { min: 6, message: "密码至少 6 位" },
            { max: 32, message: "密码最多 32 位" },
          ]}
        >
          <Password prefix={<LockOutlined />} placeholder="6-32 位新密码" />
        </Form.Item>
        <Form.Item
          name="confirm_password"
          label="确认新密码"
          dependencies={["new_password"]}
          rules={[
            { required: true, message: "请再次输入新密码" },
            ({ getFieldValue }) => ({
              validator(_, value) {
                if (!value || getFieldValue("new_password") === value) {
                  return Promise.resolve();
                }
                return Promise.reject(new Error("两次输入的密码不一致"));
              },
            }),
          ]}
        >
          <Password prefix={<LockOutlined />} placeholder="再次输入新密码" />
        </Form.Item>
        <Form.Item>
          <Button type="primary" htmlType="submit" loading={changingPwd} size="large" style={{ borderRadius: 8, fontWeight: 500 }}>
            修改密码
          </Button>
        </Form.Item>
      </Form>
    </Card>
  );

  return (
    <AppLayout>
      <Space direction="vertical" size="large" style={{ width: "100%" }}>
        <div>
          <Title level={3} style={{ margin: "0 0 4px" }}>个人中心</Title>
          <Text type="secondary">管理你的个人信息和账号安全</Text>
        </div>
        <Tabs
          defaultActiveKey="profile"
          size="large"
          items={[
            { key: "profile", label: "个人详情", children: profileTab },
            { key: "security", label: "账号安全", children: securityTab, forceRender: true },
          ]}
        />
      </Space>
    </AppLayout>
  );
}
