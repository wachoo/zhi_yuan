"use client";

import { useEffect, useState } from "react";
import { Table, Input, Select, Tag, Card, Typography, Space } from "antd";
import { TablePaginationConfig } from "antd";
import { SearchOutlined, EnvironmentOutlined } from "@ant-design/icons";
import api from "@/lib/api";
import AppLayout from "@/components/Layout";
import { University, PaginatedUniversityResponse } from "@/types";

const { Title, Text } = Typography;

export default function UniversitiesPage() {
  const [universities, setUniversities] = useState<University[]>([]);
  const [loading, setLoading] = useState(true);
  const [keyword, setKeyword] = useState("");
  const [level, setLevel] = useState<string | undefined>();
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const [total, setTotal] = useState(0);

  const fetchUniversities = async (
    currentPage = page,
    currentPageSize = pageSize,
  ) => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (keyword) params.set("keyword", keyword);
      if (level) params.set("level", level);
      params.set("page", String(currentPage));
      params.set("page_size", String(currentPageSize));
      const res = await api.get<PaginatedUniversityResponse>(
        `/api/universities?${params}`,
      );
      setUniversities(res.data.items);
      setTotal(res.data.total);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    setPage(1); // eslint-disable-line react-hooks/set-state-in-effect
    fetchUniversities(1, pageSize);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [keyword, level]);

  const handleTableChange = (pagination: TablePaginationConfig) => {
    const newPage = pagination.current || 1;
    const newPageSize = pagination.pageSize || 20;
    setPage(newPage);
    setPageSize(newPageSize);
    fetchUniversities(newPage, newPageSize);
  };

  const levelColors: Record<string, string> = {
    "985": "error",
    "211": "warning",
    双一流: "processing",
    普通本科: "default",
  };

  const columns = [
    {
      title: "排名",
      dataIndex: "ranking",
      key: "ranking",
      width: 80,
      render: (ranking: number | null) =>
        ranking ? (
          <Text strong style={{ color: "var(--zy-primary)" }}>
            #{ranking}
          </Text>
        ) : (
          "-"
        ),
    },
    {
      title: "院校名称",
      dataIndex: "name",
      key: "name",
      render: (name: string) => <Text strong>{name}</Text>,
    },
    {
      title: "所在地",
      dataIndex: "city",
      key: "city",
      render: (city: string, r: University) => (
        <Space size={4}>
          <EnvironmentOutlined style={{ color: "var(--zy-text-muted)" }} />
          <Text>
            {r.province} · {city}
          </Text>
        </Space>
      ),
    },
    {
      title: "层次",
      dataIndex: "level",
      key: "level",
      render: (level: string) => (
        <Tag
          color={levelColors[level] || "default"}
          style={{ borderRadius: 4 }}
        >
          {level}
        </Tag>
      ),
    },
    {
      title: "类型",
      dataIndex: "type",
      key: "type",
    },
    {
      title: "学费区间",
      key: "tuition",
      render: (_: unknown, r: University) =>
        r.tuition_min ? (
          <Text type="secondary">
            ¥{r.tuition_min.toLocaleString()}-{r.tuition_max?.toLocaleString()}
          </Text>
        ) : (
          "-"
        ),
    },
  ];

  const expandedRowRender = (record: University) => (
    <div style={{ padding: "8px 0" }}>
      {record.description && (
        <div style={{ marginBottom: 12 }}>
          <Text
            type="secondary"
            style={{ fontSize: 13, display: "block", marginBottom: 6 }}
          >
            院校简介
          </Text>
          <Text style={{ lineHeight: 1.8 }}>{record.description}</Text>
        </div>
      )}
      <div style={{ display: "flex", gap: 24, flexWrap: "wrap" }}>
        {record.website && (
          <div>
            <Text type="secondary" style={{ fontSize: 13 }}>
              官网：
            </Text>{" "}
            <a
              href={record.website}
              target="_blank"
              rel="noopener noreferrer"
              style={{ color: "var(--zy-secondary)" }}
            >
              {record.website}
            </a>
          </div>
        )}
        {record.tags && record.tags.length > 0 && (
          <div>
            <Text type="secondary" style={{ fontSize: 13 }}>
              标签：
            </Text>{" "}
            {record.tags.map((tag, idx) => (
              <Tag
                key={idx}
                style={{
                  borderRadius: 4,
                  background: "var(--zy-muted)",
                  border: "none",
                  color: "var(--zy-text-secondary)",
                }}
              >
                {tag}
              </Tag>
            ))}
          </div>
        )}
      </div>
    </div>
  );

  return (
    <AppLayout>
      <Space orientation="vertical" size="large" style={{ width: "100%" }}>
        <div>
          <Title level={3} style={{ margin: "0 0 4px" }}>
            院校查询
          </Title>
          <Text type="secondary">浏览全国 {total} 所院校信息</Text>
        </div>

        <Card
          style={{ borderRadius: 12, border: "1px solid var(--zy-border)" }}
        >
          <Space style={{ marginBottom: 20 }} wrap>
            <Input.Search
              placeholder="搜索院校名称"
              onSearch={(val) => setKeyword(val)}
              style={{ width: 280 }}
              allowClear
              prefix={
                <SearchOutlined style={{ color: "var(--zy-text-muted)" }} />
              }
              size="large"
            />
            <Select
              placeholder="院校层次"
              allowClear
              style={{ width: 150 }}
              onChange={setLevel}
              size="large"
              options={[
                { value: "985", label: "985" },
                { value: "211", label: "211" },
                { value: "双一流", label: "双一流" },
                { value: "普通本科", label: "普通本科" },
              ]}
            />
          </Space>
          <Table
            dataSource={universities}
            columns={columns}
            rowKey="id"
            loading={loading}
            expandable={{
              expandedRowRender,
              rowExpandable: () => true,
            }}
            pagination={{
              current: page,
              pageSize: pageSize,
              total: total,
              showSizeChanger: true,
              showQuickJumper: true,
              showTotal: (total) => `共 ${total} 所院校`,
              pageSizeOptions: ["10", "20", "50"],
            }}
            onChange={handleTableChange}
          />
        </Card>
      </Space>
    </AppLayout>
  );
}
