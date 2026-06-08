# 智愿 - AI高考志愿助手

基于大语言模型的高考志愿智能推荐系统，为考生和家长提供科学、个性化的志愿填报指导。

## 产品简介

智愿是一款面向高考考生和家长的AI志愿助手，通过**结构化数据引擎 + LLM智能解读**的方式，帮助用户：

- **精准定位**：基于历年录取数据和位次换算，推荐"冲/稳/保"院校组合
- **六维画像**：综合考虑基础信息、家庭背景、城市偏好、性格特质、能力优势、价值观六个维度
- **AI顾问**：提供24小时在线的智能对话，解答志愿填报相关问题
- **数据驱动**：所有推荐基于真实录取数据，AI仅负责解读和建议

### 核心功能

| 功能模块 | 说明 |
|---------|------|
| 智能推荐 | 输入分数和位次，生成冲/稳/保三档院校推荐 |
| 院校查询 | 按省份、层次、类型等条件筛选院校 |
| 六维画像 | 渐进式完善个人信息，提升推荐精准度 |
| AI对话 | 与AI顾问流式打字机对话，支持工具调用查询真实数据，支持会话重命名 |
| 志愿导出 | 将推荐方案导出为格式化的 Excel 表格 |
| 专业库 | 浏览专业信息、课程设置、就业方向 |

### 特色功能：考试科类

系统支持三种考试科类，智能推荐会根据用户的考试科类筛选对应专业：

| 考试科类 | 说明 |
|---------|------|
| 普通类 | 标准高考科目（物理类/历史类/综合改革） |
| 艺术类 | 艺术类专业考试（文化课+专业课） |
| 体育类 | 体育类专业考试（文化课+体育测试） |

## 技术架构

### 整体架构

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (Next.js 16)                │
│  React 19 + TypeScript + Ant Design 6                  │
│  Pages: Home / Recommend / Universities / Chat / Profile│
└────────────────────────┬────────────────────────────────┘
                         │
                         │ HTTP/REST + SSE (流式对话)
                         │
┌────────────────────────┴────────────────────────────────┐
│                    Backend (FastAPI 0.111)               │
│                                                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │  Auth API    │  │ Recommend API│  │   Chat API   │ │
│  │  (JWT)       │  │              │  │ (SSE Stream) │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
│                                                        │
│  ┌──────────────────────────────────────────────────┐ │
│  │              Services Layer (业务逻辑)            │ │
│  │  AuthService / ProfileService / ChatService      │ │
│  │  RecommendService / UniversityService            │ │
│  │  UserService / MajorService / AdmissionService   │ │
│  │  LLMService (Tool Calling + 流式输出 + 语义扩展)    │ │
│  │  RecommendationEngine / AdapterScorer (六维评分)    │ │
│  │  ExportService (Excel 志愿表导出)                   │ │
│  └──────────────────────┬───────────────────────────┘ │
│                         │                             │
│  ┌──────────────────────┴───────────────────────────┐ │
│  │              DAO Layer (数据访问)                 │ │
│  │  UserDAO / ProfileDAO / MessageDAO               │ │
│  │  UniversityDAO / MajorDAO / AdmissionDAO         │ │
│  │  RecommendDAO                                    │ │
│  │  每个 DAO 方法自管理 async_session + commit       │ │
│  └──────────────────────────────────────────────────┘ │
└────────────────────────┬────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
    ┌────┴────┐    ┌────┴────┐    ┌────┴────┐
    │PostgreSQL│    │  Redis  │    │  LLMs   │
    │  (数据)  │    │ (缓存)  │    │DeepSeek │
    └─────────┘    └─────────┘    │Qwen     │
                                  └─────────┘
