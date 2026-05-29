"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import { Input, Button, List, Typography, Space, Avatar, Empty, Spin } from "antd";
import {
  UserOutlined,
  RobotOutlined,
  PlusOutlined,
  MessageOutlined,
  DeleteOutlined,
} from "@ant-design/icons";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import api from "@/lib/api";
import AppLayout from "@/components/Layout";
import type { ChatSession, ChatMessage } from "@/types";

const { TextArea } = Input;
const { Text } = Typography;

interface DisplayMessage {
  role: "user" | "assistant";
  content: string;
}

export default function ChatPage() {
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<DisplayMessage[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [sessionsLoading, setSessionsLoading] = useState(false);
  const [historyLoading, setHistoryLoading] = useState(false);
  const listRef = useRef<HTMLDivElement>(null);

  // 加载会话列表
  const loadSessions = useCallback(async () => {
    setSessionsLoading(true);
    try {
      const res = await api.get("/api/chat/sessions");
      setSessions(res.data);
    } catch {
      // 静默处理
    } finally {
      setSessionsLoading(false);
    }
  }, []);

  // 加载指定会话的消息
  const loadSessionMessages = useCallback(async (sessionId: string) => {
    setHistoryLoading(true);
    try {
      const res = await api.get<ChatMessage[]>(
        `/api/chat/sessions/${sessionId}/messages`
      );
      const displayMsgs: DisplayMessage[] = res.data
        .filter((m) => m.role === "user" || m.role === "assistant")
        .map((m) => ({ role: m.role as "user" | "assistant", content: m.content }));
      setMessages(displayMsgs);
      setCurrentSessionId(sessionId);
    } catch {
      setMessages([]);
    } finally {
      setHistoryLoading(false);
    }
  }, []);

  // 初始化加载会话列表
  useEffect(() => {
    loadSessions();
  }, [loadSessions]);

  // 自动滚动到底部
  useEffect(() => {
    listRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages]);

  // 新建对话
  const handleNewChat = () => {
    setCurrentSessionId(null);
    setMessages([]);
    setInput("");
  };

  // 切换会话
  const handleSelectSession = (sessionId: string) => {
    if (sessionId === currentSessionId) return;
    loadSessionMessages(sessionId);
  };

  // 删除会话（本地移除）
  const handleDeleteSession = async (e: React.MouseEvent, sessionId: string) => {
    e.stopPropagation();
    setSessions((prev) => prev.filter((s) => s.session_id !== sessionId));
    if (currentSessionId === sessionId) {
      setCurrentSessionId(null);
      setMessages([]);
    }
  };

  // 发送消息
  const sendMessage = async () => {
    if (!input.trim() || loading) return;
    const userMsg = input.trim();
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: userMsg }]);
    setLoading(true);

    try {
      const params = new URLSearchParams({ message: userMsg });
      if (currentSessionId) params.set("session_id", currentSessionId);
      const res = await api.post(`/api/chat?${params}`);
      const newSessionId = res.data.session_id;
      setCurrentSessionId(newSessionId);
      setMessages((prev) => [...prev, { role: "assistant", content: res.data.reply }]);
      // 刷新会话列表
      await loadSessions();
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } } };
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: error.response?.data?.detail || "抱歉，发生了错误，请重试。",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <AppLayout>
      <div style={{ display: "flex", height: "calc(100vh - 200px)", gap: 16 }}>
        {/* 左侧会话列表 */}
        <div
          style={{
            width: 260,
            flexShrink: 0,
            display: "flex",
            flexDirection: "column",
            background: "#fff",
            borderRadius: 8,
            border: "1px solid #f0f0f0",
            overflow: "hidden",
          }}
        >
          <div style={{ padding: "12px 16px", borderBottom: "1px solid #f0f0f0" }}>
            <Button
              type="primary"
              icon={<PlusOutlined />}
              block
              onClick={handleNewChat}
            >
              新建对话
            </Button>
          </div>
          <div style={{ flex: 1, overflowY: "auto", padding: "8px 0" }}>
            {sessionsLoading ? (
              <div style={{ textAlign: "center", padding: 24 }}>
                <Spin size="small" />
              </div>
            ) : sessions.length === 0 ? (
              <Empty
                image={Empty.PRESENTED_IMAGE_SIMPLE}
                description="暂无对话"
                style={{ padding: 24 }}
              />
            ) : (
              <List
                dataSource={sessions}
                renderItem={(session) => (
                  <List.Item
                    onClick={() => handleSelectSession(session.session_id)}
                    style={{
                      padding: "10px 16px",
                      cursor: "pointer",
                      background:
                        session.session_id === currentSessionId
                          ? "#e6f4ff"
                          : "transparent",
                      borderLeft:
                        session.session_id === currentSessionId
                          ? "3px solid #1677ff"
                          : "3px solid transparent",
                      marginBottom: 0,
                      borderBottom: "none",
                    }}
                    className="session-item"
                  >
                    <div style={{ display: "flex", alignItems: "center", width: "100%", gap: 8 }}>
                      <MessageOutlined style={{ color: "#8c8c8c", flexShrink: 0 }} />
                      <div style={{ flex: 1, minWidth: 0 }}>
                        <Text
                          ellipsis
                          style={{
                            display: "block",
                            fontWeight:
                              session.session_id === currentSessionId ? 600 : 400,
                          }}
                        >
                          {session.title}
                        </Text>
                        <Text type="secondary" style={{ fontSize: 12 }}>
                          {session.message_count} 条消息
                        </Text>
                      </div>
                      <DeleteOutlined
                        style={{ color: "#bfbfbf", flexShrink: 0 }}
                        onClick={(e) => handleDeleteSession(e, session.session_id)}
                      />
                    </div>
                  </List.Item>
                )}
              />
            )}
          </div>
        </div>

        {/* 右侧对话区域 */}
        <div
          style={{
            flex: 1,
            display: "flex",
            flexDirection: "column",
            background: "#fff",
            borderRadius: 8,
            border: "1px solid #f0f0f0",
            overflow: "hidden",
          }}
        >
          <div
            style={{
              padding: "12px 20px",
              borderBottom: "1px solid #f0f0f0",
              fontWeight: 600,
              fontSize: 16,
            }}
          >
            AI志愿顾问
            {currentSessionId && (
              <Text type="secondary" style={{ fontSize: 13, fontWeight: 400, marginLeft: 8 }}>
                {sessions.find((s) => s.session_id === currentSessionId)?.title}
              </Text>
            )}
          </div>
          <div
            className="chat-scroll-area"
            style={{
              flex: 1,
              overflowY: "auto",
              overflowX: "hidden",
              padding: "16px 24px",
            }}
            ref={listRef}
          >
            {historyLoading ? (
              <div style={{ textAlign: "center", padding: 48 }}>
                <Spin />
              </div>
            ) : messages.length === 0 ? (
              <div style={{ textAlign: "center", padding: 48 }}>
                <RobotOutlined style={{ fontSize: 48, color: "#d9d9d9" }} />
                <div style={{ marginTop: 16, color: "#8c8c8c" }}>
                  你好！我是智愿AI顾问，可以帮你查询院校、专业、录取分数等信息。
                </div>
              </div>
            ) : (
              <List
                dataSource={messages}
                renderItem={(msg) => (
                  <List.Item style={{ borderBottom: "none", padding: "8px 0" }}>
                    <List.Item.Meta
                      avatar={
                        <Avatar
                          icon={
                            msg.role === "user" ? <UserOutlined /> : <RobotOutlined />
                          }
                        />
                      }
                      title={msg.role === "user" ? "我" : "智愿AI"}
                      description={
                        msg.role === "assistant" ? (
                          <div className="markdown-body">
                            <ReactMarkdown remarkPlugins={[remarkGfm]}>
                              {msg.content}
                            </ReactMarkdown>
                          </div>
                        ) : (
                          <Text>{msg.content}</Text>
                        )
                      }
                    />
                  </List.Item>
                )}
              />
            )}
          </div>
          <div style={{ padding: "12px 24px", borderTop: "1px solid #f0f0f0" }}>
            <Space.Compact style={{ width: "100%" }}>
              <TextArea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onPressEnter={(e) => {
                  if (!e.shiftKey) {
                    e.preventDefault();
                    sendMessage();
                  }
                }}
                placeholder="输入你的问题，如：华中科技大学的计算机专业怎么样？"
                autoSize={{ minRows: 1, maxRows: 4 }}
              />
              <Button
                type="primary"
                onClick={sendMessage}
                loading={loading}
                style={{ height: "auto" }}
              >
                发送
              </Button>
            </Space.Compact>
          </div>
        </div>
      </div>
    </AppLayout>
  );
}
