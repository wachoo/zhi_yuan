"use client";

import { useState } from "react";
import { Card, Form, Input, Button, Typography, Tabs, message } from "antd";
import { useRouter } from "next/navigation";
import api from "@/lib/api";

const { Title } = Typography;

export default function LoginPage() {
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const onLogin = async (values: { phone: string; password: string }) => {
    setLoading(true);
    try {
      const res = await api.post("/api/auth/login", values);
      localStorage.setItem("token", res.data.access_token);
      message.success("登录成功");
      router.push("/");
    } catch {
      message.error("登录失败，请检查手机号和密码");
    } finally {
      setLoading(false);
    }
  };

  const onRegister = async (values: { phone: string; password: string }) => {
    setLoading(true);
    try {
      const res = await api.post("/api/auth/register", values);
      localStorage.setItem("token", res.data.access_token);
      message.success("注册成功");
      router.push("/");
    } catch {
      message.error("注册失败，该手机号可能已注册");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ display: "flex", justifyContent: "center", alignItems: "center", minHeight: "100vh", background: "#f0f2f5" }}>
      <Card style={{ width: 400 }}>
        <Title level={3} style={{ textAlign: "center" }}>智愿</Title>
        <Tabs items={[
          {
            key: "login",
            label: "登录",
            children: (
              <Form onFinish={onLogin}>
                <Form.Item name="phone" rules={[{ required: true }]}>
                  <Input placeholder="手机号" size="large" />
                </Form.Item>
                <Form.Item name="password" rules={[{ required: true }]}>
                  <Input.Password placeholder="密码" size="large" />
                </Form.Item>
                <Button type="primary" htmlType="submit" block size="large" loading={loading}>登录</Button>
              </Form>
            ),
          },
          {
            key: "register",
            label: "注册",
            children: (
              <Form onFinish={onRegister}>
                <Form.Item name="phone" rules={[{ required: true }]}>
                  <Input placeholder="手机号" size="large" />
                </Form.Item>
                <Form.Item name="password" rules={[{ required: true, min: 6 }]}>
                  <Input.Password placeholder="密码（至少6位）" size="large" />
                </Form.Item>
                <Button type="primary" htmlType="submit" block size="large" loading={loading}>注册</Button>
              </Form>
            ),
          },
        ]} />
      </Card>
    </div>
  );
}