```

### 技术栈

**后端**
- **框架**: FastAPI 0.111.0 (Python 3.11+)
- **数据库**: PostgreSQL 15 (异步驱动: asyncpg)
- **ORM**: SQLAlchemy 2.0.30 + Alembic (迁移)
- **缓存**: Redis 7
- **认证**: JWT (python-jose) + bcrypt
- **LLM**: DeepSeek API / 通义千问 API (OpenAI 兼容接口，支持 Tool Calling)
- **包管理**: uv (开发) / pip (Docker 构建)

**前端**
- **框架**: Next.js 16.2.6 (App Router)
- **React**: React 19.2.4
- **语言**: TypeScript
- **样式**: Tailwind CSS
- **组件库**: Ant Design 6
- **HTTP**: Axios

**部署**
- **容器化**: Docker + Docker Compose
- **服务编排**: PostgreSQL / Redis / Backend 一键启动

### 数据规模

| 数据类型 | 数量 | 说明 |
|---------|------|------|
| 院校 | 342 所 | 覆盖 985/211/双一流/普通本科 |
| 专业 | 126 个 | 涵盖 12 大学科门类 |
| 录取记录 | 379,550 条 | 31 省 × 6 年 × 多科类 |
| 一分一段 | 150,974 条 | 各省各年分数段分布 |

### 新高考改革覆盖

系统完整覆盖全国 31 个省份的新高考改革进程，自动识别各省份改革年份并切换科类：

| 改革批次 | 起始年份 | 省份 |
|---------|---------|------|
| 第 1 批 | 2017 | 浙江、上海 |
| 第 2 批 | 2020 | 北京、天津、山东、海南 |
| 第 3 批 | 2021 | 河北、辽宁、江苏、福建、湖北、湖南、广东、重庆 |
| 第 4 批 | 2024 | 吉林、黑龙江、安徽、江西、广西、贵州、甘肃 |
| 第 5 批 | 2025 | 山西、河南、陕西、内蒙古、四川、云南、宁夏、青海 |
| 尚未改革 | - | 西藏、新疆（仍用物理类+历史类） |

### 项目结构

```
zhi_yuan/
├── backend/                 # 后端服务
│   ├── app/
│   │   ├── api/            # API 路由层（仅参数解析，无 DB 操作）
│   │   │   ├── deps.py         # 依赖注入（JWT 鉴权）
│   │   │   ├── auth.py         # 认证接口
│   │   │   ├── profile.py      # 用户画像
│   │   │   ├── universities.py # 院校查询
│   │   │   ├── recommend.py    # 智能推荐
│   │   │   └── chat.py         # AI对话（SSE 流式）
│   │   ├── constants.py    # 常量定义（SubjectType, ExamType）
│   │   ├── dao/            # 数据访问层（每个方法自管理 session）
│   │   │   ├── user.py         # 用户账号
│   │   │   ├── profile.py      # 用户画像
│   │   │   ├── message.py      # 聊天消息
│   │   │   ├── university.py   # 院校
│   │   │   ├── major.py        # 专业
│   │   │   ├── admission.py    # 录取记录 + 一分一段
│   │   │   └── recommend.py    # 推荐记录
│   │   ├── models/         # 数据模型（SQLAlchemy ORM）
│   │   ├── schemas/        # Pydantic 请求/响应模型
│   │   ├── services/       # 业务逻辑层
│   │   │   ├── auth_service.py          # 注册/登录
│   │   │   ├── profile_service.py       # 画像管理
│   │   │   ├── chat_service.py          # 对话编排 + 限流
│   │   │   ├── llm_service.py           # LLM 调用 + Tool Calling + 语义扩展
│   │   │   ├── recommend_service.py     # 推荐流程
│   │   │   ├── university_service.py    # 院校查询
│   │   │   ├── major_service.py         # 专业查询
│   │   │   ├── admission_service.py     # 录取数据查询
│   │   │   ├── user_service.py          # 用户画像摘要
│   │   │   ├── export_service.py        # Excel 志愿表导出
│   │   │   ├── recommendation_engine.py # 冲/稳/保分类引擎 + 厌恶词过滤
│   │   │   ├── adapter_scorer.py        # 六维适配评分（含城市偏好）
│   │   │   └── rank_converter.py        # 位次换算
│   │   ├── config.py       # 配置管理
│   │   ├── database.py     # 数据库连接（engine + async_session）
│   │   └── main.py         # FastAPI 入口（含 /ppt 静态挂载）
│   ├── alembic/            # 数据库迁移
│   ├── tests/              # 单元测试
│   ├── pyproject.toml      # Python 依赖（uv）
│   └── requirements.txt    # Python 依赖（pip / Docker）
├── frontend/               # 前端应用
│   ├── src/
│   │   ├── app/           # Next.js 页面
│   │   ├── components/    # React 组件
│   │   ├── lib/           # 工具函数
│   │   └── types/         # TypeScript 类型
│   └── package.json
├── ppt/                    # 项目路演 PPT（静态 HTML）
│   └── index.html
├── scripts/                # 数据脚本
│   ├── seed_universities.py  # 院校种子数据
│   ├── seed_majors.py        # 专业种子数据
│   └── seed_admission.py     # 录取记录 + 一分一段数据
├── pyproject.toml          # 项目级依赖配置
└── docker-compose.yml      # 容器编排
```

## 快速开始

### 前置要求

- Docker & Docker Compose
- Node.js 18+ (前端开发)
- Python 3.11+ (本地开发，可选)
- [uv](https://docs.astral.sh/uv/) (Python 包管理，本地开发推荐)

### 方式一：Docker Compose 一键启动（推荐）

```bash
# 1. 克隆项目
git clone <repository-url>
cd zhi_yuan

