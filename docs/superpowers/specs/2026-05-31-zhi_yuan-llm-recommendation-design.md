# 智愿 — AI 高考志愿填报助手 产品设计文档

> 创建日期：2026-05-28 · 更新日期：2026-05-31
> 版本：v2.0
> 方案：结构化引擎 + LLM 增强层 + 多角色对话 + 会员体系

---

## 1. 产品定位

**一句话定位**：基于五维用户画像 + 结构化数据引擎 + LLM 多角色智能解读的高考志愿填报助手。

**目标用户**：C 端考生及家长

**产品形态**：Web 网站（Next.js + FastAPI + PostgreSQL）

**商业模式**：免费基础功能 + 四级会员订阅（free / standard / deep / vip）

**差异化**：用 AI 把"万元级人工咨询"的深度，做到"百元级产品"的价格；多角色 AI 顾问（智愿顾问 / 张雪峰视角）提供不同风格的志愿建议。

---

## 2. 用户画像 · 五维输入模型

### 2.1 维度定义

| 维度 | 存储字段 | 后端 Schema | 前端表单 |
|------|---------|-------------|---------|
| **基础信息** | `basic_info` (JSONB) | score (0-750), rank (≥0), province, subject_type, exam_type | InputNumber + Select + Radio |
| **家庭维度** | `family_info` (JSONB) | income_range, tuition_max, prefer_city[], parent_industry | InputNumber + Select(multiple) |
| **性格维度** | `personality` (JSONB) | interests[], dislikes[], holland_code, mbti, introvert_extrovert | Select(tags) |
| **能力维度** | `ability` (JSONB) | strong_subjects[], social_ability (1-5), english_level (1-6), awards[] | Select(tags) + Slider |
| **价值观维度** | `values_info` (JSONB) | career_values[], distance_preference, plan, industry_preference[] | Checkbox.Group + Select |

**画像完整度计算**：`completeness = filled_dimensions / 5`（每维度非 null 计 1）

### 2.2 科类与考试类型

| 科类 (subject_type) | 说明 |
|---------------------|------|
| 物理类 | 新高考物理方向 |
| 历史类 | 新高考历史方向 |
| 综合改革 | 北京/上海/浙江等综合改革省份 |
| 理科 / 文科 | 老高考省份 |

| 考试类型 (exam_type) | 说明 |
|---------------------|------|
| 普通类 | 可报考大部分本科专业 |
| 艺术类 | 需省统考/校考，可选艺术类专业 |
| 体育类 | 需体育专业测试，可选体育类专业 |

### 2.3 采集流程

1. **首页快速输入**（必填）：分数 + 位次 + 省份 + 科类 + 考试类型 → 即刻生成冲稳保推荐
2. **个人中心 · 个人详情**（引导填写）：五维画像完整表单，含兴趣/厌恶标签、偏好城市、能力滑块、价值观等
3. **AI 对话追问**（动态补充）：LLM 可在对话中调用 `get_user_profile` 工具读取画像，基于上下文追问

---

## 3. 核心功能矩阵

| 功能模块 | 免费/付费 | 页面路由 | 说明 |
|---------|----------|---------|------|
| 首页快速推荐 | 免费 | `/` | 输入分数 → 生成冲稳保 |
| 院校智能查询 | 免费 | `/universities` | 按关键词/层次/省份筛选，分页表格 |
| 智能推荐 | 免费(8所/组)/付费(完整) | `/recommend` | 冲/稳/保三档 + 适配度评分 + Excel 导出 |
| AI 志愿顾问 | 免费(3次/天)/付费(无限) | `/chat` | 多角色流式对话 + 工具调用 + Markdown 渲染 |
| 个人中心 | 全功能 | `/profile` | 三个 Tab：个人详情 / 账号安全 / 会员中心 |
| 会员体系 | — | 个人中心内 | 四级会员（free/standard/deep/vip） |

### 用户旅程

```
注册 → 首页输入分数 → 生成冲稳保推荐(8所/组) → 查看院校/导出 Excel
                    ↓
           个人中心完善五维画像 → 重新推荐(完整结果 + 适配度评分)
                    ↓
           AI 顾问对话(选角色) → 查询院校/专业/录取数据 → 个性化建议
                    ↓
           升级会员 → 解锁完整推荐 + 无限对话 + 深度报告
```

