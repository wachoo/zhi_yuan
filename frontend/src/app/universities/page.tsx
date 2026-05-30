"use client";

import { useEffect, useState } from "react";
import { Table, Input, Select, Space, Tag, Card, Typography } from "antd";
import api from "@/lib/api";
import AppLayout from "@/components/Layout";
import { University, PaginatedUniversityResponse } from "@/types";

const { Text } = Typography;

export default function UniversitiesPage() {
  const [universities, setUniversities] = useState<University[]>([]);
  const [loading, setLoading] = useState(true);
  const [keyword, setKeyword] = useState("");
  const [level, setLevel] = useState<string | undefined>();
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const [total, setTotal] = useState(0);

  const fetchUniversities = async (currentPage = page, currentPageSize = pageSize) => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (keyword) params.set("keyword", keyword);
      if (level) params.set("level", level);
      params.set("page", String(currentPage));
      params.set("page_size", String(currentPageSize));
      const res = await api.get<PaginatedUniversityResponse>(`/api/universities?${params}`);
      setUniversities(res.data.items);
      setTotal(res.data.total);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    setPage(1);
    fetchUniversities(1, pageSize);
  }, [keyword, level]);

  const handleTableChange = (pagination: any) => {
    const newPage = pagination.current || 1;
    const newPageSize = pagination.pageSize || 20;
    setPage(newPage);
    setPageSize(newPageSize);
    fetchUniversities(newPage, newPageSize);
  };

  const columns = [
    { title: "排名", dataIndex: "ranking", key: "ranking", width: 80, render: (ranking: number | null) => ranking ? `#${ranking}` : "-" },
    { title: "院校名称", dataIndex: "name", key: "name" },
    { title: "所在地", dataIndex: "city", key: "city", render: (city: string, r: University) => `${r.province} · ${city}` },
    { title: "层次", dataIndex: "level", key: "level", render: (level: string) => <Tag color="blue">{level}</Tag> },
    { title: "类型", dataIndex: "type", key: "type" },
    { title: "学费区间", key: "tuition", render: (_: unknown, r: University) => r.tuition_min ? `¥${r.tuition_min}-${r.tuition_max}` : "-" },
  ];

  const expandedRowRender = (record: University) => (
    <div style={{ padding: "16px 0" }}>
      <div style={{ marginBottom: 12 }}>
        <Text strong>院校简介：</Text>
      </div>
      <div style={{ lineHeight: 1.8, color: "#595959" }}>
        {record.description || "暂无详细介绍"}
      </div>
      {record.website && (
        <div style={{ marginTop: 12 }}>
          <Text strong>官网：</Text>{" "}
          <a href={record.website} target="_blank" rel="noopener noreferrer">
            {record.website}
          </a>
        </div>
      )}
      {record.tags && record.tags.length > 0 && (
        <div style={{ marginTop: 12 }}>
          <Text strong>标签：</Text>{" "}
          {record.tags.map((tag, idx) => (
            <Tag key={idx} color="green">{tag}</Tag>
          ))}
        </div>
      )}
    </div>
  );

  return (
    <AppLayout>
      <Card>
        <Space style={{ marginBottom: 16 }}>
          <Input.Search
            placeholder="搜索院校名称"
            onSearch={(val) => setKeyword(val)}
            style={{ width: 300 }}
            allowClear
          />
          <Select
            placeholder="院校层次"
            allowClear
            style={{ width: 150 }}
            onChange={setLevel}
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
    </AppLayout>
  );
}
