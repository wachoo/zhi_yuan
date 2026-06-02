"use client";

import { useEffect, useState } from "react";
import {
  Card, Form, Select, Button, Progress, Space, Row, Col, Spin, App,
  InputNumber, Input, Checkbox, Slider, Radio, Typography,
} from "antd";
import {
  UserOutlined,
  HeartOutlined,
  TrophyOutlined,
  AimOutlined,
  HomeOutlined,
} from "@ant-design/icons";
import api from "@/lib/api";
import { UserProfile, SUBJECT_TYPE_OPTIONS, EXAM_TYPE_OPTIONS } from "@/types";

const { Text, Title } = Typography;

const interestsOptions = [
  "计算机", "编程", "设计", "音乐", "运动", "阅读", "数学", "物理",
  "化学", "生物", "经济", "法律", "医学", "教育", "艺术", "机械",
  "表演", "体育", "手工",
];

const dislikesOptions = [
  "编程", "数学", "物理", "化学", "生物", "设计", "绘画", "音乐",
  "背诵", "写作", "实验", "解剖", "户外工作", "出差", "加班", "夜班",
  "机械操作", "手工", "表演", "体育", "销售", "会计",
];

const cities = [
  "北京", "上海", "广州", "深圳",
  "成都", "杭州", "武汉", "西安", "南京", "重庆", "苏州", "长沙", "天津", "郑州",
  "东莞", "青岛", "沈阳", "宁波", "昆明", "合肥", "佛山", "福州", "哈尔滨", "济南",
  "无锡", "厦门", "温州", "大连", "贵阳", "南昌", "石家庄", "太原", "南宁", "兰州",
  "乌鲁木齐", "呼和浩特", "拉萨", "银川", "西宁", "海口", "长春", "珠海",
];

const provinces = [
  "北京", "天津", "上海", "重庆", "河北", "山西", "辽宁", "吉林", "黑龙江",
  "江苏", "浙江", "安徽", "福建", "江西", "山东", "河南", "湖北", "湖南",
  "广东", "海南", "四川", "贵州", "云南", "陕西", "甘肃", "青海", "台湾",
  "内蒙古", "广西", "西藏", "宁夏", "新疆", "香港", "澳门",
];

