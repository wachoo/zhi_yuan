"use client";

import { Layout, Menu } from "antd";
import {
  HomeOutlined,
  SearchOutlined,
  RobotOutlined,
  UserOutlined,
  StarOutlined,
} from "@ant-design/icons";
import { useRouter, usePathname } from "next/navigation";

const { Header, Content, Footer } = Layout;

const menuItems = [
  { key: "/", icon: <HomeOutlined />, label: "首页" },
  { key: "/recommend", icon: <StarOutlined />, label: "智能推荐" },
  { key: "/universities", icon: <SearchOutlined />, label: "院校查询" },
  { key: "/chat", icon: <RobotOutlined />, label: "AI顾问" },
  { key: "/profile", icon: <UserOutlined />, label: "我的画像" },
];

export default function AppLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();

  return (
    <Layout style={{ minHeight: "100vh" }}>
      <Header>
        <div style={{ float: "left", color: "#fff", fontSize: 20, fontWeight: "bold", marginRight: 40 }}>
          智愿
        </div>
        <Menu
          theme="dark"
          mode="horizontal"
          selectedKeys={[pathname]}
          items={menuItems}
          onClick={(e) => router.push(e.key)}
        />
      </Header>
      <Content style={{ padding: "24px 48px" }}>
        {children}
      </Content>
      <Footer style={{ textAlign: "center" }}>
        智愿 &copy; 2026 — 所有推荐结果仅供参考，请结合多方信息综合决策
      </Footer>
    </Layout>
  );
}
