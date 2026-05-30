"use client";

import { Suspense, useEffect, useState } from "react";
import { Card, Table, Tag, Typography, Space, Progress, Spin, Alert, Button } from "antd";
import { DownloadOutlined } from "@ant-design/icons";
import { useSearchParams, useRouter } from "next/navigation";
import api from "@/lib/api";
import AppLayout from "@/components/Layout";
import { RecommendResult } from "@/types";

const { Title } = Typography;

function RecommendContent() {
  const params = useSearchParams();
  const router = useRouter();
  const [result, setResult] = useState<RecommendResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const score = params.get("score");
  const rank = params.get("rank");
  const province = params.get("province");
  const subject_type = params.get("subject_type");
  const exam_type = params.get("exam_type");

  useEffect(() => {
    // URL 参数优先，缺失时从用户画像获取
    const fetchAndRecommend = async () => {
      let pScore = score;
      let pRank = rank;
      let pProvince = province;
      let pSubjectType = subject_type;
      let pExamType = exam_type;

      // URL 参数不全，尝试从画像补全
      if (!pScore || !pRank || !pProvince || !pSubjectType) {
        let token = localStorage.getItem("token");
        if (!token) {
          try {
            const authRes = await api.post("/api/auth/register", {
              phone: "13800138000",
              password: "test123",
            }).catch(() => api.post("/api/auth/login", { phone: "13800138000", password: "test123" }));
            token = authRes.data.access_token;
            if (token) {
              localStorage.setItem("token", token);
            }
          } catch {
            setError("未登录，请先从首页获取推荐");
            setLoading(false);
            return;
          }
        }
        try {
          const profileRes = await api.get("/api/profile");
          const basic = profileRes.data?.basic_info;
          if (basic) {
            pScore = pScore ?? String(basic.score ?? "");
            pRank = pRank ?? String(basic.rank ?? "");
            pProvince = pProvince ?? basic.province ?? "";
            pSubjectType = pSubjectType ?? basic.subject_type ?? "";
            pExamType = pExamType ?? basic.exam_type ?? "普通类";
          }
        } catch (err: any) {
          if (err?.response?.status === 404) {
            setError("暂无用户画像，请先从首页填写信息");
          } else {
            setError("获取画像失败，请从首页重新提交");
          }
          setLoading(false);
          return;
        }
      }

      console.log("[Recommend] Params:", { pScore, pRank, pProvince, pSubjectType, pExamType });

      if (!pScore || !pRank || !pProvince || !pSubjectType) {
        setError("缺少必要参数（分数、位次、省份、科类），请先从首页填写信息");
        setLoading(false);
        return;
      }

      setLoading(true);
      setError(null);
      try {
        const payload = {
          score: Number(pScore),
          rank: Number(pRank),
          province: pProvince,
          subject_type: pSubjectType,
          exam_type: pExamType || "普通类",
        };
        console.log("[Recommend] Request payload:", payload);
        const res = await api.post("/api/recommend", payload);
        console.log("[Recommend] Response:", res.status, res.data);
        setResult(res.data);
      } catch (err: any) {
        const status = err?.response?.status;
        const detail = err?.response?.data?.detail || err?.message || "未知错误";
        console.error("[Recommend] Error:", status, detail, err);
        setError(`请求失败 (${status || "网络错误"}): ${detail}`);
      } finally {
        setLoading(false);
      }
    };
    fetchAndRecommend();
  }, [score, rank, province, subject_type, exam_type]);

  const columns = [
    { title: "院校", dataIndex: "university_name", key: "university_name" },
    { title: "专业", dataIndex: "major_name", key: "major_name" },
    { title: "历年最低位次", dataIndex: "min_rank", key: "min_rank" },
    { title: "适配度", dataIndex: "adapter_score", key: "adapter_score",
      render: (score: number) => score ? <Progress percent={score} size="small" /> : "-" },
  ];

  const handleExport = () => {
    const token = localStorage.getItem("token");
    if (!token) {
      setError("未登录，无法导出");
      return;
    }

    const baseURL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
    const exportURL = `${baseURL}/api/recommend/export`;

    // Use fetch to add auth header and download as blob
    fetch(exportURL, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((response) => {
        if (!response.ok) throw new Error("Export failed");
        return response.blob();
      })
      .then((blob) => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `志愿推荐方案_${new Date().toISOString().slice(0, 10)}.xlsx`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      })
      .catch((err) => {
        console.error("Export error:", err);
        setError("导出失败，请重试");
      });
  };

  const isEmpty = result && result.rush.length === 0 && result.stable.length === 0 && result.safe.length === 0;

  return (
    <AppLayout>
      <Space direction="vertical" size="large" style={{ width: "100%" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <Title level={3} style={{ margin: 0 }}>推荐方案</Title>
          {result && !isEmpty && (
            <Button
              type="primary"
              icon={<DownloadOutlined />}
              onClick={handleExport}
              loading={loading}
            >
              导出志愿表
            </Button>
          )}
        </div>

        {error && (
          <Alert
            type="error"
            showIcon
            message="获取推荐失败"
            description={
              <Space direction="vertical">
                <span>{error}</span>
                <Button type="link" onClick={() => router.push("/")} style={{ padding: 0 }}>
                  返回首页重新提交
                </Button>
              </Space>
            }
          />
        )}

        {!loading && !error && isEmpty && (
          <Alert
            type="warning"
            showIcon
            message="暂无推荐结果"
            description="当前条件下未找到匹配的院校，请尝试调整分数或位次后重新查询。"
          />
        )}

        {result?.profile_completeness !== undefined && result.profile_completeness < 0.4 && (
          <Card>
            <Progress percent={Math.round(result.profile_completeness * 100)}
              format={(p) => `完整度 ${p}%`} />
            <p>完善个人详情可获得更精准的推荐结果</p>
          </Card>
        )}

        <Card title={<span><Tag color="red">冲</Tag> 冲刺院校</span>}>
          <Table dataSource={result?.rush || []} columns={columns} rowKey={(r) => `${r.university_name}-${r.major_name}`}
            loading={loading} pagination={false} />
        </Card>

        <Card title={<span><Tag color="blue">稳</Tag> 稳妥院校</span>}>
          <Table dataSource={result?.stable || []} columns={columns} rowKey={(r) => `${r.university_name}-${r.major_name}`}
            loading={loading} pagination={false} />
        </Card>

        <Card title={<span><Tag color="green">保</Tag> 保底院校</span>}>
          <Table dataSource={result?.safe || []} columns={columns} rowKey={(r) => `${r.university_name}-${r.major_name}`}
            loading={loading} pagination={false} />
        </Card>
      </Space>
    </AppLayout>
  );
}

export default function RecommendPage() {
  return (
    <Suspense fallback={<Spin size="large" style={{ display: "block", margin: "100px auto" }} />}>
      <RecommendContent />
    </Suspense>
  );
}
