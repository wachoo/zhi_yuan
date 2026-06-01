"use client";

import { Layout, Menu, Button, Dropdown, Avatar, Typography } from "antd";
import {
  HomeOutlined,
  SearchOutlined,
  RobotOutlined,
  StarOutlined,
  LogoutOutlined,
  AimOutlined,
  UserOutlined,
  LockOutlined,
  CrownOutlined,
  SettingOutlined,
} from "@ant-design/icons";
import { useRouter, usePathname } from "next/navigation";
import { logout } from "@/lib/api";

const { Header, Content, Footer } = Layout;
const { Text } = Typography;

const menuItems = [
  { key: "/", icon: <HomeOutlined />, label: "首页" },
  { key: "/recommend", icon: <StarOutlined />, label: "智能推荐" },
  { key: "/universities", icon: <SearchOutlined />, label: "院校查询" },
  { key: "/chat", icon: <RobotOutlined />, label: "AI顾问" },
];

export default function AppLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();

  const userMenuItems = [
    {
      key: "profile",
      icon: <UserOutlined />,
      label: "个人详情",
      onClick: () => router.push("/profile"),
    },
    {
      key: "account",
      icon: <LockOutlined />,
      label: "账号安全",
      onClick: () => router.push("/profile/account"),
    },
    {
      key: "membership",
      icon: <CrownOutlined />,
      label: "会员中心",
      onClick: () => router.push("/profile/membership"),
    },
    { type: "divider" as const },
    {
      key: "logout",
      icon: <LogoutOutlined />,
      label: "退出登录",
      danger: true,
      onClick: logout,
    },
  ];

  return (
    <Layout style={{ minHeight: "100vh", background: "var(--zy-bg)" }}>
      <Header className="zy-header">
        <div className="zy-logo">
          <div className="zy-logo-icon">
            <AimOutlined />
          </div>
          <span>智愿</span>
        </div>
        <Menu
          mode="horizontal"
          selectedKeys={[pathname]}
          items={menuItems}
          onClick={(e) => router.push(e.key)}
        />
        <Dropdown
          menu={{ items: userMenuItems }}
          trigger={["click"]}
          placement="bottomRight"
        >
          <Button
            type="text"
            style={{
              display: "flex",
              alignItems: "center",
              gap: 8,
              padding: "4px 8px",
              flexShrink: 0,
            }}
          >
            <Avatar
              size={28}
              icon={<UserOutlined />}
              style={{
                background: "linear-gradient(135deg, var(--zy-primary), var(--zy-secondary))",
              }}
            />
          </Button>
        </Dropdown>
      </Header>
      <Content className="zy-content">
        {children}
      </Content>
      <Footer className="zy-footer">
        智愿 &copy; 2026 — 所有推荐结果仅供参考，请结合多方信息综合决策
      </Footer>
    </Layout>
  );
}
