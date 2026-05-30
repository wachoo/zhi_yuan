"use client";

import { Layout, Menu, Button } from "antd";
import {
  HomeOutlined,
  SearchOutlined,
  RobotOutlined,
  SettingOutlined,
  StarOutlined,
  LogoutOutlined,
  AimOutlined,
} from "@ant-design/icons";
import { useRouter, usePathname } from "next/navigation";
import { logout } from "@/lib/api";

const { Header, Content, Footer } = Layout;

const menuItems = [
  { key: "/", icon: <HomeOutlined />, label: "首页" },
  { key: "/recommend", icon: <StarOutlined />, label: "智能推荐" },
  { key: "/universities", icon: <SearchOutlined />, label: "院校查询" },
  { key: "/chat", icon: <RobotOutlined />, label: "AI顾问" },
  { key: "/profile", icon: <SettingOutlined />, label: "个人中心" },
];

export default function AppLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();

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
        <Button
          type="text"
          icon={<LogoutOutlined />}
          onClick={logout}
          style={{ color: "var(--zy-text-secondary)", flexShrink: 0 }}
        >
          退出
        </Button>
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
