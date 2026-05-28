"use client";

import { useState, useRef, useEffect } from "react";
import { Card, Input, Button, List, Typography, Space, Avatar } from "antd";
import { UserOutlined, RobotOutlined } from "@ant-design/icons";
import api from "@/lib/api";
import AppLayout from "@/components/Layout";

const { TextArea } = Input;
const { Text } = Typography;

interface Message {
  role: "user" | "assistant";
  content: string;
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const listRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    listRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim() || loading) return;
    const userMsg = input.trim();
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: userMsg }]);
    setLoading(true);

    try {
      const params = new URLSearchParams({ message: userMsg });
      if (sessionId) params.set("session_id", sessionId);
      const res = await api.post(`/api/chat?${params}`);
      setSessionId(res.data.session_id);
      setMessages((prev) => [...prev, { role: "assistant", content: res.data.reply }]);
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } } };
      setMessages((prev) => [...prev, {
        role: "assistant",
        content: error.response?.data?.detail || "抱歉，发生了错误，请重试。",
      }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <AppLayout>
      <Card title="AI志愿顾问" style={{ height: "calc(100vh - 200px)", display: "flex", flexDirection: "column" }}>
        <div style={{ flex: 1, overflow: "auto", marginBottom: 16 }} ref={listRef}>
          <List
            dataSource={messages}
            renderItem={(msg) => (
              <List.Item>
                <List.Item.Meta
                  avatar={<Avatar icon={msg.role === "user" ? <UserOutlined /> : <RobotOutlined />} />}
                  title={msg.role === "user" ? "我" : "智愿AI"}
                  description={<Text>{msg.content}</Text>}
                />
              </List.Item>
            )}
          />
        </div>
        <Space.Compact style={{ width: "100%" }}>
          <TextArea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onPressEnter={(e) => { if (!e.shiftKey) { e.preventDefault(); sendMessage(); } }}
            placeholder="输入你的问题，如：华中科技大学的计算机专业怎么样？"
            autoSize={{ minRows: 1, maxRows: 4 }}
          />
          <Button type="primary" onClick={sendMessage} loading={loading} style={{ height: "auto" }}>
            发送
          </Button>
        </Space.Compact>
      </Card>
    </AppLayout>
  );
}