# 2. 配置环境变量
cp backend/.env.example backend/.env
# 编辑 backend/.env，填入 LLM API Key：
#   DEEPSEEK_API_KEY=your-deepseek-key
#   QWEN_API_KEY=your-qwen-key

# 3. 启动所有服务
docker compose up -d

# 4. 执行数据库迁移
docker compose exec backend alembic upgrade head

# 5. 导入种子数据
docker compose exec backend python scripts/seed_universities.py
docker compose exec backend python scripts/seed_majors.py
docker compose exec backend python scripts/seed_admission.py

# 6. 验证服务
curl http://localhost:8000/health
# 应返回: {"status":"ok","service":"智愿"}

# 7. 启动前端（开发模式）
cd frontend
npm install
npm run dev
```

访问：
- **前端**: http://localhost:3000
- **后端API文档**: http://localhost:8000/docs
- **项目路演 PPT**: http://localhost:8000/ppt/
- **数据库**: localhost:5432 (用户: zhiyuan, 密码: zhiyuan_dev_2026)

### 方式二：本地开发环境

#### 后端

```bash
# 1. 安装 uv（如尚未安装）
# macOS / Linux:
curl -LsSf https://astral.sh/uv/install.sh | sh
# 或通过 Homebrew:
brew install uv

# 2. 同步虚拟环境并安装所有依赖（基于 pyproject.toml）
uv sync

# 3. 激活虚拟环境
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# 4. 配置环境变量
cp backend/.env.example backend/.env
# 编辑 backend/.env，注意：
#   本地开发时 DATABASE_URL 和 REDIS_URL 的主机名用 localhost（不是 postgres/redis）
#   示例：DATABASE_URL=postgresql+asyncpg://zhiyuan:zhiyuan_dev_2026@localhost:5432/zhiyuan
#   示例：REDIS_URL=redis://localhost:6379/0

# 5. 安装并启动 PostgreSQL 和 Redis
# macOS (Homebrew):
brew install postgresql@15 redis
brew services start postgresql@15
brew services start redis

# 6. 创建数据库和用户
createdb zhiyuan
psql zhiyuan -c "CREATE USER zhiyuan WITH PASSWORD 'zhiyuan_dev_2026';"
psql zhiyuan -c "GRANT ALL PRIVILEGES ON DATABASE zhiyuan TO zhiyuan;"
psql zhiyuan -c "GRANT ALL ON SCHEMA public TO zhiyuan;"

# 7. 执行数据库迁移（根据模型自动建表）
cd backend
uv run alembic upgrade head

# 8. 导入种子数据
cd ..
PYTHONPATH=backend uv run --directory backend python ../scripts/seed_universities.py
PYTHONPATH=backend uv run --directory backend python ../scripts/seed_majors.py
PYTHONPATH=backend uv run --directory backend python ../scripts/seed_admission.py

# 9. 启动服务
cd backend
uv run uvicorn app.main:app --reload --port 8000
```

#### 前端

```bash
cd frontend

# 1. 安装依赖
npm install

# 2. 配置环境变量
cat > .env.local << EOF
NEXT_PUBLIC_API_URL=http://localhost:8000
EOF

