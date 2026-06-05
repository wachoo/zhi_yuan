"use client";

import { usePathname, useRouter } from "next/navigation";
import { UserOutlined, LockOutlined, CrownOutlined } from "@ant-design/icons";
import AppLayout from "@/components/Layout";

const sidebarItems = [
  { key: "/profile", icon: <UserOutlined />, label: "个人详情" },
  { key: "/profile/account", icon: <LockOutlined />, label: "账号安全" },
  { key: "/profile/membership", icon: <CrownOutlined />, label: "会员中心" },
];

export default function ProfileLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const router = useRouter();

  return (
    <AppLayout>
      <div style={{ display: "flex", gap: 24, alignItems: "flex-start" }}>
        {/* Left sidebar */}
        <div
          style={{
            width: 200,
            flexShrink: 0,
            background: "var(--zy-surface)",
            border: "1px solid var(--zy-border)",
            borderRadius: 12,
            overflow: "hidden",
          }}
        >
          <div
            style={{
              padding: "16px 16px 12px",
              borderBottom: "1px solid var(--zy-border-light)",
            }}
          >
            <div
              style={{ fontWeight: 600, fontSize: 15, color: "var(--zy-text)" }}
            >
              个人中心
            </div>
          </div>
          <nav style={{ padding: "6px 0" }}>
            {sidebarItems.map((item) => {
              const isActive = pathname === item.key;
              return (
                <button
                  key={item.key}
                  onClick={() => router.push(item.key)}
                  className={`zy-settings-nav-item ${isActive ? "zy-settings-nav-active" : ""}`}
                  style={{ borderRadius: 0, padding: "10px 16px" }}
                >
                  {item.icon}
                  <span>{item.label}</span>
                </button>
              );
            })}
          </nav>
        </div>

        {/* Right content */}
        <div style={{ flex: 1, minWidth: 0 }}>{children}</div>
      </div>
    </AppLayout>
  );
}