---

## 4. 技术架构

### 4.1 架构分层

```
前端层 (Next.js 16 + React 19 + Ant Design 5 + TailwindCSS 4)
  首页快速推荐 | 院校查询 | 智能推荐(Excel导出) | AI对话(SSE流式) | 个人中心(Tabs)
       │
API 层 (FastAPI + SQLAlchemy async + JWT 鉴权)
  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
  │ 认证服务      │ │ 画像服务     │ │ 支付服务     │
  │ · 注册/登录   │ │ · 五维存储   │ │ · 四级会员   │
  │ · JWT 24h    │ │ · 完整度追踪 │ │ · 模拟支付   │
  │ · 改密/退出   │ │ · 渐进采集   │ │ · 订单管理   │
  └──────┬──────┘ └──────┬──────┘ └──────┬──────┘
         │               │               │
  ┌──────┴───────────────┴───────────────┴──────┐
  │               推荐引擎服务                    │
  │ · 位次换算(RankConverter)                     │
  │ · 录取记录筛选(RecommendationEngine.filter)   │
  │ · 冲稳保分类(RecommendationEngine.categorize) │
  │ · 六维适配度评分(AdapterScorer)               │
  │ · LLM 语义扩展(厌恶/兴趣关键词)               │
  │ · Excel 导出(ExportService)                   │
  └──────┬──────────────────────────┬────────────┘
         │                          │
  ┌──────┴──────┐            ┌──────┴──────┐
  │ 数据服务层   │            │ LLM 编排服务 │
  │ · 院校查询   │            │ · 6 工具调用  │
  │ · 专业查询   │            │ · 多轮对话    │
  │ · 录取分数   │            │ · 流式 SSE   │
  │ · 一分一段   │            │ · 多角色技能  │
  └──────┬──────┘            └──────┬──────┘
         └───────────┬──────────────┘
                     │
              数据层 (PostgreSQL)
              10 张表 · 6 次迁移
```

### 4.2 技术选型

| 层级 | 选型 | 版本 |
|------|------|------|
| 前端 | Next.js + React + Ant Design + TailwindCSS | 16.2 / 19 / 5 / 4 |
| 后端 | Python + FastAPI + SQLAlchemy (async) | 3.11 / 0.128 / 2.0 |
| 数据库 | PostgreSQL + asyncpg | — |
| LLM | 通义千问 (qwen3.7-max, 主) + DeepSeek (deepseek-v4-pro, 备) | — |
| 认证 | JWT (python-jose) + bcrypt | — |
| 导出 | openpyxl (Excel) | — |
| 部署 | Docker + Nginx | — |

### 4.3 推荐引擎算法

```
输入：用户五维画像 + 考试参数
输出：冲/稳/保院校列表 + 六维适配度评分

Step 1 · 位次换算 (RankConverter)
  equivalent_rank = current_rank × (target_year_plan_count / current_year_plan_count)
  支持批量换算多年历史数据

Step 2 · 录取记录查询 (AdmissionDAO)
  按 province + subject_type + exam_type 联合查询
  JOIN universities + majors 获取完整信息

Step 3 · 多条件筛选 (RecommendationEngine.filter)
  · 省份/科类/考试类型匹配
  · 学费 ≤ tuition_max（如有）
  · 厌恶专业过滤（LLM 语义扩展 或 硬编码关键词映射）

Step 4 · 冲稳保分类 (RecommendationEngine.categorize)
  rank_ratio = min_rank / equivalent_rank
  · 冲：ratio ∈ [0.70, 0.95)  → 有希望但有风险
  · 稳：ratio ∈ [0.95, 1.20)  → 较稳妥
  · 保：ratio ∈ [1.20, 2.00)  → 基本稳妥

Step 5 · 会员限制 (RecommendationEngine.limit_for_tier)
  · 免费用户：每组最多 8 所
  · 付费用户：完整结果

Step 6 · 六维适配度评分 (AdapterScorer)
  权重（默认）：basic=0.30, family=0.10, city=0.15,
               personality=0.25, ability=0.10, values=0.10
  动态调整：未填写的维度权重归零，已填维度按比例重新分配

Step 7 · 持久化 → Step 8 · 返回 RecommendResult
```

