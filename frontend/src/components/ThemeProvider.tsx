"use client";

import { ConfigProvider } from "antd";
import zhCN from "antd/locale/zh_CN";
import { zhiYuanTheme } from "@/lib/theme";

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  return (
    <ConfigProvider theme={zhiYuanTheme} locale={zhCN}>
      {children}
    </ConfigProvider>
  );
}
