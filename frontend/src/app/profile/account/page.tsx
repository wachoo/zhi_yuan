"use client";

import { useState } from "react";
import { Card, Form, Button, App, Space, Typography, Input } from "antd";
import { LockOutlined } from "@ant-design/icons";
import api, { logout } from "@/lib/api";

const { Text, Title } = Typography;
const { Password } = Input;

export default function AccountPage() {
  const { message } = App.useApp();
  const [pwdForm] = Form.useForm();
  const [changingPwd, setChangingPwd] = useState(false);

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

  return (
    <Space orientation="vertical" size={24} style={{ width: "100%" }}>
      <div>
        <Title level={3} style={{ margin: "0 0 4px" }}>账号安全</Title>
        <Text type="secondary">管理你的账号安全设置</Text>
      </div>

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
    </Space>
  );
}