# 3. 启动开发服务器
npm run dev
```

## 部署指南

### 生产环境部署

#### 1. 环境准备

```bash
# 服务器要求
- Ubuntu 20.04+ / CentOS 8+
- 4GB+ RAM
- 50GB+ SSD
- Docker & Docker Compose

# 安装 Docker
curl -fsSL https://get.docker.com | sh
sudo systemctl enable docker
sudo systemctl start docker

# 安装 Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### 2. 配置生产环境变量

```bash
# 后端配置
cp backend/.env.example backend/.env
# 必须修改以下配置：
#   DATABASE_URL=postgresql+asyncpg://user:pass@postgres:5432/zhiyuan
#   SECRET_KEY=<生成强随机密钥>
#   DEEPSEEK_API_KEY=<生产环境API Key>
#   DEBUG=False

# 生成密钥
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

#### 3. 构建与启动

```bash
# 构建镜像
docker compose build

# 启动服务（后台运行）
docker compose up -d

# 查看日志
docker compose logs -f backend

# 初始化数据库
docker compose exec backend alembic upgrade head
docker compose exec backend python scripts/seed_universities.py
docker compose exec backend python scripts/seed_majors.py
docker compose exec backend python scripts/seed_admission.py
```

#### 4. Nginx 反向代理

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $http_host;

        # SSE 流式对话支持
        proxy_buffering off;
        proxy_cache off;
        proxy_read_timeout 300s;
        chunked_transfer_encoding on;
    }

    location /ppt {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
    }
}
```

#### 5. 前端生产构建

```bash
cd frontend
npm install
npm run build
npm start  # 或使用 PM2: pm2 start npm -- start
```

### 数据管理

```bash
# 备份数据库
docker compose exec postgres pg_dump -U zhiyuan zhiyuan > backup_$(date +%Y%m%d).sql

# 恢复数据库
docker compose exec -T postgres psql -U zhiyuan zhiyuan < backup_20260528.sql

# 查看数据库统计
docker compose exec postgres psql -U zhiyuan -d zhiyuan -c "
  SELECT
    (SELECT count(*) FROM universities) as universities,
    (SELECT count(*) FROM majors) as majors,
    (SELECT count(*) FROM users) as users;
"
```

### 监控与日志

```bash
# 查看所有服务状态
docker compose ps

# 查看后端日志
docker compose logs -f backend

# 查看数据库连接
docker compose exec postgres psql -U zhiyuan -d zhiyuan -c "SELECT count(*) FROM pg_stat_activity;"

# 查看Redis内存
docker compose exec redis redis-cli info memory
```

## API 文档

启动后端后访问 `http://localhost:8000/docs` 查看交互式 API 文档。

启动后端后访问 `http://localhost:8000/ppt/` 查看项目路演 PPT。

### 主要接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/auth/register` | POST | 用户注册 |
| `/api/auth/login` | POST | 用户登录 |
| `/api/profile` | GET/PUT | 用户画像管理 |
| `/api/universities` | GET | 院校列表查询（支持分页/筛选） |
| `/api/recommend` | POST | 获取智能推荐（冲/稳/保） |
| `/api/recommend/export` | GET | 导出志愿表（Excel） |
| `/api/chat` | POST | AI 对话（SSE 流式输出，打字机效果） |
| `/api/chat/sessions` | GET | 获取会话列表 |
| `/api/chat/sessions/{id}` | PUT | 重命名会话标题 |
| `/api/chat/sessions/{id}/messages` | GET | 获取会话消息 |
| `/health` | GET | 健康检查 |
| `/ppt/` | GET | 项目路演 PPT（静态页面） |

### 示例：获取推荐

```bash
# 1. 注册/登录获取 token
TOKEN=$(curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"phone":"13800138000","password":"test123"}' \
  | jq -r '.access_token')

# 2. 获取推荐（普通类）
curl -X POST http://localhost:8000/api/recommend \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "score": 620,
    "rank": 5000,
    "province": "浙江",
    "subject_type": "综合改革",
    "exam_type": "普通类"
  }'

# 3. 获取推荐（艺术类）
curl -X POST http://localhost:8000/api/recommend \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "score": 520,
    "rank": 8000,
    "province": "浙江",
    "subject_type": "综合改革",
    "exam_type": "艺术类"
  }'
```

### 示例：AI 对话（流式）

