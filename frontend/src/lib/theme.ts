"use client";

import { theme } from "antd";
import type { ThemeConfig } from "antd";

/**
 * 智愿 EdTech 设计主题
 * 风格：教育科技简约风 — 可信、专业、清晰
 * 受众：高考生 + 家长（年龄跨度 17-55）
 */
export const zhiYuanTheme: ThemeConfig = {
  token: {
    // 品牌色
    colorPrimary: "#1E3A5F",
    colorLink: "#2563EB",
    colorSuccess: "#059669",
    colorWarning: "#D97706",
    colorError: "#DC2626",

    // 背景与表面
    colorBgContainer: "#FFFFFF",
    colorBgLayout: "#F8FAFC",
    colorBorder: "#E2E8F0",
    colorBorderSecondary: "#F1F5F9",

    // 文字
    colorText: "#0F172A",
    colorTextSecondary: "#475569",
    colorTextTertiary: "#94A3B8",
    colorTextQuaternary: "#CBD5E1",

    // 排版
    fontFamily: '"Noto Sans SC", "PingFang SC", "Microsoft YaHei", -apple-system, BlinkMacSystemFont, sans-serif',
    fontSize: 14,
    fontSizeHeading1: 30,
    fontSizeHeading2: 24,
    fontSizeHeading3: 20,
    fontSizeHeading4: 16,
    lineHeight: 1.6,

    // 圆角
    borderRadius: 8,
    borderRadiusLG: 12,
    borderRadiusSM: 6,

    // 阴影
    boxShadow: "0 1px 3px rgba(15, 23, 42, 0.08), 0 1px 2px rgba(15, 23, 42, 0.04)",
    boxShadowSecondary: "0 4px 12px rgba(15, 23, 42, 0.08)",

    // 间距
    padding: 16,
    paddingLG: 24,
    marginLG: 24,
  },
  components: {
    Layout: {
      headerBg: "#FFFFFF",
      headerColor: "#0F172A",
      headerHeight: 64,
      headerPadding: "0 32px",
      footerBg: "#F8FAFC",
      footerPadding: "24px 32px",
      bodyBg: "#F8FAFC",
    },
    Menu: {
      itemColor: "#475569",
      itemHoverColor: "#1E3A5F",
      itemSelectedColor: "#1E3A5F",
      itemSelectedBg: "transparent",
      horizontalItemSelectedBg: "transparent",
      horizontalItemHoverColor: "#1E3A5F",
      horizontalLineHeight: "64px",
      activeBarBorderWidth: 2,
    },
    Button: {
      primaryShadow: "0 1px 2px rgba(30, 58, 95, 0.2)",
      fontWeight: 500,
    },
    Card: {
      headerBg: "transparent",
      paddingLG: 24,
    },
    Input: {
      controlHeight: 40,
      controlHeightLG: 44,
    },
    Select: {
      controlHeight: 40,
      controlHeightLG: 44,
    },
    InputNumber: {
      controlHeight: 40,
      controlHeightLG: 44,
    },
    Table: {
      headerBg: "#F8FAFC",
      headerColor: "#475569",
      headerSortActiveBg: "#F1F5F9",
      rowHoverBg: "#F1F5F9",
      borderColor: "#E2E8F0",
    },
    Tabs: {
      inkBarColor: "#1E3A5F",
      itemActiveColor: "#1E3A5F",
      itemSelectedColor: "#1E3A5F",
      itemHoverColor: "#1E3A5F",
    },
    Progress: {
      defaultColor: "#1E3A5F",
    },
    Tag: {
      borderRadiusSM: 4,
    },
  },
  algorithm: theme.defaultAlgorithm,
};
