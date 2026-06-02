"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import { Input, Button, Typography, Space, Avatar, Empty, Spin, Select, Tag, App } from "antd";
import {
  UserOutlined,
  RobotOutlined,
  PlusOutlined,
  MessageOutlined,
  DeleteOutlined,
  PauseCircleOutlined,
  EditOutlined,
  CheckOutlined,
  SendOutlined,
} from "@ant-design/icons";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import api from "@/lib/api";
import AppLayout from "@/components/Layout";
import type { ChatSession, ChatMessage } from "@/types";

const { TextArea } = Input;
const { Text } = Typography;

// 打字机光标 CSS 动画
const streamCursorStyle = `
@keyframes blink-cursor {
  0%, 100% { opacity: 1; }
  50% { opacity: 0; }
}
.streaming-cursor {
  display: inline-block;
  animation: blink-cursor 0.8s step-end infinite;
  color: var(--zy-primary);
  font-weight: 400;
}
`;

// 流式 Markdown 渲染组件
function StreamingMarkdown({ content }: { content: string }) {
  let displayContent = content;
  const fenceCount = (content.match(/^```/gm) || []).length;
  const inCodeBlock = fenceCount % 2 !== 0;

  if (inCodeBlock) {
    const lines = content.split("\n");
    const lastLine = lines[lines.length - 1] || "";
    const lastFenceIdx = content.lastIndexOf("```");
    const fenceLine = content.substring(lastFenceIdx).split("\n")[0];

    if (fenceLine === "```" || fenceLine === "``") {
      displayContent = content + "\n```";
    } else if (lastLine.startsWith("```") && lastLine !== "```") {
      displayContent = content + "\n```\n";
    } else {
      displayContent = content + "\n```";
    }
  }

  return (
    <div className="markdown-body">
      <ReactMarkdown remarkPlugins={[remarkGfm]}>
        {displayContent}
      </ReactMarkdown>
      <span className="streaming-cursor">▍</span>
    </div>
  );
}

interface DisplayMessage {
  id?: string;
  role: "user" | "assistant";
  content: string;
  skill_name?: string;
}

interface Skill {
  id: string;
  name: string;
  description: string;
}

export default function ChatPage() {
  const { modal, message } = App.useApp();
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<DisplayMessage[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [sessionsLoading, setSessionsLoading] = useState(false);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [streaming, setStreaming] = useState(false);
  const [skills, setSkills] = useState<Skill[]>([]);
  const [currentSkillId, setCurrentSkillId] = useState("default");
  const [editingSessionId, setEditingSessionId] = useState<string | null>(null);
  const [editingTitle, setEditingTitle] = useState("");
  const listRef = useRef<HTMLDivElement>(null);
  const abortRef = useRef<AbortController | null>(null);
  const streamSkillNameRef = useRef<string | null>(null);

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

  const loadSessionMessages = useCallback(async (sessionId: string) => {
    setHistoryLoading(true);
    try {
      const res = await api.get<ChatMessage[]>(
        `/api/chat/sessions/${sessionId}/messages`
      );
      const displayMsgs: DisplayMessage[] = res.data
        .filter((m) => m.role === "user" || m.role === "assistant")
        .map((m) => ({
          id: m.id,
          role: m.role as "user" | "assistant",
          content: m.content,
          skill_name: m.skill_name ?? undefined,
        }));
      setMessages(displayMsgs);
      setCurrentSessionId(sessionId);
    } catch {
      setMessages([]);
    } finally {
      setHistoryLoading(false);
    }
  }, []);

  useEffect(() => {
    loadSessions();
  }, [loadSessions]);

  useEffect(() => {
    const loadSkills = async () => {
      try {
        const res = await api.get<Skill[]>("/api/chat/skills");
        setSkills(res.data);
      } catch {
        setSkills([{ id: "default", name: "智愿顾问", description: "" }]);
      }
    };
    loadSkills();
  }, []);

  useEffect(() => {
    if (listRef.current) {
      listRef.current.scrollTop = listRef.current.scrollHeight;
    }
  }, [messages]);

  const handleNewChat = () => {
    setCurrentSessionId(null);
    setMessages([]);
    setInput("");
  };

  const handleSelectSession = (sessionId: string) => {
    if (sessionId === currentSessionId) return;
    loadSessionMessages(sessionId);
  };

  const handleDeleteSession = async (e: React.MouseEvent, sessionId: string) => {
    e.stopPropagation();
    modal.confirm({
      title: "确认删除",
      content: "删除该会话及其所有对话记录？此操作不可恢复。",
      okText: "删除",
      okButtonProps: { danger: true },
      cancelText: "取消",
      onOk: async () => {
        try {
          await api.delete(`/api/chat/sessions/${sessionId}`);
          setSessions((prev) => prev.filter((s) => s.session_id !== sessionId));
          if (currentSessionId === sessionId) {
            setCurrentSessionId(null);
            setMessages([]);
          }
        } catch {
          message.error("删除会话失败");
        }
      },
    });
  };

  const handleDeleteMessage = async (msgIndex: number) => {
    const msg = messages[msgIndex];
    if (!msg.id || !currentSessionId) return;

    modal.confirm({
      title: "确认删除",
      content: "删除该问答对？此操作不可恢复。",
      okText: "删除",
      okButtonProps: { danger: true },
      cancelText: "取消",
      onOk: async () => {
        try {
          await api.delete(`/api/chat/sessions/${currentSessionId}/messages/${msg.id}`);
          // 从本地状态移除该 user 消息和紧随的 assistant 消息
          setMessages((prev) => {
            const next = [...prev];
            const nextMsg = next[msgIndex + 1];
            // 如果下一条是 assistant，也一并移除
            if (nextMsg && nextMsg.role === "assistant") {
              next.splice(msgIndex, 2);
            } else {
              next.splice(msgIndex, 1);
            }
            // 如果会话变空，清除当前会话
            if (next.length === 0) {
              setCurrentSessionId(null);
            }
            return next;
          });
          // 刷新会话列表（会话可能已被后端删除）
          loadSessions();
        } catch {
          message.error("删除失败");
        }
      },
    });
  };

  const handleRenameStart = (e: React.MouseEvent, session: ChatSession) => {
    e.stopPropagation();
    setEditingSessionId(session.session_id);
    setEditingTitle(session.title);
  };

  const handleRenameCommit = async () => {
    if (!editingSessionId) return;
    const newTitle = editingTitle.trim();
    const targetId = editingSessionId;
    setEditingSessionId(null);
    if (!newTitle) return;
    try {
      await api.put(`/api/chat/sessions/${targetId}`, { title: newTitle });
      setSessions((prev) =>
        prev.map((s) =>
          s.session_id === targetId ? { ...s, title: newTitle } : s
        )
      );
    } catch {
      // 失败时静默处理
    }
  };

  const handleRenameCancel = () => {
    setEditingSessionId(null);
  };

  const sendMessage = async () => {
    if (!input.trim() || loading) return;
    const userMsg = input.trim();
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: userMsg }]);
    setLoading(true);
    setStreaming(true);

    setMessages((prev) => [...prev, { role: "assistant", content: "" }]);

    const controller = new AbortController();
    abortRef.current = controller;
    streamSkillNameRef.current = null;

    try {
      const params = new URLSearchParams({ message: userMsg });
      if (currentSessionId) params.set("session_id", currentSessionId);
      params.set("skill_id", currentSkillId);

      const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;
      const baseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

      const response = await fetch(`${baseUrl}/api/chat/stream?${params}`, {
        method: "POST",
        headers: {
          Authorization: token ? `Bearer ${token}` : "",
        },
        signal: controller.signal,
      });

      if (response.status === 401) {
        localStorage.removeItem("token");
        window.location.href = "/login";
        return;
      }

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const reader = response.body?.getReader();
      if (!reader) throw new Error("无法获取响应流");

      const decoder = new TextDecoder();
      let buffer = "";
      let accumulated = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() || "";

        for (const line of lines) {
          if (!line.startsWith("data: ")) continue;
          const data = line.slice(6).trim();

          if (data === "[DONE]") continue;

          // 统一尝试 JSON 解析，区分元数据和文本内容
          try {
            const parsed = JSON.parse(data);
            if (typeof parsed === "object" && parsed !== null) {
              if (parsed.session_id) {
                setCurrentSessionId(parsed.session_id);
                loadSessions();
              }
              if (parsed.skill_name) {
                streamSkillNameRef.current = parsed.skill_name;
              }
            }
            // 合法 JSON → 元数据，跳过
            continue;
          } catch {
            // 非 JSON → 当作普通文本内容累积
          }

          accumulated += data;
          const snapshot = accumulated;
          setMessages((prev) => {
            const next = [...prev];
            if (next.length > 0 && next[next.length - 1].role === "assistant") {
              next[next.length - 1] = { ...next[next.length - 1], content: snapshot };
            }
            return next;
          });
        }
      }
    } catch (err: unknown) {
      if (err instanceof Error && err.name === "AbortError") {
        // 用户主动取消
      } else {
        setMessages((prev) => {
          const next = [...prev];
          if (next.length > 0 && next[next.length - 1].role === "assistant") {
            if (!next[next.length - 1].content) {
              next[next.length - 1] = {
                ...next[next.length - 1],
                content: "抱歉，发生了错误，请重试。",
              };
            }
          }
          return next;
        });
      }
    } finally {
      setLoading(false);
      setStreaming(false);
      abortRef.current = null;
      // 将流式期间捕获的 skill_name 写入最后一条 assistant 消息
      if (streamSkillNameRef.current) {
        const name = streamSkillNameRef.current;
        setMessages((prev) => {
          const next = [...prev];
          if (next.length > 0 && next[next.length - 1].role === "assistant") {
            next[next.length - 1] = { ...next[next.length - 1], skill_name: name };
          }
          return next;
        });
      }
    }
  };

  const stopStreaming = () => {
    abortRef.current?.abort();
  };

  return (
    <AppLayout>
      <style>{streamCursorStyle}</style>
      <div style={{ display: "flex", height: "calc(100vh - 200px)", gap: 16 }}>
        {/* Sidebar */}
        <div className="zy-chat-sidebar" style={{ width: 280, flexShrink: 0 }}>
          <div style={{ padding: 16, borderBottom: "1px solid var(--zy-border)" }}>
            <Button
              type="primary"
              icon={<PlusOutlined />}
              block
              onClick={handleNewChat}
              style={{ height: 42, borderRadius: 8, fontWeight: 500 }}
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
              <div>
                {sessions.map((session) => (
                  <div
                    key={session.session_id}
                    onClick={() => handleSelectSession(session.session_id)}
                    className="session-item"
                    style={{
                      padding: "12px 16px",
                      cursor: "pointer",
                      background:
                        session.session_id === currentSessionId
                          ? "var(--zy-muted)"
                          : "transparent",
                      borderLeft:
                        session.session_id === currentSessionId
                          ? "3px solid var(--zy-primary)"
                          : "3px solid transparent",
                    }}
                  >
                    <div style={{ display: "flex", alignItems: "center", width: "100%", gap: 10 }}>
                      <MessageOutlined style={{ color: "var(--zy-text-muted)", flexShrink: 0 }} />
                      {editingSessionId === session.session_id ? (
                        <>
                          <Input
                            size="small"
                            value={editingTitle}
                            onChange={(e) => setEditingTitle(e.target.value)}
                            onPressEnter={(e) => {
                              e.stopPropagation();
                              handleRenameCommit();
                            }}
                            onKeyDown={(e) => {
                              if (e.key === "Escape") {
                                e.stopPropagation();
                                handleRenameCancel();
                              }
                            }}
                            onBlur={() => handleRenameCommit()}
                            onClick={(e) => e.stopPropagation()}
                            autoFocus
                            maxLength={100}
                            style={{ flex: 1 }}
                          />
                          <CheckOutlined
                            style={{ color: "var(--zy-primary)", flexShrink: 0, cursor: "pointer" }}
                            onMouseDown={(e) => {
                              e.preventDefault();
                              handleRenameCommit();
                            }}
                          />
                        </>
                      ) : (
                        <>
                          <div style={{ flex: 1, minWidth: 0 }}>
                            <Text
                              ellipsis
                              style={{
                                display: "block",
                                fontWeight: session.session_id === currentSessionId ? 600 : 400,
                                fontSize: 14,
                              }}
                            >
                              {session.title}
                            </Text>
                            <Text type="secondary" style={{ fontSize: 12 }}>
                              {session.message_count} 条消息
                            </Text>
                          </div>
                          <EditOutlined
                            className="anticon-edit"
                            style={{ color: "var(--zy-text-muted)", flexShrink: 0, cursor: "pointer", fontSize: 13 }}
                            onClick={(e) => handleRenameStart(e, session)}
                          />
                          <DeleteOutlined
                            className="anticon-delete"
                            style={{ color: "var(--zy-text-muted)", flexShrink: 0, cursor: "pointer", fontSize: 13 }}
                            onClick={(e) => handleDeleteSession(e, session.session_id)}
                          />
                        </>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Main chat area */}
        <div className="zy-chat-main" style={{ flex: 1 }}>
          {/* Header */}
          <div
            style={{
              padding: "14px 24px",
              borderBottom: "1px solid var(--zy-border)",
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              background: "var(--zy-surface)",
            }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
              <div style={{
                width: 36,
                height: 36,
                background: "linear-gradient(135deg, var(--zy-primary), var(--zy-secondary))",
                borderRadius: 10,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                color: "white",
              }}>
                <RobotOutlined />
              </div>
              <div>
                <Text strong style={{ fontSize: 15 }}>AI志愿顾问</Text>
                {currentSessionId && (
                  <Text type="secondary" style={{ fontSize: 12, display: "block" }}>
                    {sessions.find((s) => s.session_id === currentSessionId)?.title}
                  </Text>
                )}
              </div>
            </div>
          </div>

          {/* Messages */}
          <div
            className="chat-scroll-area"
            style={{
              flex: 1,
              overflowY: "auto",
              overflowX: "hidden",
              padding: "20px 28px",
              background: "var(--zy-bg)",
            }}
            ref={listRef}
          >
            {historyLoading ? (
              <div style={{ textAlign: "center", padding: 48 }}>
                <Spin />
              </div>
            ) : messages.length === 0 ? (
              <div style={{ textAlign: "center", padding: 48 }}>
                <div style={{
                  width: 72,
                  height: 72,
                  background: "linear-gradient(135deg, var(--zy-primary), var(--zy-secondary))",
                  borderRadius: 20,
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  margin: "0 auto 20px",
                  color: "white",
                  fontSize: 32,
                }}>
                  <RobotOutlined />
                </div>
                <Text strong style={{ fontSize: 16, display: "block", marginBottom: 8 }}>
                  你好！我是智愿AI顾问
                </Text>
                <Text type="secondary">
                  可以帮你查询院校、专业、录取分数等信息，试试问我吧
                </Text>
              </div>
            ) : (
              <div>
                {messages.map((msg, msgIndex) => (
                  <div key={msg.id ?? msgIndex} style={{ display: "flex", gap: 12, padding: "10px 0", alignItems: "flex-start" }}>
                    <Avatar
                      style={{
                        background: msg.role === "user"
                          ? "var(--zy-primary)"
                          : "linear-gradient(135deg, #1E3A5F, #2563EB)",
                        flexShrink: 0,
                      }}
                      icon={msg.role === "user" ? <UserOutlined /> : <RobotOutlined />}
                    />
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <div style={{ marginBottom: 4 }}>
                        <Space size={6}>
                          <Text strong style={{ fontSize: 13 }}>
                            {msg.role === "user" ? "我" : "智愿AI"}
                          </Text>
                          {msg.role === "assistant" && msg.skill_name && (
                            <Tag style={{ borderRadius: 4, fontSize: 11, lineHeight: "18px", margin: 0 }}>
                              {msg.skill_name}
                            </Tag>
                          )}
                        </Space>
                      </div>
                      <div>
                        {msg.role === "assistant" ? (
                          streaming && msgIndex === messages.length - 1 ? (
                            <StreamingMarkdown content={msg.content} />
                          ) : (
                            <div className="markdown-body">
                              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                                {msg.content}
                              </ReactMarkdown>
                            </div>
                          )
                        ) : (
                          <div style={{
                            background: "var(--zy-surface)",
                            padding: "12px 16px",
                            borderRadius: "4px 12px 12px 12px",
                            border: "1px solid var(--zy-border)",
                            display: "inline-block",
                            maxWidth: "80%",
                          }}>
                            <Text>{msg.content}</Text>
                          </div>
                        )}
                      </div>
                    </div>
                    {msg.role === "user" && msg.id && !streaming && (
                      <DeleteOutlined
                        className="anticon-delete"
                        style={{ color: "var(--zy-text-muted)", cursor: "pointer", fontSize: 13, flexShrink: 0, marginTop: 4 }}
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDeleteMessage(msgIndex);
                        }}
                      />
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Input area */}
          <div style={{
            padding: "16px 24px",
            borderTop: "1px solid var(--zy-border)",
            background: "var(--zy-surface)",
          }}>
            <div style={{ display: "flex", gap: 12, alignItems: "flex-end" }}>
              <TextArea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onPressEnter={(e) => {
                  if (!e.shiftKey && !streaming) {
                    e.preventDefault();
                    sendMessage();
                  }
                }}
                placeholder="输入你的问题，如：华中科技大学的计算机专业怎么样？"
                autoSize={{ minRows: 1, maxRows: 4 }}
                disabled={streaming}
                style={{ flex: 1, borderRadius: 10, resize: "none" }}
              />
              {streaming ? (
                <Button
                  danger
                  icon={<PauseCircleOutlined />}
                  onClick={stopStreaming}
                  style={{ height: 42, borderRadius: 10 }}
                >
                  停止
                </Button>
              ) : (
                <Button
                  type="primary"
                  icon={<SendOutlined />}
                  onClick={sendMessage}
                  loading={loading}
                  style={{ height: 42, borderRadius: 10 }}
                >
                  发送
                </Button>
              )}
            </div>
            <div style={{ marginTop: 8 }}>
              <Select
                value={currentSkillId}
                onChange={setCurrentSkillId}
                style={{ width: 160 }}
                size="small"
                options={skills.map((s) => ({
                  value: s.id,
                  label: s.name,
                }))}
              />
            </div>
          </div>
        </div>
      </div>
    </AppLayout>
  );
}
