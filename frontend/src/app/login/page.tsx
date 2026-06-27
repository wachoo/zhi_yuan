"use client";

import { Suspense, useState } from "react";
import { Form, Input, Button, Tabs, App, Typography, Spin } from "antd";
import { useRouter, useSearchParams } from "next/navigation";
import { AimOutlined } from "@ant-design/icons";
import api, { setTokens } from "@/lib/api";

const { Title, Text } = Typography;

function LoginContent() {
  const { message } = App.useApp();
  const [loading, setLoading] = useState(false);
  const router = useRouter();
  const searchParams = useSearchParams();
  const redirectTo = searchParams.get("redirect") || "/";

  const onLogin = async (values: { phone: string; password: string }) => {
    setLoading(true);
    try {
      console.log("[DEBUG] Login request:", values);
      const res = await api.post("/api/auth/login", values);
      console.log("[DEBUG] Login response:", res.data);
      setTokens(res.data.access_token, res.data.refresh_token);
      message.success("登录成功");
      router.push(redirectTo);
    } catch (err: any) {
      console.error("[DEBUG] Login error:", err);
      console.error("[DEBUG] Error response:", err.response?.data);
      console.error("[DEBUG] Error status:", err.response?.status);
      message.error("登录失败，请检查手机号和密码");
    } finally {
      setLoading(false);
    }
  };

  const onRegister = async (values: { phone: string; password: string }) => {
    setLoading(true);
    try {
      const res = await api.post("/api/auth/register", values);
      setTokens(res.data.access_token, res.data.refresh_token);
      message.success("注册成功");
      router.push(redirectTo);
    } catch {
      message.error("注册失败，该手机号可能已注册");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      style={{
        display: "flex",
        minHeight: "100vh",
        background: "var(--zy-bg)",
      }}
    >
      {/* Left branding panel */}
      <div
        style={{
          flex: 1,
          background: "linear-gradient(135deg, #1E3A5F 0%, #2563EB 100%)",
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          alignItems: "center",
          padding: 48,
          position: "relative",
          overflow: "hidden",
        }}
      >
        {/* Decorative circles */}
        <div
          style={{
            position: "absolute",
            top: -100,
            right: -80,
            width: 300,
            height: 300,
            background:
              "radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%)",
            borderRadius: "50%",
          }}
        />
        <div
          style={{
            position: "absolute",
            bottom: -60,
            left: -40,
            width: 200,
            height: 200,
            background:
              "radial-gradient(circle, rgba(255,255,255,0.08) 0%, transparent 70%)",
            borderRadius: "50%",
          }}
        />

        <div
          style={{
            position: "relative",
            zIndex: 1,
            textAlign: "center",
            color: "white",
          }}
        >
          <div
            style={{
              width: 72,
              height: 72,
              background: "rgba(255,255,255,0.15)",
              borderRadius: 16,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              margin: "0 auto 24px",
              fontSize: 32,
              backdropFilter: "blur(10px)",
            }}
          >
            <AimOutlined />
          </div>
          <Title
            level={1}
            style={{ color: "white", margin: "0 0 12px", fontSize: 36 }}
          >
            智愿
          </Title>
          <Text
            style={{
              color: "rgba(255,255,255,0.85)",
              fontSize: 16,
              lineHeight: 1.8,
            }}
          >
            AI 驱动的高考志愿智能推荐
            <br />
            基于历年录取数据，精准定位冲/稳/保院校
          </Text>

          <div
            style={{
              marginTop: 48,
              display: "flex",
              gap: 32,
              justifyContent: "center",
            }}
          >
            {[
              { num: "342+", label: "覆盖院校" },
              { num: "126+", label: "热门专业" },
              { num: "37万+", label: "录取数据" },
            ].map((stat) => (
              <div key={stat.label} style={{ textAlign: "center" }}>
                <div style={{ fontSize: 24, fontWeight: 700, color: "white" }}>
                  {stat.num}
                </div>
                <div
                  style={{
                    fontSize: 13,
                    color: "rgba(255,255,255,0.7)",
                    marginTop: 4,
                  }}
                >
                  {stat.label}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Right form panel */}
      <div
        style={{
          flex: 1,
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          padding: 48,
        }}
      >
        <div style={{ width: "100%", maxWidth: 400 }}>
          <div style={{ marginBottom: 32 }}>
            <Title
              level={3}
              style={{ margin: "0 0 8px", color: "var(--zy-text)" }}
            >
              欢迎使用智愿
            </Title>
            <Text style={{ color: "var(--zy-text-secondary)" }}>
              登录或注册以开始获取个性化志愿推荐
            </Text>
          </div>

          <Tabs
            items={[
              {
                key: "login",
                label: "登录",
                children: (
                  <Form layout="vertical" onFinish={onLogin} size="large">
                    <Form.Item
                      name="phone"
                      label="手机号"
                      rules={[{ required: true, message: "请输入手机号" }]}
                    >
                      <Input placeholder="请输入手机号" />
                    </Form.Item>
                    <Form.Item
                      name="password"
                      label="密码"
                      rules={[{ required: true, message: "请输入密码" }]}
                    >
                      <Input.Password placeholder="请输入密码" />
                    </Form.Item>
                    <Button
                      type="primary"
                      htmlType="submit"
                      block
                      loading={loading}
                      style={{ height: 44, fontWeight: 500 }}
                    >
                      登录
                    </Button>
                  </Form>
                ),
              },
              {
                key: "register",
                label: "注册",
                children: (
                  <Form layout="vertical" onFinish={onRegister} size="large">
                    <Form.Item
                      name="phone"
                      label="手机号"
                      rules={[{ required: true, message: "请输入手机号" }]}
                    >
                      <Input placeholder="请输入手机号" />
                    </Form.Item>
                    <Form.Item
                      name="password"
                      label="密码"
                      rules={[
                        { required: true, message: "请输入密码" },
                        { min: 6, message: "密码至少6位" },
                      ]}
                    >
                      <Input.Password placeholder="请设置密码（至少6位）" />
                    </Form.Item>
                    <Button
                      type="primary"
                      htmlType="submit"
                      block
                      loading={loading}
                      style={{ height: 44, fontWeight: 500 }}
                    >
                      注册
                    </Button>
                  </Form>
                ),
              },
            ]}
          />
        </div>
      </div>
    </div>
  );
}

export default function LoginPage() {
  return (
    <Suspense
      fallback={
        <Spin size="large" style={{ display: "block", margin: "100px auto" }} />
      }
    >
      <LoginContent />
    </Suspense>
  );
}