### 4.4 LLM 编排层

**LLM 不参与核心计算**，作为"理解和表达"层：

#### 工具调用 (6 个 Tool)

| 工具名 | 用途 | 调用服务 |
|--------|------|---------|
| `query_university` | 查询院校基本信息 | UniversityService |
| `query_major` | 查询专业详情（课程/就业/薪资） | MajorService |
| `query_admission_score` | 查询历年录取分数和位次 | AdmissionService |
| `query_score_segment` | 查询一分一段表 | AdmissionService |
| `get_user_profile` | 查询用户五维画像 | UserService |
| `get_user_recommendation` | 查询最近推荐结果 | RecommendService |

#### 多角色技能系统 (SkillRegistry)

| 技能 ID | 名称 | 风格 |
|---------|-----|------|
| `default` | 智愿顾问 | 专业、客观、数据驱动，9 条硬性规则 |
| `zhangxuefeng` | 名师张 | 犀利务实，阶层意识，反鸡汤，含红/黄/绿情绪档位 |


每个 Skill 定义：
- `system_prompt_template`：含 `{profile_summary}` 和 `{recommendation_summary}` 占位符
- `render_system_prompt()`：动态注入用户画像摘要 + 推荐结果
- `emotion_tiers`：情绪档位配置（张雪峰专属）

#### 对话流程

```
前端 Select 选择角色 → skill_id 随消息发送
  → ChatService(skill_id=xxx)
  → _gather_context()：获取画像摘要 + 推荐摘要
  → _build_messages()：拉取最近 10 条历史 + 当前消息
  → LLM.chat_stream()：多轮工具调用循环（最多 80 轮）
    → 每轮检查 tool_calls → 执行工具 → 追加结果 → 继续
    → 最终回复 SSE 流式输出
  → 前端 ReactMarkdown 实时渲染（含代码块自动修复 + 闪烁光标）
```

#### LLM 语义扩展

`semantic_expand()`：用 LLM 对厌恶/兴趣领域进行关键词扩展
- 输入：dislikes/interests 列表 + 数据库全量专业名
- 策略 1（有专业列表）：让 LLM 从列表中选择匹配专业
- 策略 2（无列表）：自由生成扩展关键词
- 10 分钟内存缓存（MD5 key），避免重复调用

### 4.5 对话系统

- **会话管理**：支持新建/切换/重命名/删除对话，按 session_id 分组
- **消息持久化**：ChatMessage 表存储 role/content/tool_calls
- **流式输出**：SSE (Server-Sent Events) + `StreamingResponse`
- **前端渲染**：`StreamingMarkdown` 组件实时渲染 + 自动修复未闭合代码块 + 闪烁光标动画
- **限流**：免费用户每日 3 次对话，付费用户无限制

---

## 5. 会员与支付体系

### 5.1 四级会员

| 层级 | 价格 | 核心权益 |
|------|------|---------|
| **免费版** | ¥0 | 推荐 8 所/组、AI 对话 3 次/天、基础画像 |
| **标准版** | ¥29.90 | 完整推荐结果、AI 对话无限、Excel 导出 |
| **深度版** | ¥59.90 | 标准版全部 + 深度分析报告 + 职业路径 |
| **VIP 版** | ¥99.90 | 深度版全部 + 真人顾问电话咨询 + 录取跟踪 |

### 5.2 支付流程（当前为模拟）

```
前端选择会员 + 支付方式(支付宝/微信)
  → POST /api/payment/orders → 返回 order_no + qr_content
  → 前端显示二维码 + 30 分钟倒计时
  → POST /api/payment/simulate → 模拟支付成功
  → 更新用户 membership_tier + membership_expires_at (+30 天)
  → 订单状态 → activated
```

### 5.3 订单模型

`Order` 表：order_no (ZY+时间戳+UUID), tier, amount, payment_method, status (pending→paid→activated→expired→cancelled), paid_at, membership_start/end

---

## 6. 数据体系