```bash
# SSE 流式对话，逐字输出
curl -N -X POST "http://localhost:8000/api/chat?message=浙大多少分能上" \
  -H "Authorization: Bearer $TOKEN"

# 返回格式（Server-Sent Events）:
# event: start
# data: {"session_id": "xxx-xxx"}
#
# event: delta
# data: 根
#
# event: delta
# data: 据
#
# event: done
# data: {"session_id": "xxx-xxx"}
```

前端对接（fetch + ReadableStream）：

```javascript
const res = await fetch("/api/chat?message=你好", {
  method: "POST",
  headers: { "Authorization": `Bearer ${token}` }
});
const reader = res.body.getReader();
const decoder = new TextDecoder();

while (true) {
  const { done, value } = await reader.read();
  if (done) break;
  const text = decoder.decode(value);
  // 解析 SSE event: delta / data: xxx
  const matches = text.matchAll(/event: delta\ndata: (.+)\n\n/g);
  for (const m of matches) {
    container.textContent += m[1];  // 逐字追加
  }
}
```

### LLM Tool Calling 工具

AI 对话支持 6 个工具，LLM 会根据用户问题自动调用：

| 工具 | 用途 | 示例问题 |
|------|------|---------|
| `query_university` | 院校基本信息 | "浙大是什么层次？" |
| `query_major` | 专业详情 | "计算机专业学什么？" |
| `query_admission_score` | 历年录取分数/位次 | "浙大在浙江多少分能上？" |
| `query_score_segment` | 一分一段表 | "620分对应什么位次？" |
| `get_user_profile` | 用户五维画像 | "根据我的情况分析..." |
| `get_user_recommendation` | 用户推荐结果 | "帮我解读推荐方案" |

## 测试

```bash
# 运行所有测试
cd backend
uv run pytest

# 运行特定测试
uv run pytest tests/test_rank_converter.py -v
uv run pytest tests/test_recommendation.py -v
uv run pytest tests/test_adapter_scorer.py -v

# 测试覆盖率
uv run pytest --cov=app --cov-report=html
```

## 数据库模型管理

项目使用 **SQLAlchemy 2.0** 定义模型，**Alembic** 管理数据库迁移。模型文件位于 `backend/app/models/`。

### 初始化建表（首次部署）

```bash
cd backend

# 根据所有模型自动生成初始迁移脚本
uv run alembic revision --autogenerate -m "init: create all tables"

# 执行迁移，创建所有表
uv run alembic upgrade head

# 验证建表结果
psql zhiyuan -c "\dt"
```

### 修改模型（增删字段/表）

```bash
cd backend

# 1. 修改 app/models/*.py 中的模型定义

# 2. 自动生成增量迁移脚本
uv run alembic revision --autogenerate -m "描述本次变更"

# 3. 检查生成的迁移脚本（alembic/versions/xxx.py），确认无误后执行
uv run alembic upgrade head
```

### 常用迁移操作

```bash
cd backend

# 查看当前数据库迁移版本
uv run alembic current

# 查看迁移历史
uv run alembic history --verbose

# 回滚到上一个版本
uv run alembic downgrade -1

# 回滚到指定版本
uv run alembic downgrade <revision_id>

# 回滚所有迁移（清空所有表结构）
uv run alembic downgrade base
```

### 模型文件说明

| 文件 | 模型 | 对应表 | 说明 |
|------|------|--------|------|
| `user.py` | User | users | 用户账号（手机号、密码、会员等级） |
| `user.py` | UserProfile | user_profiles | 五维画像（JSONB 存储） |
| `university.py` | University | universities | 院校信息 |
| `major.py` | Major | majors | 专业信息 |
| `major.py` | UniversityMajor | university_majors | 院校-专业关联 |
| `admission.py` | AdmissionRecord | admission_records | 历年录取数据 |
| `admission.py` | ScoreSegment | score_segments | 一分一段表 |
| `recommendation.py` | Recommendation | recommendations | 推荐记录 |
| `recommendation.py` | ChatMessage | chat_messages | AI 对话消息 |
| `chat_session.py` | ChatSession | chat_sessions | 会话元数据（自定义标题） |

> **注意**：新增模型后需在 `app/models/__init__.py` 中导入，否则 Alembic 无法检测到新表。