export default function ProfilePage() {
  const { modal, message } = App.useApp();
  const [form] = Form.useForm();
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
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
          initialValues.professional_score = (data.basic_info as Record<string, unknown>).professional_score;
          setExamType(data.basic_info.exam_type);
        }
        if (data.personality) {
          initialValues.interests = (data.personality as Record<string, unknown>).interests;
          initialValues.dislikes = (data.personality as Record<string, unknown>).dislikes;
        }
        if (data.family_info) {
          initialValues.tuition_max = (data.family_info as Record<string, unknown>).tuition_max;
          initialValues.prefer_city = (data.family_info as Record<string, unknown>).prefer_city;
          initialValues.income_range = (data.family_info as Record<string, unknown>).income_range;
          initialValues.parent_industry = (data.family_info as Record<string, unknown>).parent_industry;
          initialValues.parent_education = (data.family_info as Record<string, unknown>).parent_education;
          initialValues.hukou_type = (data.family_info as Record<string, unknown>).hukou_type;
          initialValues.has_siblings = (data.family_info as Record<string, unknown>).has_siblings;
          initialValues.has_elderly_care = (data.family_info as Record<string, unknown>).has_elderly_care;
          initialValues.home_province = (data.family_info as Record<string, unknown>).home_province;
          initialValues.home_city = (data.family_info as Record<string, unknown>).home_city;
          initialValues.home_district = (data.family_info as Record<string, unknown>).home_district;
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
          professional_score: values.professional_score,
        };
      }

      updateData.family_info = {
        tuition_max: values.tuition_max,
        prefer_city: values.prefer_city,
        income_range: values.income_range,
        parent_industry: values.parent_industry,
        parent_education: values.parent_education,
        hukou_type: values.hukou_type,
        has_siblings: values.has_siblings,
        has_elderly_care: values.has_elderly_care,
        home_province: values.home_province,
        home_city: values.home_city,
        home_district: values.home_district,
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
    } catch {
      message.error("保存失败");
    } finally {
      setSaving(false);
    }
  };

  const onSave = (values: Record<string, unknown>) => {
    modal.confirm({
      title: "确认保存",
      content: "是否保存当前个人详情？",
      okText: "确认",
      cancelText: "取消",
      onOk: () => doSave(values),
    });
  };

  return (
    <Spin spinning={loading}>
    <Space orientation="vertical" size={24} style={{ width: "100%" }}>
      <div>
        <Title level={3} style={{ margin: "0 0 4px" }}>个人详情</Title>
        <Text type="secondary">完善五维画像，获得更精准的院校推荐</Text>
      </div>

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
              <Form.Item name="subject_type" label="首选科目" rules={[{ required: true, message: "请选择首选科目" }]}>
                <Select placeholder="选择首选科目" options={SUBJECT_TYPE_OPTIONS} />
              </Form.Item>
            </Col>
          </Row>
          <Form.Item name="exam_type" label="报考科类" rules={[{ required: true, message: "请选择报考科类" }]} style={{ marginBottom: 0 }}>
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
          {(examType === "艺术类" || examType === "体育类") && (
            <Form.Item
              name="professional_score"
              label={examType === "艺术类" ? "艺考专业分" : "体育术科分"}
              rules={[{ required: true, message: `请输入${examType === "艺术类" ? "艺考" : "体育术科"}专业分` }]}
              extra={examType === "艺术类" ? "省级艺术类专业统考成绩（满分因省份而异，通常300分）" : "省级体育专业统考成绩（满分因省份而异，通常100-400分）"}
              style={{ marginTop: 12 }}
            >
              <InputNumber min={0} max={400} style={{ width: "100%" }} placeholder="如：260" />
            </Form.Item>
          )}
        </Card>

        {/* Family Info */}
        <Card
          title={
            <Space>
              <HomeOutlined style={{ color: "var(--zy-accent)" }} />
              <span>家庭情况</span>
            </Space>
          }
          style={{ borderRadius: 12, border: "1px solid var(--zy-border)", marginTop: 16 }}
        >
          <Row gutter={16}>
            <Col xs={24} sm={12}>
              <Form.Item name="income_range" label="家庭年收入">
                <Select
                  placeholder="选择收入区间"
                  options={[
                    { value: "5万以下", label: "5万以下" },
                    { value: "5-10万", label: "5-10万" },
                    { value: "10-20万", label: "10-20万" },
                    { value: "20-50万", label: "20-50万" },
                    { value: "50-100万", label: "50-100万" },
                    { value: "100万以上", label: "100万以上" },
                  ]}
                />
              </Form.Item>
            </Col>
            <Col xs={24} sm={12}>
              <Form.Item name="tuition_max" label="可接受最高学费（元/年）">
                <InputNumber min={0} max={200000} style={{ width: "100%" }} placeholder="如：10000" />
              </Form.Item>
            </Col>
          </Row>
          <Row gutter={16}>
            <Col xs={24} sm={12}>
              <Form.Item name="parent_industry" label="父母职业方向">
                <Select
                  placeholder="选择主要职业领域"
                  options={[
                    { value: "公务员/事业单位", label: "公务员/事业单位" },
                    { value: "企业管理", label: "企业管理" },
                    { value: "个体经营", label: "个体经营" },
                    { value: "教育/科研", label: "教育/科研" },
                    { value: "医疗/卫生", label: "医疗/卫生" },
                    { value: "工程技术", label: "工程技术" },
                    { value: "金融/财务", label: "金融/财务" },
                    { value: "法律", label: "法律" },
                    { value: "自由职业", label: "自由职业" },
                    { value: "务农", label: "务农" },
                    { value: "务工", label: "务工" },
                    { value: "其他", label: "其他" },
                  ]}
                />
              </Form.Item>
            </Col>
            <Col xs={24} sm={12}>
              <Form.Item name="parent_education" label="父母最高学历">
                <Select
                  placeholder="选择学历"
                  options={[
                    { value: "初中及以下", label: "初中及以下" },
                    { value: "高中/中专", label: "高中/中专" },
                    { value: "大专", label: "大专" },
                    { value: "本科", label: "本科" },
                    { value: "硕士及以上", label: "硕士及以上" },
                  ]}
                />
              </Form.Item>
            </Col>
          </Row>
          <Form.Item name="hukou_type" label="户口类型">
            <Radio.Group options={[
              { value: "城市", label: "城市" },
              { value: "城镇", label: "城镇" },
              { value: "农村", label: "农村" },
            ]} />
          </Form.Item>
          <Row gutter={16}>
            <Col xs={24} sm={12}>
              <Form.Item name="has_siblings" label="是否独生子女">
                <Radio.Group options={[
                  { value: false, label: "独生子女" },
                  { value: true, label: "有兄弟姐妹" },
                ]} />
              </Form.Item>
            </Col>
            <Col xs={24} sm={12}>
              <Form.Item name="has_elderly_care" label="是否有老人赡养负担">
                <Radio.Group options={[
                  { value: false, label: "无" },
                  { value: true, label: "有" },
                ]} />
              </Form.Item>
            </Col>
          </Row>
          <Row gutter={16}>
            <Col xs={24} sm={8}>
              <Form.Item name="home_province" label="家庭所在省">
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
            <Col xs={24} sm={8}>
              <Form.Item name="home_city" label="所在城市">
                <Input placeholder="如：杭州市" />
              </Form.Item>
            </Col>
            <Col xs={24} sm={8}>
              <Form.Item name="home_district" label="所在区/县">
                <Input placeholder="如：西湖区" />
              </Form.Item>
            </Col>
          </Row>
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
              options={interestsOptions.map((i) => ({ value: i, label: i }))}
            />
          </Form.Item>
          <Form.Item name="dislikes" label="厌恶领域">
            <Select
              mode="tags"
              placeholder="从列表选择，或输入自定义关键词后回车添加（如：编程、数学、实验等）"
              style={{ width: "100%" }}
              options={dislikesOptions.map((d) => ({ value: d, label: d }))}
            />
          </Form.Item>
          <Form.Item name="prefer_city" label="偏好城市">
            <Select
              mode="multiple"
              placeholder="选择你偏好的城市（可多选）"
              options={cities.map((c) => ({ value: c, label: c }))}
            />
          </Form.Item>
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
    </Spin>
  );
}