### 6.1 数据库表结构（10 张表）

```
users                          ← 用户账户
 ├── user_profiles (1:1)       ← 五维画像 (JSONB)
 ├── recommendations (1:N)     ← 推荐记录 (快照+结果)
 ├── chat_messages (1:N)       ← 对话消息
 ├── chat_sessions (1:N)       ← 对话会话
 └── orders (1:N)              ← 支付订单

universities                   ← 院校库 (3000+)
 ├── admission_records (1:N)   ← 历年录取数据
 └── university_majors (M:N)   ← 院校-专业关联

majors                         ← 专业库 (800+)
 └── admission_records (N:1)

score_segments                 ← 一分一段表
```

### 6.2 核心表字段

| 表 | 关键字段 | 说明 |
|---|---------|------|
| `users` | phone(unique), password_hash, membership_tier, daily_chat_count | 手机号登录，JWT 鉴权 |
| `user_profiles` | basic_info/family_info/personality/ability/values_info (JSONB), completeness | 五维灵活存储 |
| `universities` | name, province, city, level(985/211/双一流), type, tags[], tuition, ranking, lat/long | 院校基础信息 |
| `majors` | name, category, courses[], career_directions[], avg_salary, is_normal/is_art/is_sports | 专业 + 考试类型标记 |
| `admission_records` | university_id, major_id, province, year, subject_type, exam_type, min/avg/max score & rank | 核心录取数据 |
| `score_segments` | province, year, subject_type, score, count, cumulative_count | 一分一段 |
| `recommendations` | input_snapshot(JSONB), result(JSONB), tier | 推荐快照 |
| `chat_messages` | session_id, role, content, tool_calls(JSONB) | 对话持久化 |
| `orders` | order_no(unique), tier, amount, status, membership_start/end | 支付订单 |

### 6.3 数据库迁移历史（6 次）

1. 初始建表（universities, majors, admission_records, score_segments, users, user_profiles, recommendations, chat_messages, university_majors）
2. 院校表增加 `ranking` 字段
3. 录取记录增加 `exam_type` 字段（普通类/艺术类/体育类）
4. 专业表增加 `is_normal/is_art/is_sports` 布尔字段
5. 新增 `chat_sessions` 表（会话管理）
6. 新增 `orders` 表（支付订单）

---

## 7. 前端页面结构

### 7.1 页面路由

| 路由 | 页面 | 核心组件 |
|------|------|---------|
| `/` | 首页 | Hero + 快速输入表单 + 自动注册测试账号 |
| `/login` | 登录/注册 | 左右分栏 + Tabs(登录/注册) |
| `/recommend` | 智能推荐 | 冲/稳/保三色卡片 + 适配度表格 + Excel 导出 |
| `/universities` | 院校查询 | 搜索 + 筛选 + 分页表格 + 展开详情 |
| `/chat` | AI 顾问 | 左侧会话列表 + 右侧流式对话 + 角色选择 |
| `/profile` | 个人中心 | Tabs: 个人详情 / 账号安全 / 会员中心 |

### 7.2 设计体系

**主题色**：深靛蓝 `#1E3A5F` + 亮蓝 `#2563EB`

| 用途 | CSS 变量 | 色值 |
|------|---------|------|
| 主色 | `--zy-primary` | `#1E3A5F` |
| 强调色 | `--zy-secondary` | `#2563EB` |
| 点缀色 | `--zy-accent` | `#059669` |
| 背景 | `--zy-bg` | `#F8FAFC` |
| 主文字 | `--zy-text` | `#0F172A` |
| 冲 | `--zy-rush` | `#EF4444` |
| 稳 | `--zy-stable` | `#2563EB` |
| 保 | `--zy-safe` | `#10B981` |

**Ant Design 主题**：通过 `ConfigProvider` + 自定义 `ThemeConfig` 统一覆盖组件样式（圆角 8/12px、行高 1.6、字重 600）

---

## 8. 完整 API 清单

### 认证 (prefix: `/api/auth`)

| 方法 | 路径 | 鉴权 | 说明 |
|------|------|------|------|
| POST | `/register` | 无 | 手机号 + 密码注册 |
| POST | `/login` | 无 | 手机号 + 密码登录 |
| GET | `/me` | 必须 | 获取当前用户信息 |
| PUT | `/password` | 必须 | 修改密码（旧密码验证） |

