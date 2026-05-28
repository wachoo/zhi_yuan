"use client";

import { useEffect, useState } from "react";
import { Table, Input, Select, Space, Tag, Card } from "antd";
import api from "@/lib/api";
import AppLayout from "@/components/Layout";
import { University } from "@/types";

export default function UniversitiesPage() {
  const [universities, setUniversities] = useState<University[]>([]);
  const [loading, setLoading] = useState(true);
  const [keyword, setKeyword] = useState("");
  const [level, setLevel] = useState<string | undefined>();

  const fetchUniversities = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (keyword) params.set("keyword", keyword);
      if (level) params.set("level", level);
      const res = await api.get(`/api/universities?${params}`);
      setUniversities(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchUniversities(); }, [keyword, level]);

  const columns = [
    { title: "院校名称", dataIndex: "name", key: "name" },
    { title: "所在地", dataIndex: "city", key: "city", render: (city: string, r: University) => `${r.province} · ${city}` },
    { title: "层次", dataIndex: "level", key: "level", render: (level: string) => <Tag color="blue">{level}</Tag> },
    { title: "类型", dataIndex: "type", key: "type" },
    { title: "学费区间", key: "tuition", render: (_: unknown, r: University) => r.tuition_min ? `¥${r.tuition_min}-${r.tuition_max}` : "-" },
  ];

  return (
    <AppLayout>
      <Card>
        <Space style={{ marginBottom: 16 }}>
          <Input.Search placeholder="搜索院校名称" onSearch={setKeyword} style={{ width: 300 }} />
          <Select placeholder="院校层次" allowClear style={{ width: 150 }} onChange={setLevel}
            options={[
              { value: "985", label: "985" }, { value: "211", label: "211" },
              { value: "双一流", label: "双一流" }, { value: "普通本科", label: "普通本科" },
            ]} />
        </Space>
        <Table dataSource={universities} columns={columns} rowKey="id" loading={loading} />
      </Card>
    </AppLayout>
  );
}