## 后端架构说明

项目采用 **API → Service → DAO → Model** 四层架构：

```
请求 → API（参数解析 + 鉴权）→ Service（业务编排）→ DAO（数据访问）→ Model（ORM）
```

| 层 | 职责 | 规则 |
|---|------|------|
| **API** | 路由分发、参数校验、依赖注入 | 不含任何 DB 操作，不含 `self.db` |
| **Service** | 业务逻辑编排、限流、上下文采集 | 不含 DB 操作，通过 DAO 访问数据 |
| **DAO** | 数据访问、session 管理 | 每个方法 `async with async_session()` 自管理事务 |
| **Model** | ORM 定义 | 纯数据结构 |

### 当前已知限制

DAO 层每个方法独立管理 session，跨 DAO 的操作（如 `AuthService.register` 中创建用户 + 创建画像）**不支持事务回滚**。如需生产级事务保障，可改为 Service 层管理 session、DAO 接受 session 参数。

## 常见问题

**Q: 数据库连接失败？**  
A: 确保 PostgreSQL 已启动，且 `.env` 中的 `DATABASE_URL` 配置正确。Docker 环境使用 `postgres` 作为主机名。

**Q: LLM API 调用失败？**  
A: 检查 `DEEPSEEK_API_KEY` 或 `QWEN_API_KEY` 是否正确配置，并确保服务器可以访问外部 API。

**Q: 前端无法连接后端？**  
A: 检查 `frontend/.env.local` 中的 `NEXT_PUBLIC_API_URL` 是否正确，默认为 `http://localhost:8000`。

**Q: 如何添加更多院校/专业数据？**  
A: 编辑 `scripts/seed_universities.py` 和 `scripts/seed_majors.py`，然后重新运行脚本。

**Q: 注册时报 `ValueError: password cannot be longer than 72 bytes`？**  
A: 这是 `passlib` 与 `bcrypt>=4.1` 不兼容导致的。本项目已移除 `passlib`，直接使用 `bcrypt` 库。如仍遇此问题，确认 `pyproject.toml` 中依赖为 `bcrypt>=4.0` 而非 `passlib[bcrypt]`。

**Q: AI 对话没有返回内容？**  
A: LLM 启用 Tool Calling 后，首次返回的 `message.content` 为 `None`（工具调用请求）。`LLMService` 已实现完整的 tool calling 循环，确保依赖版本 `openai>=1.0`。

**Q: 智能推荐返回空结果？**  
A: 检查以下几点：
1. 确保已导入录取数据：`python scripts/seed_admission.py`
2. 检查请求参数中的 `exam_type` 是否正确（普通类/艺术类/体育类）
3. 艺术类和体育类专业数量较少，系统会自动从相关专业池中选取
4. 查看后端日志确认查询条件

## 开发计划

- [x] 五维画像 + 智能推荐 + AI 对话（Tool Calling + SSE 流式）
- [x] 三层架构重构（API / Service / DAO）
- [x] Alembic 数据库迁移
- [x] 项目路演 PPT
- [x] 考试科类支持（普通类/艺术类/体育类）
- [x] 新高考改革省份全覆盖（31 省）
- [x] 大规模录取数据生成（379,550 条）
- [x] 院校列表分页与排序
- [x] 六维适配评分（新增城市偏好权重）
- [x] LLM 语义扩展（厌恶领域过滤，避免字面匹配遗漏）
- [x] 志愿表 Excel 导出（冲/稳/保格式化表格）
- [x] AI 对话会话重命名
- [ ] 数据爬取模块（阳光高考网、各省考试院）
- [ ] 深度报告生成（PDF 导出）
- [ ] 会员系统与支付集成
- [ ] DAO 层事务支持（Service 管理 session）
- [ ] 移动端适配（PWA / 小程序）
- [ ] 性能优化（Redis 缓存、CDN）
- [ ] SEO 优化

## 许可证

MIT License

## 联系方式

如有问题或建议，请提交 Issue 或联系开发团队。

### 智愿项目开放群

欢迎加入飞书群聊，交流项目使用与志愿问题：

🔗 https://applink.feishu.cn/client/chat/chatter/add_by_link?link_token=cb3j66ba-492e-47b2-bc13-39939abfe3f7
