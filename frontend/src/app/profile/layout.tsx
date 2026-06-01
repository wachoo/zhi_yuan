"use client";

import { usePathname, useRouter } from "next/navigation";
import {
  UserOutlined,
  LockOutlined,
  CrownOutlined,
} from "@ant-design/icons";
import AppLayout from "@/components/Layout";

const sidebarItems = [
  { key: "/profile", icon: <UserOutlined />, label: "个人详情" },
  { key: "/profile/account", icon: <LockOutlined />, label: "账号安全" },
  { key: "/profile/membership", icon: <CrownOutlined />, label: "会员中心" },
];

export default function ProfileLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();

  return (
    <AppLayout>
      <div style={{ display: "flex", gap: 32, alignItems: "flex-start" }}>
        {/* Left sidebar */}
        <nav className="zy-settings-sidebar">
          {sidebarItems.map((item) => {
            const isActive = pathname === item.key;
            return (
              <button
                key={item.key}
                onClick={() => router.push(item.key)}
                className={`zy-settings-nav-item ${isActive ? "zy-settings-nav-active" : ""}`}
              >
                {item.icon}
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>

        {/* Right content */}
        <div style={{ flex: 1, minWidth: 0 }}>
          {children}
        </div>
      </div>
    </AppLayout>
  );
}
