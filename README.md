# 智愿 - AI高考志愿助手

基于大语言模型的高考志愿智能推荐系统，为考生和家长提供科学、个性化的志愿填报指导。

## 产品简介

智愿是一款面向高考考生和家长的AI志愿助手，通过**结构化数据引擎 + LLM智能解读**的方式，帮助用户：

- **精准定位**：基于历年录取数据和位次换算，推荐"冲/稳/保"院校组合
- **五维画像**：综合考虑基础信息、家庭背景、性格特质、能力优势、价值观五个维度
- **AI顾问**：提供24小时在线的智能对话，解答志愿填报相关问题
- **数据驱动**：所有推荐基于真实录取数据，AI仅负责解读和建议

### 核心功能

| 功能模块 | 说明 |
|---------|------|
| 智能推荐 | 输入分数和位次，生成冲/稳/保三档院校推荐 |
| 院校查询 | 按省份、层次、类型等条件筛选院校 |
| 五维画像 | 渐进式完善个人信息，提升推荐精准度 |
| AI对话 | 与AI顾问实时对话，获取个性化建议 |
| 专业库 | 浏览专业信息、课程设置、就业方向 |

## 技术架构

### 整体架构

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (Next.js 14)                │
│  TypeScript + Tailwind CSS + Ant Design                │
│  Pages: Home / Recommend / Universities / Chat / Profile│
└────────────────────────┬────────────────────────────────┘
                         │
                         │ HTTP/REST API
                         │
┌────────────────────────┴────────────────────────────────┐
│                    Backend (FastAPI)                    │
│                                                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │  Auth API    │  │ Recommend API│  │   Chat API   │ │
│  │  (JWT)       │  │              │  │  (Streaming) │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
│                                                        │
│  ┌──────────────────────────────────────────────────┐ │
│  │              Services Layer                      │ │
│  │  - RankConverter (位次换算)                       │ │
│  │  - RecommendationEngine (推荐引擎)                │ │
│  │  - AdapterScorer (五维适配评分)                   │ │
│  │  - LLMService (大模型服务)                        │ │
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
- **框架**: FastAPI (Python 3.11+)
- **数据库**: PostgreSQL 15 (异步驱动: asyncpg)
- **ORM**: SQLAlchemy 2.0 + Alembic (迁移)
- **缓存**: Redis 7
- **认证**: JWT (python-jose)
- **LLM**: DeepSeek API / 通义千问 API (OpenAI 兼容接口)

**前端**
- **框架**: Next.js 14 (App Router)
- **语言**: TypeScript
- **样式**: Tailwind CSS
- **组件库**: Ant Design
- **HTTP**: Axios

**部署**
- **容器化**: Docker + Docker Compose
- **服务编排**: PostgreSQL / Redis / Backend 一键启动

### 项目结构

```
zhi_yuan/
├── backend/                 # 后端服务
│   ├── app/
│   │   ├── api/            # API 路由层
│   │   │   ├── auth.py         # 认证接口
│   │   │   ├── profile.py      # 用户画像
│   │   │   ├── universities.py # 院校查询
│   │   │   ├── recommend.py    # 智能推荐
│   │   │   └── chat.py         # AI对话
│   │   ├── models/         # 数据模型
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── services/       # 业务逻辑层
│   │   │   ├── rank_converter.py        # 位次换算
│   │   │   ├── recommendation_engine.py # 推荐引擎
│   │   │   ├── adapter_scorer.py        # 适配评分
│   │   │   └── llm_service.py           # LLM服务
│   │   ├── config.py       # 配置管理
│   │   ├── database.py     # 数据库连接
│   │   └── main.py         # FastAPI入口
│   ├── alembic/            # 数据库迁移
│   ├── tests/              # 单元测试
│   └── requirements.txt    # Python依赖（pip）
├── pyproject.toml          # Python依赖（uv）
├── frontend/               # 前端应用
│   ├── src/
│   │   ├── app/           # Next.js页面
│   │   ├── components/    # React组件
│   │   ├── lib/           # 工具函数
│   │   └── types/         # TypeScript类型
│   └── package.json
├── scripts/               # 数据脚本
│   ├── seed_universities.py  # 院校种子数据
│   └── seed_majors.py        # 专业种子数据
└── docker-compose.yml     # 容器编排
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

启动后端后访问 http://localhost:8000/ppt/ 查看项目路演文档。
### 主要接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/auth/register` | POST | 用户注册 |
| `/api/auth/login` | POST | 用户登录 |
| `/api/profile` | GET/PUT | 用户画像管理 |
| `/api/universities` | GET | 院校列表查询 |
| `/api/recommend` | POST | 获取智能推荐 |
| `/api/chat` | POST | AI对话（普通） |
| `/api/chat/stream` | POST | AI对话（流式） |

### 示例：获取推荐

```bash
# 1. 注册/登录获取 token
TOKEN=$(curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"phone":"13800138000","password":"test123"}' \
  | jq -r '.access_token')

# 2. 获取推荐
curl -X POST http://localhost:8000/api/recommend \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "score": 620,
    "rank": 5000,
    "province": "浙江",
    "subject_type": "综合改革"
  }'
```

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

> **注意**：新增模型后需在 `app/models/__init__.py` 中导入，否则 Alembic 无法检测到新表。

## 常见问题

**Q: 数据库连接失败？**  
A: 确保 PostgreSQL 已启动，且 `.env` 中的 `DATABASE_URL` 配置正确。Docker 环境使用 `postgres` 作为主机名。

**Q: LLM API 调用失败？**  
A: 检查 `DEEPSEEK_API_KEY` 或 `QWEN_API_KEY` 是否正确配置，并确保服务器可以访问外部 API。

**Q: 前端无法连接后端？**  
A: 检查 `frontend/.env.local` 中的 `NEXT_PUBLIC_API_URL` 是否正确，默认为 `http://localhost:8000`。

**Q: 如何添加更多院校/专业数据？**  
A: 编辑 `scripts/seed_universities.py` 和 `scripts/seed_majors.py`，然后重新运行脚本。

## 开发计划

- [ ] 数据爬取模块（阳光高考网、各省考试院）
- [ ] 深度报告生成（PDF导出）
- [ ] 会员系统与支付集成
- [ ] 移动端适配（PWA / 小程序）
- [ ] 性能优化（缓存、CDN）
- [ ] SEO 优化

## 许可证

MIT License

## 联系方式

如有问题或建议，请提交 Issue 或联系开发团队。
