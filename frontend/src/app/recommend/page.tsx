"use client";

import { useEffect, useState } from "react";
import { Card, Table, Tag, Typography, Space, Progress } from "antd";
import { useSearchParams } from "next/navigation";
import api from "@/lib/api";
import AppLayout from "@/components/Layout";
import { RecommendResult } from "@/types";

const { Title } = Typography;

export default function RecommendPage() {
  const params = useSearchParams();
  const [result, setResult] = useState<RecommendResult | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchRecommend = async () => {
      try {
        const res = await api.post("/api/recommend", {
          score: Number(params.get("score")),
          rank: Number(params.get("rank")),
          province: params.get("province"),
          subject_type: params.get("subject_type"),
        });
        setResult(res.data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchRecommend();
  }, [params]);

  const columns = [
    { title: "院校", dataIndex: "university_name", key: "university_name" },
    { title: "专业", dataIndex: "major_name", key: "major_name" },
    { title: "历年最低位次", dataIndex: "min_rank", key: "min_rank" },
    { title: "适配度", dataIndex: "adapter_score", key: "adapter_score",
      render: (score: number) => score ? <Progress percent={score} size="small" /> : "-" },
  ];

  return (
    <AppLayout>
      <Space direction="vertical" size="large" style={{ width: "100%" }}>
        <Title level={3}>推荐方案</Title>

        {result?.profile_completeness !== undefined && result.profile_completeness < 0.4 && (
          <Card>
            <Progress percent={Math.round(result.profile_completeness * 100)}
              format={(p) => `画像完整度 ${p}%`} />
            <p>完善个人画像可获得更精准的推荐结果</p>
          </Card>
        )}

        <Card title={<span><Tag color="red">冲</Tag> 冲刺院校</span>}>
          <Table dataSource={result?.rush || []} columns={columns} rowKey="university_name"
            loading={loading} pagination={false} />
        </Card>

        <Card title={<span><Tag color="blue">稳</Tag> 稳妥院校</span>}>
          <Table dataSource={result?.stable || []} columns={columns} rowKey="university_name"
            loading={loading} pagination={false} />
        </Card>

        <Card title={<span><Tag color="green">保</Tag> 保底院校</span>}>
          <Table dataSource={result?.safe || []} columns={columns} rowKey="university_name"
            loading={loading} pagination={false} />
        </Card>
      </Space>
    </AppLayout>
  );
}