### 画像 (prefix: `/api/profile`)

| 方法 | 路径 | 鉴权 | 说明 |
|------|------|------|------|
| GET | `/` | 必须 | 获取五维画像 + 完整度 |
| PUT | `/` | 必须 | 更新画像（任意维度） |

### 院校 (prefix: `/api/universities`)

| 方法 | 路径 | 鉴权 | 说明 |
|------|------|------|------|
| GET | `/` | 无 | 分页列表（省份/层次/类型/关键词筛选） |
| GET | `/{id}` | 无 | 单所院校详情 |

### 推荐 (prefix: `/api/recommend`)

| 方法 | 路径 | 鉴权 | 说明 |
|------|------|------|------|
| POST | `/` | 必须 | 生成冲稳保推荐 |
| GET | `/export` | 必须 | 导出推荐结果为 Excel |

### AI 对话 (prefix: `/api/chat`)

| 方法 | 路径 | 鉴权 | 说明 |
|------|------|------|------|
| GET | `/skills` | 无 | 获取可用角色列表 |
| GET | `/sessions` | 必须 | 获取会话列表 |
| PUT | `/sessions/{id}` | 必须 | 重命名会话 |
| GET | `/sessions/{id}/messages` | 必须 | 获取会话消息 |
| POST | `/` | 必须 | 普通对话 |
| POST | `/stream` | 必须 | SSE 流式对话 |

### 支付 (prefix: `/api/payment`)

| 方法 | 路径 | 鉴权 | 说明 |
|------|------|------|------|
| GET | `/tiers` | 可选 | 获取会员等级定价 |
| GET | `/membership` | 必须 | 获取当前会员状态 |
| POST | `/orders` | 必须 | 创建支付订单 |
| POST | `/simulate` | 必须 | 模拟支付成功（开发用） |
| GET | `/orders` | 必须 | 获取订单历史 |

---

## 9. 风险分析

| 风险 | 等级 | 应对策略 |
|------|------|---------|
| 数据准确性 | 高 | 多源交叉验证 + 人工审核，所有结果标注"仅供参考" |
| LLM 幻觉 | 高 | LLM 不做核心计算，强制工具调用获取数据，Prompt 约束 + 输出审核 |
| 高考季高并发 | 高 | 核心查询全缓存，弹性扩容 + 限流降级，LLM 请求排队 |
| 政策变化 | 中 | 按省份抽象规则引擎，31 省独立配置，预留扩展点 |
| 法律合规 | 中 | 数据最小化采集，免责声明 + 不承诺录取，符合《个人信息保护法》 |
| 竞品跟进 | 中 | 多角色 AI + 五维画像做深壁垒，积累用户数据飞轮 |

---

## 10. 已实现 vs 规划

### 已实现 (MVP)

- [x] 用户注册/登录/改密/退出
- [x] 五维画像采集与回显
- [x] 推荐引擎（位次换算 + 冲稳保分类 + 六维适配度评分）
- [x] LLM 语义扩展（厌恶/兴趣关键词）
- [x] AI 志愿顾问（SSE 流式 + 6 工具调用 + 多轮对话 + Markdown 渲染）
- [x] 多角色技能（智愿顾问 + 张雪峰视角）
- [x] 会话管理（新建/切换/重命名/删除）
- [x] 院校查询（分页 + 筛选 + 展开详情）
- [x] 推荐结果 Excel 导出
- [x] 四级会员体系 + 模拟支付
- [x] 个人中心（个人详情/账号安全/会员中心）

### 规划中

- [ ] 真实支付对接（支付宝/微信支付 SDK）
- [ ] 深度分析报告 PDF 生成
- [ ] 职业路径规划
- [ ] 志愿表模拟与对比
- [ ] 内置简化版霍兰德/MBTI 测评
- [ ] SEO 长尾内容页
- [ ] 小程序/App 扩展
- [ ] 推荐算法精度回测（基于真实录取结果）
- [ ] Redis 缓存层
- [ ] Elasticsearch 全文搜索
