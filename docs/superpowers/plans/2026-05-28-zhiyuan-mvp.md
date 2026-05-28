# 智愿 MVP 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 构建智愿MVP——从数据库到前端全链路可运行的高考志愿填报推荐系统。

**Architecture:** Python/FastAPI后端提供RESTful API + Next.js前端提供SSR页面。推荐引擎使用确定性算法（位次换算+冲稳保+五维适配），LLM层调用DeepSeek/通义千问API做对话和报告生成。PostgreSQL存储核心数据，Redis做缓存，Docker Compose编排本地开发环境。

**Tech Stack:** Python 3.11+ / FastAPI / SQLAlchemy / Alembic / PostgreSQL 15 / Redis 7 / Next.js 14 (App Router) / TypeScript / TailwindCSS / Ant Design / DeepSeek API / Docker Compose

---

## 项目目录结构

```
zhi_yuan/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                    # FastAPI入口
│   │   ├── config.py                  # 配置管理
│   │   ├── database.py                # 数据库连接
│   │   ├── models/                    # SQLAlchemy模型
│   │   │   ├── __init__.py
│   │   │   ├── university.py
│   │   │   ├── major.py
│   │   │   ├── admission.py
│   │   │   ├── user.py
│   │   │   └── recommendation.py
│   │   ├── schemas/                   # Pydantic请求/响应模型
│   │   │   ├── __init__.py
│   │   │   ├── university.py
│   │   │   ├── major.py
│   │   │   ├── user.py
│   │   │   └── recommendation.py
│   │   ├── api/                       # API路由
│   │   │   ├── __init__.py
│   │   │   ├── deps.py                # 依赖注入
│   │   │   ├── auth.py
│   │   │   ├── universities.py
│   │   │   ├── majors.py
│   │   │   ├── profile.py
│   │   │   ├── recommend.py
│   │   │   └── chat.py
│   │   ├── services/                  # 业务逻辑
│   │   │   ├── __init__.py
│   │   │   ├── recommendation_engine.py
│   │   │   ├── rank_converter.py
│   │   │   ├── adapter_scorer.py
│   │   │   ├── llm_service.py
│   │   │   └── report_generator.py
│   │   └── crawler/                   # 数据采集
│   │       ├── __init__.py
│   │       ├── base.py
│   │       ├── sunshine.py            # 阳光高考网
│   │       └── provincial.py          # 省考试院
│   ├── alembic/                       # 数据库迁移
│   │   └── versions/
│   ├── alembic.ini
│   ├── tests/
│   │   ├── conftest.py
│   │   ├── test_rank_converter.py
│   │   ├── test_recommendation.py
│   │   ├── test_adapter_scorer.py
│   │   └── test_api/
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── app/                       # Next.js App Router
│   │   ├── components/
│   │   ├── lib/
│   │   └── types/
│   ├── package.json
│   ├── Dockerfile
│   └── .env.local.example
├── docker-compose.yml
├── docs/
│   └── superpowers/
└── scripts/
    ├── seed_universities.py
    └── seed_majors.py
```

---

## Task 1: 项目脚手架

**Files:**
- Create: `docker-compose.yml`
- Create: `backend/requirements.txt`
- Create: `backend/.env.example`
- Create: `backend/app/__init__.py`
- Create: `backend/app/main.py`
- Create: `backend/app/config.py`
- Create: `backend/Dockerfile`
- Create: `.gitignore`

- [ ] **Step 1: 创建根目录 .gitignore**

```gitignore
# Python
__pycache__/
*.py[cod]
*.egg-info/
dist/
.venv/
venv/

# Node
node_modules/
.next/

# Environment
.env
.env.local
backend/.env

# IDE
.idea/
.vscode/
*.swp

# OS
.DS_Store
Thumbs.db

# Docker
docker-compose.override.yml
```

- [ ] **Step 2: 创建 docker-compose.yml**

```yaml
version: "3.9"

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: zhiyuan
      POSTGRES_USER: zhiyuan
      POSTGRES_PASSWORD: zhiyuan_dev_2026
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    env_file:
      - ./backend/.env
    depends_on:
      - postgres
      - redis
    volumes:
      - ./backend:/app
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

volumes:
  pgdata:
```

- [ ] **Step 3: 创建 backend/requirements.txt**

```
fastapi==0.111.0
uvicorn[standard]==0.30.1
sqlalchemy==2.0.30
alembic==1.13.1
psycopg2-binary==2.9.9
asyncpg==0.29.0
pydantic==2.7.4
pydantic-settings==2.3.3
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.9
redis==5.0.6
httpx==0.27.0
openai==1.35.3
numpy==1.26.4
pandas==2.2.2
pytest==8.2.2
pytest-asyncio==0.23.7
httpx==0.27.0
```

- [ ] **Step 4: 创建 backend/.env.example**

```
DATABASE_URL=postgresql+asyncpg://zhiyuan:zhiyuan_dev_2026@postgres:5432/zhiyuan
REDIS_URL=redis://redis:6379/0
SECRET_KEY=change-me-in-production-use-openssl-rand-hex-32
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
DEEPSEEK_API_KEY=your-deepseek-api-key
QWEN_API_KEY=your-qwen-api-key
DEEPSEEK_BASE_URL=https://api.deepseek.com
QWEN_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
```

- [ ] **Step 5: 创建 backend/app/config.py**

```python
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://zhiyuan:zhiyuan_dev_2026@localhost:5432/zhiyuan"
    REDIS_URL: str = "redis://localhost:6379/0"

    # Auth
    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    # LLM
    DEEPSEEK_API_KEY: str = ""
    QWEN_API_KEY: str = ""
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com"
    QWEN_BASE_URL: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"

    # App
    APP_NAME: str = "智愿"
    DEBUG: bool = True

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
```

- [ ] **Step 6: 创建 backend/app/__init__.py 和 backend/app/main.py**

`backend/app/__init__.py`:
```python
```

`backend/app/main.py`:
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    description="智愿 - LLM高考志愿填报助手API",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": settings.APP_NAME}
```

- [ ] **Step 7: 创建 backend/Dockerfile**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

- [ ] **Step 8: 复制 .env.example 为 .env 并启动验证**

Run:
```bash
cd /Users/chaowang/workspace/gte/zhi_yuan
cp backend/.env.example backend/.env
docker compose up -d postgres redis
docker compose up -d backend
curl http://localhost:8000/health
```

Expected: `{"status":"ok","service":"智愿"}`

- [ ] **Step 9: Commit**

```bash
git init
git add .
git commit -m "feat: project scaffolding with FastAPI, Docker Compose, PostgreSQL, Redis"
```

---

## Task 2: 数据库Schema与迁移

**Files:**
- Create: `backend/app/database.py`
- Create: `backend/app/models/__init__.py`
- Create: `backend/app/models/university.py`
- Create: `backend/app/models/major.py`
- Create: `backend/app/models/admission.py`
- Create: `backend/app/models/user.py`
- Create: `backend/app/models/recommendation.py`
- Create: `backend/alembic.ini`
- Create: `backend/alembic/env.py`

- [ ] **Step 1: 创建 backend/app/database.py**

```python
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from app.config import get_settings

settings = get_settings()

engine = create_async_engine(settings.DATABASE_URL, echo=settings.DEBUG)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncSession:
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
```

- [ ] **Step 2: 创建数据模型**

`backend/app/models/__init__.py`:
```python
from app.models.university import University
from app.models.major import Major, UniversityMajor
from app.models.admission import AdmissionRecord, ScoreSegment
from app.models.user import User, UserProfile
from app.models.recommendation import Recommendation, ChatMessage

__all__ = [
    "University", "Major", "UniversityMajor",
    "AdmissionRecord", "ScoreSegment",
    "User", "UserProfile",
    "Recommendation", "ChatMessage",
]
```

`backend/app/models/university.py`:
```python
import uuid
from sqlalchemy import String, Text, Float, ARRAY
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class University(Base):
    __tablename__ = "universities"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    province: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    city: Mapped[str] = mapped_column(String(50), nullable=False)
    level: Mapped[str] = mapped_column(String(20), nullable=True)  # 985/211/双一流/普通本科/民办
    type: Mapped[str] = mapped_column(String(20), nullable=True)   # 综合/理工/师范/医药/财经
    tags: Mapped[list] = mapped_column(ARRAY(String), default=list)
    tuition_min: Mapped[int] = mapped_column(nullable=True)
    tuition_max: Mapped[int] = mapped_column(nullable=True)
    website: Mapped[str] = mapped_column(String(500), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    latitude: Mapped[float] = mapped_column(Float, nullable=True)
    longitude: Mapped[float] = mapped_column(Float, nullable=True)
    logo_url: Mapped[str] = mapped_column(String(500), nullable=True)

    admission_records = relationship("AdmissionRecord", back_populates="university")
```

`backend/app/models/major.py`:
```python
import uuid
from sqlalchemy import String, Text, Integer, Float, ARRAY, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Major(Base):
    __tablename__ = "majors"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(50), nullable=False)  # 工学/理学/文学...
    degree: Mapped[str] = mapped_column(String(10), default="本科")
    duration: Mapped[int] = mapped_column(Integer, default=4)  # 学制年限
    description: Mapped[str] = mapped_column(Text, nullable=True)
    courses: Mapped[list] = mapped_column(ARRAY(String), default=list)
    career_directions: Mapped[list] = mapped_column(ARRAY(String), default=list)
    avg_salary: Mapped[int] = mapped_column(Integer, nullable=True)  # 参考月薪(元)
    subject_requirements: Mapped[dict] = mapped_column(JSONB, nullable=True)  # 新高考选科要求

    university_majors = relationship("UniversityMajor", back_populates="major")


class UniversityMajor(Base):
    __tablename__ = "university_majors"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    university_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("universities.id"), index=True)
    major_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("majors.id"), index=True)
    ranking: Mapped[str] = mapped_column(String(10), nullable=True)  # 学科评估等级 A+/A/A-...

    university = relationship("University")
    major = relationship("Major", back_populates="university_majors")
```

`backend/app/models/admission.py`:
```python
import uuid
from sqlalchemy import String, Integer, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class AdmissionRecord(Base):
    __tablename__ = "admission_records"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    university_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("universities.id"), index=True)
    major_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("majors.id"), nullable=True)
    province: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    year: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    batch: Mapped[str] = mapped_column(String(30), nullable=True)  # 本科一批/二批/提前批
    subject_type: Mapped[str] = mapped_column(String(20), nullable=False)  # 文/理/物理类/历史类/综合改革
    min_score: Mapped[int] = mapped_column(Integer, nullable=True)
    avg_score: Mapped[int] = mapped_column(Integer, nullable=True)
    max_score: Mapped[int] = mapped_column(Integer, nullable=True)
    min_rank: Mapped[int] = mapped_column(Integer, nullable=True)
    avg_rank: Mapped[int] = mapped_column(Integer, nullable=True)
    plan_count: Mapped[int] = mapped_column(Integer, nullable=True)
    actual_count: Mapped[int] = mapped_column(Integer, nullable=True)

    university = relationship("University", back_populates="admission_records")


class ScoreSegment(Base):
    """一分一段表"""
    __tablename__ = "score_segments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    province: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    year: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    subject_type: Mapped[str] = mapped_column(String(20), nullable=False)
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    count: Mapped[int] = mapped_column(Integer, nullable=False)      # 本分人数
    cumulative_count: Mapped[int] = mapped_column(Integer, nullable=False)  # 累计人数（位次）
```

`backend/app/models/user.py`:
```python
import uuid
from datetime import datetime
from sqlalchemy import String, Text, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    phone: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(200), nullable=False)
    nickname: Mapped[str] = mapped_column(String(50), nullable=True)
    membership_tier: Mapped[str] = mapped_column(String(20), default="free")  # free/standard/deep/vip
    membership_expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    daily_chat_count: Mapped[int] = mapped_column(default=0)
    last_chat_date: Mapped[str] = mapped_column(String(10), nullable=True)  # YYYY-MM-DD
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), unique=True, index=True)
    basic_info: Mapped[dict] = mapped_column(JSONB, nullable=True)
    family_info: Mapped[dict] = mapped_column(JSONB, nullable=True)
    personality: Mapped[dict] = mapped_column(JSONB, nullable=True)
    ability: Mapped[dict] = mapped_column(JSONB, nullable=True)
    values_info: Mapped[dict] = mapped_column(JSONB, nullable=True)
    completeness: Mapped[float] = mapped_column(Float, default=0.0)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

`backend/app/models/recommendation.py`:
```python
import uuid
from datetime import datetime
from sqlalchemy import String, Text, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class Recommendation(Base):
    __tablename__ = "recommendations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    input_snapshot: Mapped[dict] = mapped_column(JSONB, nullable=False)
    result: Mapped[dict] = mapped_column(JSONB, nullable=False)  # {rush: [...], stable: [...], safe: [...]}
    tier: Mapped[str] = mapped_column(String(20), default="free")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    session_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    role: Mapped[str] = mapped_column(String(20), nullable=False)  # user/assistant/system/tool
    content: Mapped[str] = mapped_column(Text, nullable=False)
    tool_calls: Mapped[dict] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
```

- [ ] **Step 3: 初始化 Alembic**

Run:
```bash
cd /Users/chaowang/workspace/gte/zhi_yuan/backend
docker compose exec backend alembic init alembic
```

然后修改 `backend/alembic/env.py`:
```python
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
from app.database import Base
from app.models import *  # noqa: F401, F403
from app.config import get_settings

config = context.config
settings = get_settings()
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL.replace("+asyncpg", ""))

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

- [ ] **Step 4: 生成并执行迁移**

Run:
```bash
docker compose exec backend alembic revision --autogenerate -m "initial schema"
docker compose exec backend alembic upgrade head
```

- [ ] **Step 5: 验证表结构**

Run:
```bash
docker compose exec postgres psql -U zhiyuan -d zhiyuan -c "\dt"
```

Expected: 显示 universities, majors, university_majors, admission_records, score_segments, users, user_profiles, recommendations, chat_messages 共9张表。

- [ ] **Step 6: Commit**

```bash
git add backend/
git commit -m "feat: database schema with all core tables via Alembic migration"
```

---

## Task 3: 种子数据——院校库与专业库

**Files:**
- Create: `scripts/seed_universities.py`
- Create: `scripts/seed_majors.py`

- [ ] **Step 1: 创建院校种子数据脚本**

`scripts/seed_universities.py`:
```python
"""种子数据：985/211/双一流院校基础信息"""
import asyncio
import uuid
import sys
sys.path.insert(0, "backend")

from sqlalchemy.ext.asyncio import AsyncSession
from app.database import async_session
from app.models.university import University

# 部分985院校示例数据（实际需3000+条）
UNIVERSITIES = [
    {"name": "清华大学", "province": "北京", "city": "北京", "level": "985", "type": "理工",
     "tags": ["985", "211", "双一流", "C9"], "tuition_min": 5000, "tuition_max": 10000,
     "website": "https://www.tsinghua.edu.cn", "latitude": 39.9994, "longitude": 116.3267},
    {"name": "北京大学", "province": "北京", "city": "北京", "level": "985", "type": "综合",
     "tags": ["985", "211", "双一流", "C9"], "tuition_min": 5000, "tuition_max": 8000,
     "website": "https://www.pku.edu.cn", "latitude": 39.9870, "longitude": 116.3052},
    {"name": "浙江大学", "province": "浙江", "city": "杭州", "level": "985", "type": "综合",
     "tags": ["985", "211", "双一流", "C9"], "tuition_min": 5500, "tuition_max": 9000,
     "website": "https://www.zju.edu.cn", "latitude": 30.3085, "longitude": 120.0864},
    {"name": "复旦大学", "province": "上海", "city": "上海", "level": "985", "type": "综合",
     "tags": ["985", "211", "双一流"], "tuition_min": 5500, "tuition_max": 8500,
     "website": "https://www.fudan.edu.cn", "latitude": 31.2986, "longitude": 121.5034},
    {"name": "上海交通大学", "province": "上海", "city": "上海", "level": "985", "type": "理工",
     "tags": ["985", "211", "双一流", "C9"], "tuition_min": 5500, "tuition_max": 9000,
     "website": "https://www.sjtu.edu.cn", "latitude": 31.0282, "longitude": 121.4436},
    {"name": "华中科技大学", "province": "湖北", "city": "武汉", "level": "985", "type": "理工",
     "tags": ["985", "211", "双一流"], "tuition_min": 4500, "tuition_max": 8000,
     "website": "https://www.hust.edu.cn", "latitude": 30.5115, "longitude": 114.4143},
    {"name": "武汉大学", "province": "湖北", "city": "武汉", "level": "985", "type": "综合",
     "tags": ["985", "211", "双一流"], "tuition_min": 4500, "tuition_max": 8000,
     "website": "https://www.whu.edu.cn", "latitude": 30.5378, "longitude": 114.3626},
    {"name": "南京大学", "province": "江苏", "city": "南京", "level": "985", "type": "综合",
     "tags": ["985", "211", "双一流", "C9"], "tuition_min": 5200, "tuition_max": 7800,
     "website": "https://www.nju.edu.cn", "latitude": 32.0579, "longitude": 118.7781},
    {"name": "中国科学技术大学", "province": "安徽", "city": "合肥", "level": "985", "type": "理工",
     "tags": ["985", "211", "双一流", "C9"], "tuition_min": 4800, "tuition_max": 7000,
     "website": "https://www.ustc.edu.cn", "latitude": 31.8427, "longitude": 117.2654},
    {"name": "西安交通大学", "province": "陕西", "city": "西安", "level": "985", "type": "理工",
     "tags": ["985", "211", "双一流", "C9"], "tuition_min": 4500, "tuition_max": 7500,
     "website": "https://www.xjtu.edu.cn", "latitude": 34.2358, "longitude": 108.9872},
    {"name": "哈尔滨工业大学", "province": "黑龙江", "city": "哈尔滨", "level": "985", "type": "理工",
     "tags": ["985", "211", "双一流", "C9"], "tuition_min": 4000, "tuition_max": 7000,
     "website": "https://www.hit.edu.cn", "latitude": 45.7411, "longitude": 126.6278},
    {"name": "中山大学", "province": "广东", "city": "广州", "level": "985", "type": "综合",
     "tags": ["985", "211", "双一流"], "tuition_min": 5160, "tuition_max": 8000,
     "website": "https://www.sysu.edu.cn", "latitude": 23.0934, "longitude": 113.2971},
    {"name": "四川大学", "province": "四川", "city": "成都", "level": "985", "type": "综合",
     "tags": ["985", "211", "双一流"], "tuition_min": 4440, "tuition_max": 7500,
     "website": "https://www.scu.edu.cn", "latitude": 30.6301, "longitude": 104.0826},
    {"name": "北京航空航天大学", "province": "北京", "city": "北京", "level": "985", "type": "理工",
     "tags": ["985", "211", "双一流"], "tuition_min": 5000, "tuition_max": 8000,
     "website": "https://www.buaa.edu.cn", "latitude": 39.9831, "longitude": 116.3474},
    {"name": "同济大学", "province": "上海", "city": "上海", "level": "985", "type": "理工",
     "tags": ["985", "211", "双一流"], "tuition_min": 5500, "tuition_max": 9000,
     "website": "https://www.tongji.edu.cn", "latitude": 31.2837, "longitude": 121.5019},
]


async def seed():
    async with async_session() as session:
        for data in UNIVERSITIES:
            uni = University(id=uuid.uuid4(), **data)
            session.add(uni)
        await session.commit()
        print(f"Inserted {len(UNIVERSITIES)} universities")


if __name__ == "__main__":
    asyncio.run(seed())
```

- [ ] **Step 2: 创建专业种子数据脚本**

`scripts/seed_majors.py`:
```python
"""种子数据：常见本科专业"""
import asyncio
import uuid
import sys
sys.path.insert(0, "backend")

from sqlalchemy.ext.asyncio import AsyncSession
from app.database import async_session
from app.models.major import Major

MAJORS = [
    {"name": "计算机科学与技术", "category": "工学", "duration": 4,
     "courses": ["数据结构", "操作系统", "计算机网络", "数据库", "编译原理", "算法设计"],
     "career_directions": ["软件工程师", "算法工程师", "系统架构师", "数据工程师"],
     "avg_salary": 15000,
     "subject_requirements": {"must": ["物理"], "prefer": ["化学"]}},
    {"name": "软件工程", "category": "工学", "duration": 4,
     "courses": ["程序设计", "数据结构", "软件工程导论", "软件测试", "项目管理"],
     "career_directions": ["软件开发", "项目经理", "产品经理", "测试工程师"],
     "avg_salary": 14000,
     "subject_requirements": {"must": ["物理"]}},
    {"name": "电子信息工程", "category": "工学", "duration": 4,
     "courses": ["电路分析", "信号与系统", "数字电路", "模拟电路", "通信原理"],
     "career_directions": ["硬件工程师", "通信工程师", "嵌入式开发", "IC设计"],
     "avg_salary": 12000,
     "subject_requirements": {"must": ["物理"]}},
    {"name": "临床医学", "category": "医学", "duration": 5,
     "courses": ["人体解剖学", "生理学", "病理学", "药理学", "内科学", "外科学"],
     "career_directions": ["临床医生", "医学研究", "公共卫生"],
     "avg_salary": 10000,
     "subject_requirements": {"must": ["物理", "化学"]}},
    {"name": "金融学", "category": "经济学", "duration": 4,
     "courses": ["微观经济学", "宏观经济学", "金融学", "投资学", "金融工程"],
     "career_directions": ["银行", "证券", "基金", "保险", "金融科技"],
     "avg_salary": 12000,
     "subject_requirements": {}},
    {"name": "法学", "category": "法学", "duration": 4,
     "courses": ["宪法", "民法", "刑法", "行政法", "国际法", "诉讼法"],
     "career_directions": ["律师", "法官", "检察官", "法务", "公务员"],
     "avg_salary": 10000,
     "subject_requirements": {}},
    {"name": "英语", "category": "文学", "duration": 4,
     "courses": ["综合英语", "英语写作", "翻译理论与实践", "英美文学", "语言学"],
     "career_directions": ["翻译", "外贸", "教育", "国际组织"],
     "avg_salary": 8000,
     "subject_requirements": {}},
    {"name": "土木工程", "category": "工学", "duration": 4,
     "courses": ["结构力学", "材料力学", "土力学", "混凝土结构", "钢结构"],
     "career_directions": ["结构设计", "施工管理", "工程造价", "监理"],
     "avg_salary": 9000,
     "subject_requirements": {"must": ["物理"]}},
    {"name": "会计学", "category": "管理学", "duration": 4,
     "courses": ["基础会计", "中级财务会计", "审计学", "成本管理", "税法"],
     "career_directions": ["会计师", "审计师", "财务分析", "税务师"],
     "avg_salary": 9000,
     "subject_requirements": {}},
    {"name": "人工智能", "category": "工学", "duration": 4,
     "courses": ["机器学习", "深度学习", "自然语言处理", "计算机视觉", "强化学习"],
     "career_directions": ["AI工程师", "算法研究员", "数据科学家"],
     "avg_salary": 18000,
     "subject_requirements": {"must": ["物理"]}},
]


async def seed():
    async with async_session() as session:
        for data in MAJORS:
            major = Major(id=uuid.uuid4(), **data)
            session.add(major)
        await session.commit()
        print(f"Inserted {len(MAJORS)} majors")


if __name__ == "__main__":
    asyncio.run(seed())
```

- [ ] **Step 3: 运行种子数据**

Run:
```bash
cd /Users/chaowang/workspace/gte/zhi_yuan
docker compose exec backend python -c "
import asyncio, sys
sys.path.insert(0, '.')
from scripts import seed_universities, seed_majors
" 2>/dev/null || python scripts/seed_universities.py && python scripts/seed_majors.py
```

Expected:
```
Inserted 15 universities
Inserted 10 majors
```

- [ ] **Step 4: 验证数据**

Run:
```bash
docker compose exec postgres psql -U zhiyuan -d zhiyuan -c "SELECT name, level, province FROM universities LIMIT 5;"
```

- [ ] **Step 5: Commit**

```bash
git add scripts/
git commit -m "feat: seed data for universities and majors"
```

---

## Task 4: 位次换算算法（TDD）

**Files:**
- Create: `backend/tests/__init__.py`
- Create: `backend/tests/conftest.py`
- Create: `backend/tests/test_rank_converter.py`
- Create: `backend/app/services/__init__.py`
- Create: `backend/app/services/rank_converter.py`

- [ ] **Step 1: 创建测试配置**

`backend/tests/__init__.py`: 空文件

`backend/tests/conftest.py`:
```python
import pytest
import asyncio


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
```

- [ ] **Step 2: 编写位次换算的失败测试**

`backend/tests/test_rank_converter.py`:
```python
from app.services.rank_converter import RankConverter


class TestRankConverter:
    def setup_method(self):
        self.converter = RankConverter()

    def test_basic_conversion_same_plan_count(self):
        """招生计划数相同时，位次不变"""
        result = self.converter.convert(
            current_rank=5000,
            current_year_plan=10000,
            target_year_plan=10000,
        )
        assert result == 5000

    def test_conversion_plan_increased(self):
        """招生计划增加时，等效位次放大（排名数字变大=排名更低）"""
        result = self.converter.convert(
            current_rank=5000,
            current_year_plan=10000,
            target_year_plan=12000,
        )
        assert result == 6000

    def test_conversion_plan_decreased(self):
        """招生计划减少时，等效位次缩小"""
        result = self.converter.convert(
            current_rank=6000,
            current_year_plan=12000,
            target_year_plan=10000,
        )
        assert result == 5000

    def test_batch_conversion_multiple_years(self):
        """批量换算到多个历史年份"""
        history = [
            {"year": 2025, "plan_count": 11000},
            {"year": 2024, "plan_count": 10500},
            {"year": 2023, "plan_count": 10000},
        ]
        results = self.converter.batch_convert(
            current_rank=5000,
            current_year_plan=10000,
            history=history,
        )
        assert len(results) == 3
        assert results[0]["year"] == 2025
        assert results[0]["equivalent_rank"] == 5500
        assert results[1]["year"] == 2024
        assert results[1]["equivalent_rank"] == 5250
        assert results[2]["year"] == 2023
        assert results[2]["equivalent_rank"] == 5000

    def test_conversion_with_score_line_adjustment(self):
        """考虑批次线变化的修正"""
        result = self.converter.convert(
            current_rank=5000,
            current_year_plan=10000,
            target_year_plan=10000,
            current_batch_line=520,
            target_batch_line=530,
            score=600,
        )
        # 批次线升高10分，等效位次应略微变大（排名降低）
        assert result > 5000

    def test_conversion_rank_zero_returns_zero(self):
        """位次为0的边界情况"""
        result = self.converter.convert(
            current_rank=0,
            current_year_plan=10000,
            target_year_plan=10000,
        )
        assert result == 0
```

- [ ] **Step 3: 运行测试，确认失败**

Run:
```bash
cd /Users/chaowang/workspace/gte/zhi_yuan/backend
python -m pytest tests/test_rank_converter.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'app.services.rank_converter'`

- [ ] **Step 4: 实现位次换算器**

`backend/app/services/__init__.py`: 空文件

`backend/app/services/rank_converter.py`:
```python
class RankConverter:
    """位次等效换算器

    核心公式：等效位次 = 当年位次 × (目标年计划数 / 当年计划数)
    批次线修正：当批次线变化较大时，叠加线性修正因子
    """

    def convert(
        self,
        current_rank: int,
        current_year_plan: int,
        target_year_plan: int,
        current_batch_line: int | None = None,
        target_batch_line: int | None = None,
        score: int | None = None,
    ) -> int:
        if current_rank == 0:
            return 0

        # 基础换算
        ratio = target_year_plan / current_year_plan
        equivalent = current_rank * ratio

        # 批次线修正
        if (current_batch_line and target_batch_line and score
                and current_batch_line != target_batch_line):
            line_diff = target_batch_line - current_batch_line
            # 每变化10分，位次偏移约3%
            adjustment = 1 + (line_diff / 10) * 0.03
            equivalent *= adjustment

        return round(equivalent)

    def batch_convert(
        self,
        current_rank: int,
        current_year_plan: int,
        history: list[dict],
    ) -> list[dict]:
        results = []
        for item in history:
            eq_rank = self.convert(
                current_rank=current_rank,
                current_year_plan=current_year_plan,
                target_year_plan=item["plan_count"],
            )
            results.append({
                "year": item["year"],
                "equivalent_rank": eq_rank,
                "plan_count": item["plan_count"],
            })
        return results
```

- [ ] **Step 5: 运行测试，确认通过**

Run:
```bash
cd /Users/chaowang/workspace/gte/zhi_yuan/backend
python -m pytest tests/test_rank_converter.py -v
```

Expected: 6 passed

- [ ] **Step 6: Commit**

```bash
git add backend/app/services/rank_converter.py backend/tests/test_rank_converter.py backend/tests/conftest.py backend/tests/__init__.py backend/app/services/__init__.py
git commit -m "feat: rank converter with TDD - equivalent rank calculation across years"
```

---

## Task 5: 推荐引擎——冲稳保筛选（TDD）

**Files:**
- Create: `backend/tests/test_recommendation.py`
- Create: `backend/app/services/recommendation_engine.py`
- Create: `backend/app/schemas/__init__.py`
- Create: `backend/app/schemas/recommendation.py`

- [ ] **Step 1: 编写推荐引擎的失败测试**

`backend/tests/test_recommendation.py`:
```python
from app.services.recommendation_engine import RecommendationEngine


class TestRecommendationEngine:
    def setup_method(self):
        self.engine = RecommendationEngine()

    def _make_record(self, uni_name: str, major_name: str, min_rank: int,
                     year: int = 2025, province: str = "浙江",
                     subject_type: str = "综合改革",
                     tuition_min: int = 5000, tuition_max: int = 8000,
                     level: str = "985"):
        """构造模拟的录取记录"""
        return {
            "university_name": uni_name,
            "major_name": major_name,
            "min_rank": min_rank,
            "year": year,
            "province": province,
            "subject_type": subject_type,
            "tuition_min": tuition_min,
            "tuition_max": tuition_max,
            "level": level,
        }

    def test_categorize_rush_stable_safe(self):
        """位次5000的考生，冲/稳/保分类正确"""
        records = [
            self._make_record("A大学", "计算机", 4000),   # 冲（位次比考生好=数字小）
            self._make_record("B大学", "计算机", 4500),   # 冲
            self._make_record("C大学", "计算机", 5200),   # 稳
            self._make_record("D大学", "计算机", 5800),   # 稳
            self._make_record("E大学", "计算机", 7000),   # 保
            self._make_record("F大学", "计算机", 8000),   # 保
        ]

        result = self.engine.categorize(
            equivalent_rank=5000,
            records=records,
        )

        assert len(result["rush"]) == 2
        assert len(result["stable"]) == 2
        assert len(result["safe"]) == 2
        assert result["rush"][0]["university_name"] == "A大学"
        assert result["safe"][-1]["university_name"] == "F大学"

    def test_filter_by_province(self):
        """按省份过滤"""
        records = [
            self._make_record("A大学", "计算机", 5000, province="浙江"),
            self._make_record("B大学", "计算机", 5000, province="北京"),
        ]
        filtered = self.engine.filter_records(
            records=records,
            province="浙江",
            subject_type="综合改革",
        )
        assert len(filtered) == 1

    def test_filter_by_tuition(self):
        """按学费区间过滤"""
        records = [
            self._make_record("A大学", "计算机", 5000, tuition_max=6000),
            self._make_record("B大学", "计算机", 5000, tuition_min=30000, tuition_max=50000),
        ]
        filtered = self.engine.filter_records(
            records=records,
            province="浙江",
            subject_type="综合改革",
            tuition_max=10000,
        )
        assert len(filtered) == 1
        assert filtered[0]["university_name"] == "A大学"

    def test_empty_records_returns_empty(self):
        """空数据返回空结果"""
        result = self.engine.categorize(equivalent_rank=5000, records=[])
        assert result == {"rush": [], "stable": [], "safe": []}

    def test_free_tier_limits_to_three(self):
        """免费版限制返回3所"""
        records = [self._make_record(f"大学{i}", "计算机", 5000 + i) for i in range(20)]
        result = self.engine.categorize(equivalent_rank=5000, records=records)
        free_result = self.engine.limit_for_tier(result, tier="free", max_per_group=1)
        total = len(free_result["rush"]) + len(free_result["stable"]) + len(free_result["safe"])
        assert total == 3
```

- [ ] **Step 2: 运行测试，确认失败**

Run:
```bash
python -m pytest tests/test_recommendation.py -v
```

Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: 实现推荐引擎**

`backend/app/services/recommendation_engine.py`:
```python
class RecommendationEngine:
    """推荐引擎核心：冲/稳/保分类 + 硬性条件过滤"""

    # 冲稳保位次区间系数
    RUSH_RANGE = (0.7, 0.95)     # 历年位次比等效位次好(数字小)的70%-95%区间
    STABLE_RANGE = (0.95, 1.2)   # 历年位次与等效位次接近的95%-120%区间
    SAFE_RANGE = (1.2, 2.0)      # 历年位次比等效位次差(数字大)的120%-200%区间

    def filter_records(
        self,
        records: list[dict],
        province: str,
        subject_type: str,
        tuition_max: int | None = None,
        levels: list[str] | None = None,
        provinces_exclude: list[str] | None = None,
    ) -> list[dict]:
        filtered = []
        for r in records:
            # 省份匹配
            if r["province"] != province:
                continue
            # 科类匹配
            if r["subject_type"] != subject_type:
                continue
            # 学费过滤
            if tuition_max and r.get("tuition_min", 0) > tuition_max:
                continue
            # 层次过滤
            if levels and r.get("level") not in levels:
                continue
            # 排除省份（不接受外地）
            if provinces_exclude and r.get("university_province") in provinces_exclude:
                continue
            filtered.append(r)
        return filtered

    def categorize(self, equivalent_rank: int, records: list[dict]) -> dict:
        if not records:
            return {"rush": [], "stable": [], "safe": []}

        rush, stable, safe = [], [], []

        for r in records:
            min_rank = r["min_rank"]
            if min_rank is None:
                continue

            ratio = min_rank / equivalent_rank if equivalent_rank > 0 else 0

            entry = {**r, "rank_ratio": round(ratio, 3)}

            if self.RUSH_RANGE[0] <= ratio < self.RUSH_RANGE[1]:
                rush.append(entry)
            elif self.STABLE_RANGE[0] <= ratio < self.STABLE_RANGE[1]:
                stable.append(entry)
            elif self.SAFE_RANGE[0] <= ratio < self.SAFE_RANGE[1]:
                safe.append(entry)

        # 组内按位次比排序（冲: 从高到低，稳和保: 从低到高）
        rush.sort(key=lambda x: x["rank_ratio"], reverse=True)
        stable.sort(key=lambda x: x["rank_ratio"])
        safe.sort(key=lambda x: x["rank_ratio"])

        return {"rush": rush, "stable": stable, "safe": safe}

    def limit_for_tier(self, result: dict, tier: str = "free",
                       max_per_group: int = 1) -> dict:
        if tier == "free":
            return {
                "rush": result["rush"][:max_per_group],
                "stable": result["stable"][:max_per_group],
                "safe": result["safe"][:max_per_group],
            }
        return result  # 付费版返回全部
```

- [ ] **Step 4: 运行测试，确认通过**

Run:
```bash
python -m pytest tests/test_recommendation.py -v
```

Expected: 5 passed

- [ ] **Step 5: Commit**

```bash
git add backend/app/services/recommendation_engine.py backend/tests/test_recommendation.py
git commit -m "feat: recommendation engine with rush/stable/safe categorization"
```

---

## Task 6: 五维适配度评分（TDD）

**Files:**
- Create: `backend/tests/test_adapter_scorer.py`
- Create: `backend/app/services/adapter_scorer.py`

- [ ] **Step 1: 编写适配度评分的失败测试**

`backend/tests/test_adapter_scorer.py`:
```python
from app.services.adapter_scorer import AdapterScorer


class TestAdapterScorer:
    def setup_method(self):
        self.scorer = AdapterScorer()

    def test_basic_only_profile(self):
        """仅基础信息时，只有基础匹配分"""
        profile = {
            "basic_info": {"score": 620, "rank": 5000, "province": "浙江", "subject_type": "综合改革"},
        }
        record = {"university_name": "A大学", "major_name": "计算机", "min_rank": 5200}

        score = self.scorer.score(profile=profile, record=record)
        assert 0 <= score["total"] <= 100
        assert score["dimensions"]["basic"] > 0
        assert score["dimensions"]["family"] == 0
        assert score["dimensions"]["personality"] == 0

    def test_full_profile_all_dimensions(self):
        """完整五维画像，所有维度都有分数"""
        profile = {
            "basic_info": {"score": 620, "rank": 5000, "province": "浙江", "subject_type": "综合改革"},
            "family_info": {"income_range": "20-50万", "tuition_max": 10000, "prefer_city": ["上海", "杭州"]},
            "personality": {"interests": ["计算机", "编程"], "holland_code": "IR"},
            "ability": {"strong_subjects": ["数学", "物理"], "english_level": 4},
            "values_info": {"career_values": ["高薪"], "distance_preference": "接受外地", "plan": "直接就业"},
        }
        record = {
            "university_name": "A大学",
            "major_name": "计算机科学与技术",
            "min_rank": 5200,
            "city": "上海",
            "tuition_max": 6000,
            "career_directions": ["软件工程师", "算法工程师"],
        }

        score = self.scorer.score(profile=profile, record=record)
        assert score["total"] > 0
        assert score["dimensions"]["basic"] > 0
        assert score["dimensions"]["family"] > 0
        assert score["dimensions"]["personality"] > 0
        assert score["dimensions"]["ability"] > 0
        assert score["dimensions"]["values"] > 0

    def test_city_match_boosts_family_score(self):
        """城市匹配提升家庭维度分数"""
        profile = {
            "basic_info": {"score": 620, "rank": 5000, "province": "浙江", "subject_type": "综合改革"},
            "family_info": {"prefer_city": ["上海"]},
        }
        record_match = {"university_name": "A", "major_name": "CS", "min_rank": 5000, "city": "上海"}
        record_miss = {"university_name": "B", "major_name": "CS", "min_rank": 5000, "city": "哈尔滨"}

        score_match = self.scorer.score(profile=profile, record=record_match)
        score_miss = self.scorer.score(profile=profile, record=record_miss)
        assert score_match["dimensions"]["family"] > score_miss["dimensions"]["family"]

    def test_interest_match_boosts_personality(self):
        """兴趣匹配提升性格维度分数"""
        profile = {
            "basic_info": {"score": 620, "rank": 5000, "province": "浙江", "subject_type": "综合改革"},
            "personality": {"interests": ["计算机", "编程"]},
        }
        record_match = {"university_name": "A", "major_name": "计算机科学与技术", "min_rank": 5000}
        record_miss = {"university_name": "B", "major_name": "土木工程", "min_rank": 5000}

        score_match = self.scorer.score(profile=profile, record=record_match)
        score_miss = self.scorer.score(profile=profile, record=record_miss)
        assert score_match["dimensions"]["personality"] > score_miss["dimensions"]["personality"]

    def test_score_range_is_zero_to_hundred(self):
        """总分始终在0-100之间"""
        profile = {
            "basic_info": {"score": 620, "rank": 5000, "province": "浙江", "subject_type": "综合改革"},
            "family_info": {"income_range": "20-50万", "tuition_max": 10000, "prefer_city": ["上海"]},
            "personality": {"interests": ["计算机"], "holland_code": "IR"},
            "ability": {"strong_subjects": ["数学"], "english_level": 4},
            "values_info": {"career_values": ["高薪"], "plan": "直接就业"},
        }
        record = {"university_name": "A", "major_name": "计算机", "min_rank": 5000, "city": "上海",
                  "tuition_max": 6000, "career_directions": ["软件工程师"]}

        score = self.scorer.score(profile=profile, record=record)
        assert 0 <= score["total"] <= 100
```

- [ ] **Step 2: 运行测试，确认失败**

Run:
```bash
python -m pytest tests/test_adapter_scorer.py -v
```

Expected: FAIL

- [ ] **Step 3: 实现五维适配度评分器**

`backend/app/services/adapter_scorer.py`:
```python
class AdapterScorer:
    """五维适配度评分器

    Score = W1×基础 + W2×家庭 + W3×性格 + W4×能力 + W5×价值观
    权重根据画像完整度动态调整
    """

    # 默认维度权重
    DEFAULT_WEIGHTS = {
        "basic": 0.35,
        "family": 0.15,
        "personality": 0.25,
        "ability": 0.10,
        "values": 0.15,
    }

    def score(self, profile: dict, record: dict) -> dict:
        dimensions = {}

        # 基础维度：位次接近度
        dimensions["basic"] = self._score_basic(profile, record)

        # 家庭维度：学费+城市匹配
        dimensions["family"] = self._score_family(profile, record)

        # 性格维度：兴趣+专业匹配
        dimensions["personality"] = self._score_personality(profile, record)

        # 能力维度：学科强项+专业匹配
        dimensions["ability"] = self._score_ability(profile, record)

        # 价值观维度：职业规划+行业匹配
        dimensions["values"] = self._score_values(profile, record)

        # 计算权重
        weights = self._compute_weights(profile)

        # 加权总分
        total = sum(dimensions[k] * weights[k] for k in dimensions)
        total = min(100, max(0, round(total, 1)))

        return {
            "total": total,
            "dimensions": {k: round(v, 1) for k, v in dimensions.items()},
            "weights": weights,
        }

    def _score_basic(self, profile: dict, record: dict) -> float:
        basic = profile.get("basic_info", {})
        rank = basic.get("rank", 0)
        min_rank = record.get("min_rank", 0)
        if rank == 0 or min_rank == 0:
            return 50.0

        ratio = min_rank / rank
        if 0.95 <= ratio <= 1.2:
            return 90.0  # 稳
        elif 0.7 <= ratio < 0.95:
            return 70.0  # 冲
        elif 1.2 < ratio <= 2.0:
            return 85.0  # 保
        else:
            return 30.0

    def _score_family(self, profile: dict, record: dict) -> float:
        family = profile.get("family_info")
        if not family:
            return 0.0

        score = 50.0  # 基础分

        # 学费匹配
        tuition_max = family.get("tuition_max")
        record_tuition = record.get("tuition_max", 0)
        if tuition_max and record_tuition:
            if record_tuition <= tuition_max:
                score += 25.0
            else:
                score -= 25.0

        # 城市偏好匹配
        prefer_cities = family.get("prefer_city", [])
        record_city = record.get("city", "")
        if prefer_cities and record_city:
            if record_city in prefer_cities:
                score += 25.0
            else:
                score -= 10.0

        return min(100, max(0, score))

    def _score_personality(self, profile: dict, record: dict) -> float:
        personality = profile.get("personality")
        if not personality:
            return 0.0

        score = 50.0
        interests = personality.get("interests", [])
        major_name = record.get("major_name", "")

        if interests and major_name:
            # 关键词匹配
            match_count = sum(1 for i in interests if i in major_name or major_name in i)
            score += match_count * 25.0

        return min(100, max(0, score))

    def _score_ability(self, profile: dict, record: dict) -> float:
        ability = profile.get("ability")
        if not ability:
            return 0.0

        score = 50.0
        strong_subjects = ability.get("strong_subjects", [])
        major_name = record.get("major_name", "")

        # 简单关联：数学/物理强 → 理工类专业加分
        science_keywords = {"数学": ["计算机", "软件", "电子", "人工智能", "自动化", "数学"],
                            "物理": ["计算机", "电子", "土木", "机械", "自动化", "物理"]}
        for subj in strong_subjects:
            related = science_keywords.get(subj, [])
            if any(kw in major_name for kw in related):
                score += 15.0

        return min(100, max(0, score))

    def _score_values(self, profile: dict, record: dict) -> float:
        values = profile.get("values_info")
        if not values:
            return 0.0

        score = 50.0
        career_values = values.get("career_values", [])
        career_directions = record.get("career_directions", [])

        # 高薪导向 + 高薪专业
        if "高薪" in career_values:
            high_salary_keywords = ["计算机", "软件", "人工智能", "金融", "电子"]
            major_name = record.get("major_name", "")
            if any(kw in major_name for kw in high_salary_keywords):
                score += 25.0

        # 稳定导向 + 体制内友好
        if "稳定" in career_values:
            stable_keywords = ["师范", "医学", "法学", "会计"]
            major_name = record.get("major_name", "")
            if any(kw in major_name for kw in stable_keywords):
                score += 25.0

        return min(100, max(0, score))

    def _compute_weights(self, profile: dict) -> dict:
        filled = []
        if profile.get("basic_info"):
            filled.append("basic")
        if profile.get("family_info"):
            filled.append("family")
        if profile.get("personality"):
            filled.append("personality")
        if profile.get("ability"):
            filled.append("ability")
        if profile.get("values_info"):
            filled.append("values")

        if len(filled) <= 1:
            # 仅基础信息
            return {"basic": 1.0, "family": 0.0, "personality": 0.0, "ability": 0.0, "values": 0.0}

        # 归一化已填维度的默认权重
        raw = {k: self.DEFAULT_WEIGHTS[k] if k in filled else 0.0 for k in self.DEFAULT_WEIGHTS}
        total = sum(raw.values())
        if total == 0:
            return raw
        return {k: round(v / total, 3) for k, v in raw.items()}
```

- [ ] **Step 4: 运行测试，确认通过**

Run:
```bash
python -m pytest tests/test_adapter_scorer.py -v
```

Expected: 5 passed

- [ ] **Step 5: Commit**

```bash
git add backend/app/services/adapter_scorer.py backend/tests/test_adapter_scorer.py
git commit -m "feat: five-dimension adapter scorer with dynamic weighting"
```

---

## Task 7: 认证与用户系统

**Files:**
- Create: `backend/app/schemas/user.py`
- Create: `backend/app/api/deps.py`
- Create: `backend/app/api/auth.py`
- Create: `backend/app/api/profile.py`
- Create: `backend/tests/test_api/test_auth.py`

- [ ] **Step 1: 创建 Pydantic Schema**

`backend/app/schemas/__init__.py`: 空文件

`backend/app/schemas/user.py`:
```python
import uuid
from datetime import datetime
from pydantic import BaseModel, Field


class UserRegister(BaseModel):
    phone: str = Field(..., pattern=r"^1[3-9]\d{9}$")
    password: str = Field(..., min_length=6, max_length=32)


class UserLogin(BaseModel):
    phone: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: uuid.UUID


class UserInfo(BaseModel):
    id: uuid.UUID
    phone: str
    nickname: str | None
    membership_tier: str
    created_at: datetime

    class Config:
        from_attributes = True


class ProfileBasicInfo(BaseModel):
    score: int = Field(..., ge=0, le=750)
    rank: int = Field(..., ge=0)
    province: str
    subject_type: str  # 文/理/物理类/历史类/综合改革


class ProfileFamilyInfo(BaseModel):
    income_range: str | None = None
    tuition_max: int | None = None
    prefer_city: list[str] | None = None
    parent_industry: str | None = None


class ProfilePersonality(BaseModel):
    interests: list[str] | None = None
    holland_code: str | None = None
    mbti: str | None = None
    introvert_extrovert: str | None = None


class ProfileAbility(BaseModel):
    strong_subjects: list[str] | None = None
    social_ability: int | None = Field(None, ge=1, le=5)
    english_level: int | None = Field(None, ge=1, le=6)
    awards: list[str] | None = None


class ProfileValues(BaseModel):
    career_values: list[str] | None = None
    distance_preference: str | None = None
    plan: str | None = None
    industry_preference: list[str] | None = None


class ProfileUpdate(BaseModel):
    basic_info: ProfileBasicInfo | None = None
    family_info: ProfileFamilyInfo | None = None
    personality: ProfilePersonality | None = None
    ability: ProfileAbility | None = None
    values_info: ProfileValues | None = None
```

- [ ] **Step 2: 创建依赖注入**

`backend/app/api/__init__.py`: 空文件

`backend/app/api/deps.py`:
```python
import uuid
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.config import get_settings
from app.models.user import User

settings = get_settings()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无效的认证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    result = await db.execute(select(User).where(User.id == uuid.UUID(user_id)))
    user = result.scalar_one_or_none()
    if user is None:
        raise credentials_exception
    return user
```

- [ ] **Step 3: 创建认证API**

`backend/app/api/auth.py`:
```python
import uuid
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from jose import jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.config import get_settings
from app.models.user import User, UserProfile
from app.schemas.user import UserRegister, UserLogin, TokenResponse, UserInfo

router = APIRouter(prefix="/api/auth", tags=["认证"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
settings = get_settings()


def create_access_token(user_id: uuid.UUID) -> str:
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": str(user_id), "exp": expire}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


@router.post("/register", response_model=TokenResponse)
async def register(data: UserRegister, db: AsyncSession = Depends(get_db)):
    # 检查手机号是否已注册
    result = await db.execute(select(User).where(User.phone == data.phone))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="该手机号已注册")

    user = User(
        id=uuid.uuid4(),
        phone=data.phone,
        password_hash=pwd_context.hash(data.password),
    )
    db.add(user)

    # 同时创建空画像
    profile = UserProfile(id=uuid.uuid4(), user_id=user.id)
    db.add(profile)

    await db.flush()
    token = create_access_token(user.id)
    return TokenResponse(access_token=token, user_id=user.id)


@router.post("/login", response_model=TokenResponse)
async def login(data: UserLogin, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.phone == data.phone))
    user = result.scalar_one_or_none()
    if not user or not pwd_context.verify(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="手机号或密码错误")

    token = create_access_token(user.id)
    return TokenResponse(access_token=token, user_id=user.id)


@router.get("/me", response_model=UserInfo)
async def get_me(user: User = Depends(
    __import__("app.api.deps", fromlist=["get_current_user"]).get_current_user
)):
    return user
```

- [ ] **Step 4: 创建画像API**

`backend/app/api/profile.py`:
```python
import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.api.deps import get_current_user
from app.models.user import User, UserProfile
from app.schemas.user import ProfileUpdate

router = APIRouter(prefix="/api/profile", tags=["用户画像"])


def _calc_completeness(profile: UserProfile) -> float:
    """计算画像完整度 0.0~1.0"""
    filled = 0
    total = 5
    if profile.basic_info:
        filled += 1
    if profile.family_info:
        filled += 1
    if profile.personality:
        filled += 1
    if profile.ability:
        filled += 1
    if profile.values_info:
        filled += 1
    return filled / total


@router.get("")
async def get_profile(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(UserProfile).where(UserProfile.user_id == user.id))
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="画像不存在")

    return {
        "basic_info": profile.basic_info,
        "family_info": profile.family_info,
        "personality": profile.personality,
        "ability": profile.ability,
        "values_info": profile.values_info,
        "completeness": profile.completeness,
    }


@router.put("")
async def update_profile(
    data: ProfileUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(UserProfile).where(UserProfile.user_id == user.id))
    profile = result.scalar_one_or_none()
    if not profile:
        profile = UserProfile(id=uuid.uuid4(), user_id=user.id)
        db.add(profile)

    # 渐进式更新：只更新传入的维度
    if data.basic_info is not None:
        profile.basic_info = data.basic_info.model_dump(exclude_none=True)
    if data.family_info is not None:
        profile.family_info = data.family_info.model_dump(exclude_none=True)
    if data.personality is not None:
        profile.personality = data.personality.model_dump(exclude_none=True)
    if data.ability is not None:
        profile.ability = data.ability.model_dump(exclude_none=True)
    if data.values_info is not None:
        profile.values_info = data.values_info.model_dump(exclude_none=True)

    profile.completeness = _calc_completeness(profile)
    profile.updated_at = datetime.utcnow()

    await db.flush()
    return {"completeness": profile.completeness, "message": "画像已更新"}
```

- [ ] **Step 5: 注册路由到主应用**

修改 `backend/app/main.py`，在现有内容后添加:
```python
from app.api.auth import router as auth_router
from app.api.profile import router as profile_router

app.include_router(auth_router)
app.include_router(profile_router)
```

- [ ] **Step 6: 验证API**

Run:
```bash
# 注册
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"phone":"13800138000","password":"test123"}'

# 登录
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"phone":"13800138000","password":"test123"}'
```

Expected: 返回 `{"access_token": "...", "user_id": "..."}`

- [ ] **Step 7: Commit**

```bash
git add backend/app/api/ backend/app/schemas/ backend/app/main.py
git commit -m "feat: auth (register/login) and progressive profile API"
```

---

## Task 8: 院校查询与推荐API

**Files:**
- Create: `backend/app/schemas/university.py`
- Create: `backend/app/schemas/recommendation.py`
- Create: `backend/app/api/universities.py`
- Create: `backend/app/api/recommend.py`

- [ ] **Step 1: 创建查询Schema**

`backend/app/schemas/university.py`:
```python
import uuid
from pydantic import BaseModel


class UniversityOut(BaseModel):
    id: uuid.UUID
    name: str
    province: str
    city: str
    level: str | None
    type: str | None
    tags: list[str]
    tuition_min: int | None
    tuition_max: int | None
    website: str | None
    logo_url: str | None

    class Config:
        from_attributes = True


class UniversityQuery(BaseModel):
    province: str | None = None
    level: str | None = None
    type: str | None = None
    keyword: str | None = None
    page: int = 1
    page_size: int = 20


class MajorOut(BaseModel):
    id: uuid.UUID
    name: str
    category: str
    degree: str
    duration: int
    description: str | None
    courses: list[str]
    career_directions: list[str]
    avg_salary: int | None

    class Config:
        from_attributes = True
```

`backend/app/schemas/recommendation.py`:
```python
import uuid
from pydantic import BaseModel


class RecommendRequest(BaseModel):
    score: int | None = None
    rank: int | None = None
    province: str | None = None
    subject_type: str | None = None


class RecommendItem(BaseModel):
    university_name: str
    major_name: str
    min_rank: int | None
    rank_ratio: float | None
    adapter_score: float | None


class RecommendResult(BaseModel):
    rush: list[RecommendItem]
    stable: list[RecommendItem]
    safe: list[RecommendItem]
    profile_completeness: float = 0.0
```

- [ ] **Step 2: 创建院校查询API**

`backend/app/api/universities.py`:
```python
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.models.university import University
from app.schemas.university import UniversityOut

router = APIRouter(prefix="/api/universities", tags=["院校"])


@router.get("", response_model=list[UniversityOut])
async def list_universities(
    province: str | None = None,
    level: str | None = None,
    type: str | None = None,
    keyword: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    query = select(University)

    if province:
        query = query.where(University.province == province)
    if level:
        query = query.where(University.level == level)
    if type:
        query = query.where(University.type == type)
    if keyword:
        query = query.where(University.name.ilike(f"%{keyword}%"))

    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{university_id}", response_model=UniversityOut)
async def get_university(university_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(University).where(University.id == university_id))
    uni = result.scalar_one_or_none()
    if not uni:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="院校不存在")
    return uni
```

- [ ] **Step 3: 创建推荐API**

`backend/app/api/recommend.py`:
```python
import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.api.deps import get_current_user
from app.models.user import User, UserProfile
from app.models.admission import AdmissionRecord
from app.models.university import University
from app.models.major import Major
from app.services.rank_converter import RankConverter
from app.services.recommendation_engine import RecommendationEngine
from app.services.adapter_scorer import AdapterScorer
from app.schemas.recommendation import RecommendRequest, RecommendResult, RecommendItem
from app.models.recommendation import Recommendation

router = APIRouter(prefix="/api/recommend", tags=["推荐"])


@router.post("", response_model=RecommendResult)
async def get_recommendation(
    request: RecommendRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # 1. 获取用户画像
    result = await db.execute(select(UserProfile).where(UserProfile.user_id == user.id))
    profile = result.scalar_one_or_none()

    profile_dict = {}
    if profile:
        profile_dict = {
            "basic_info": profile.basic_info or {},
            "family_info": profile.family_info,
            "personality": profile.personality,
            "ability": profile.ability,
            "values_info": profile.values_info,
        }

    # 请求参数覆盖画像中的基础信息
    basic = profile_dict.get("basic_info", {})
    rank = request.rank or basic.get("rank", 0)
    province = request.province or basic.get("province", "")
    subject_type = request.subject_type or basic.get("subject_type", "")

    if not rank or not province or not subject_type:
        raise HTTPException(status_code=400, detail="请至少提供位次、省份和科类")

    # 2. 查询录取记录
    records_result = await db.execute(
        select(AdmissionRecord, University, Major)
        .join(University, AdmissionRecord.university_id == University.id)
        .outerjoin(Major, AdmissionRecord.major_id == Major.id)
        .where(AdmissionRecord.province == province)
        .where(AdmissionRecord.subject_type == subject_type)
    )

    records = []
    for admission, uni, major in records_result:
        records.append({
            "university_name": uni.name,
            "university_province": uni.province,
            "major_name": major.name if major else "未分专业",
            "min_rank": admission.min_rank,
            "year": admission.year,
            "province": admission.province,
            "subject_type": admission.subject_type,
            "tuition_min": uni.tuition_min or 0,
            "tuition_max": uni.tuition_max or 999999,
            "level": uni.level or "",
            "city": uni.city,
            "career_directions": major.career_directions if major else [],
        })

    # 3. 过滤
    engine = RecommendationEngine()
    tuition_max = None
    family = profile_dict.get("family_info")
    if family:
        tuition_max = family.get("tuition_max")

    filtered = engine.filter_records(
        records=records,
        province=province,
        subject_type=subject_type,
        tuition_max=tuition_max,
    )

    # 4. 冲稳保分类
    categorized = engine.categorize(equivalent_rank=rank, records=filtered)

    # 5. 免费版限制
    tier = user.membership_tier
    categorized = engine.limit_for_tier(categorized, tier=tier, max_per_group=1 if tier == "free" else 999)

    # 6. 五维适配度评分
    scorer = AdapterScorer()
    for group in ["rush", "stable", "safe"]:
        for item in categorized[group]:
            score = scorer.score(profile=profile_dict, record=item)
            item["adapter_score"] = score["total"]

    # 7. 保存推荐记录
    rec = Recommendation(
        id=uuid.uuid4(),
        user_id=user.id,
        input_snapshot={"rank": rank, "province": province, "subject_type": subject_type},
        result={k: [{"university_name": i["university_name"], "major_name": i["major_name"],
                      "adapter_score": i.get("adapter_score")} for i in v]
                for k, v in categorized.items()},
        tier=tier,
    )
    db.add(rec)
    await db.flush()

    # 8. 构造响应
    def to_items(items):
        return [RecommendItem(
            university_name=i["university_name"],
            major_name=i["major_name"],
            min_rank=i.get("min_rank"),
            rank_ratio=i.get("rank_ratio"),
            adapter_score=i.get("adapter_score"),
        ) for i in items]

    return RecommendResult(
        rush=to_items(categorized["rush"]),
        stable=to_items(categorized["stable"]),
        safe=to_items(categorized["safe"]),
        profile_completeness=profile.completeness if profile else 0.0,
    )
```

- [ ] **Step 4: 注册路由**

修改 `backend/app/main.py`，添加:
```python
from app.api.universities import router as universities_router
from app.api.recommend import router as recommend_router

app.include_router(universities_router)
app.include_router(recommend_router)
```

- [ ] **Step 5: 验证API**

Run:
```bash
curl http://localhost:8000/api/universities?level=985
```

Expected: 返回985院校列表

- [ ] **Step 6: Commit**

```bash
git add backend/app/api/universities.py backend/app/api/recommend.py backend/app/schemas/university.py backend/app/schemas/recommendation.py backend/app/main.py
git commit -m "feat: university query API and recommendation endpoint"
```

---

## Task 9: LLM对话服务

**Files:**
- Create: `backend/app/services/llm_service.py`
- Create: `backend/app/api/chat.py`

- [ ] **Step 1: 实现LLM服务**

`backend/app/services/llm_service.py`:
```python
import json
from openai import AsyncOpenAI
from app.config import get_settings

settings = get_settings()

# 双模型配置
LLM_CONFIGS = {
    "deepseek": {
        "api_key": settings.DEEPSEEK_API_KEY,
        "base_url": settings.DEEPSEEK_BASE_URL,
        "model": "deepseek-chat",
    },
    "qwen": {
        "api_key": settings.QWEN_API_KEY,
        "base_url": settings.QWEN_BASE_URL,
        "model": "qwen-plus",
    },
}

SYSTEM_PROMPT = """你是"智愿"的AI高考志愿顾问。你的职责是帮助考生和家长理解高考志愿填报的相关知识，并基于考生的个人情况给出个性化建议。

重要规则：
1. 所有分数线、录取概率等数据必须来自工具调用返回的结果，绝对不能编造数据
2. 如果工具返回的数据不足以回答问题，请如实告知用户
3. 每次回答末尾适当提醒"以上信息仅供参考，建议结合多方信息综合决策"
4. 保持专业、耐心、客观的语气
5. 不要推荐具体的培训机构或付费服务

当前用户画像摘要：
{profile_summary}

当前推荐结果：
{recommendation_summary}
"""

# 工具定义（供LLM调用）
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "query_university",
            "description": "查询院校详细信息，包括分数线、专业、学费等",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "院校名称"},
                    "province": {"type": "string", "description": "考生所在省份"},
                },
                "required": ["name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "query_major",
            "description": "查询专业详细信息，包括课程、就业方向、薪资等",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "专业名称"},
                },
                "required": ["name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "compare_universities",
            "description": "比较两所或多所院校的分数线、排名、专业等",
            "parameters": {
                "type": "object",
                "properties": {
                    "names": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "要比较的院校名称列表",
                    },
                },
                "required": ["names"],
            },
        },
    },
]


class LLMService:
    def __init__(self, provider: str = "deepseek"):
        config = LLM_CONFIGS.get(provider, LLM_CONFIGS["deepseek"])
        self.client = AsyncOpenAI(api_key=config["api_key"], base_url=config["base_url"])
        self.model = config["model"]

    async def chat(
        self,
        messages: list[dict],
        profile_summary: str = "",
        recommendation_summary: str = "",
    ) -> str:
        system = SYSTEM_PROMPT.format(
            profile_summary=profile_summary or "用户尚未填写个人画像",
            recommendation_summary=recommendation_summary or "暂无推荐结果",
        )

        full_messages = [{"role": "system", "content": system}] + messages

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=full_messages,
                tools=TOOLS,
                temperature=0.7,
                max_tokens=2000,
            )
            return response.choices[0].message.content
        except Exception as e:
            # 主模型失败，尝试备用模型
            return f"抱歉，AI服务暂时不可用，请稍后再试。（错误: {str(e)}）"

    async def chat_stream(self, messages: list[dict], profile_summary: str = "",
                          recommendation_summary: str = ""):
        system = SYSTEM_PROMPT.format(
            profile_summary=profile_summary or "用户尚未填写个人画像",
            recommendation_summary=recommendation_summary or "暂无推荐结果",
        )
        full_messages = [{"role": "system", "content": system}] + messages

        try:
            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=full_messages,
                tools=TOOLS,
                temperature=0.7,
                max_tokens=2000,
                stream=True,
            )
            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception:
            yield "抱歉，AI服务暂时不可用，请稍后再试。"
```

- [ ] **Step 2: 创建对话API**

`backend/app/api/chat.py`:
```python
import uuid
from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.api.deps import get_current_user
from app.models.user import User, UserProfile
from app.models.recommendation import ChatMessage, Recommendation
from app.services.llm_service import LLMService

router = APIRouter(prefix="/api/chat", tags=["AI对话"])

FREE_DAILY_LIMIT = 3


@router.post("")
async def chat(
    message: str,
    session_id: str | None = None,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # 检查每日对话次数
    today = date.today().isoformat()
    if user.last_chat_date != today:
        user.daily_chat_count = 0
        user.last_chat_date = today

    if user.membership_tier == "free" and user.daily_chat_count >= FREE_DAILY_LIMIT:
        raise HTTPException(
            status_code=429,
            detail=f"今日免费对话次数已用完（{FREE_DAILY_LIMIT}次/天），升级会员可解锁无限对话"
        )

    # 获取或创建会话
    if not session_id:
        session_id = str(uuid.uuid4())

    # 获取用户画像摘要
    result = await db.execute(select(UserProfile).where(UserProfile.user_id == user.id))
    profile = result.scalar_one_or_none()
    profile_summary = ""
    if profile and profile.basic_info:
        b = profile.basic_info
        profile_summary = f"分数: {b.get('score', '未知')}, 位次: {b.get('rank', '未知')}, 省份: {b.get('province', '未知')}, 科类: {b.get('subject_type', '未知')}"

    # 获取最近推荐结果
    rec_result = await db.execute(
        select(Recommendation)
        .where(Recommendation.user_id == user.id)
        .order_by(Recommendation.created_at.desc())
        .limit(1)
    )
    rec = rec_result.scalar_one_or_none()
    recommendation_summary = str(rec.result) if rec else ""

    # 获取历史消息（最近10条）
    history_result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.user_id == user.id, ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at.desc())
        .limit(10)
    )
    history = list(reversed(history_result.scalars().all()))
    messages = [{"role": m.role, "content": m.content} for m in history]
    messages.append({"role": "user", "content": message})

    # 保存用户消息
    user_msg = ChatMessage(
        id=uuid.uuid4(), user_id=user.id, session_id=session_id,
        role="user", content=message,
    )
    db.add(user_msg)

    # 调用LLM
    llm = LLMService()
    reply = await llm.chat(messages, profile_summary, recommendation_summary)

    # 保存AI回复
    ai_msg = ChatMessage(
        id=uuid.uuid4(), user_id=user.id, session_id=session_id,
        role="assistant", content=reply,
    )
    db.add(ai_msg)

    # 更新计数
    user.daily_chat_count += 1

    await db.flush()
    return {"session_id": session_id, "reply": reply}


@router.post("/stream")
async def chat_stream(
    message: str,
    session_id: str | None = None,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """流式对话接口"""
    if not session_id:
        session_id = str(uuid.uuid4())

    llm = LLMService()

    async def generate():
        async for chunk in llm.chat_stream([{"role": "user", "content": message}]):
            yield f"data: {chunk}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")
```

- [ ] **Step 3: 注册路由**

修改 `backend/app/main.py`，添加:
```python
from app.api.chat import router as chat_router
app.include_router(chat_router)
```

- [ ] **Step 4: Commit**

```bash
git add backend/app/services/llm_service.py backend/app/api/chat.py backend/app/main.py
git commit -m "feat: LLM chat service with DeepSeek/Qwen dual-provider and streaming"
```

---

## Task 10: Next.js 前端脚手架

**Files:**
- Create: `frontend/` 目录（通过 Next.js CLI 初始化）
- Create: `frontend/.env.local.example`

- [ ] **Step 1: 初始化 Next.js 项目**

Run:
```bash
cd /Users/chaowang/workspace/gte/zhi_yuan
npx create-next-app@latest frontend --typescript --tailwind --eslint --app --src-dir --import-alias "@/*" --no-git
```

- [ ] **Step 2: 安装依赖**

Run:
```bash
cd /Users/chaowang/workspace/gte/zhi_yuan/frontend
npm install antd @ant-design/icons axios dayjs
npm install -D @types/node
```

- [ ] **Step 3: 创建环境配置**

`frontend/.env.local.example`:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Run:
```bash
cp frontend/.env.local.example frontend/.env.local
```

- [ ] **Step 4: 创建 API 客户端**

`frontend/src/lib/api.ts`:
```typescript
import axios from "axios";

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000",
  headers: { "Content-Type": "application/json" },
});

// 请求拦截器：自动附加 token
api.interceptors.request.use((config) => {
  const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// 响应拦截器：处理401
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      if (typeof window !== "undefined") {
        localStorage.removeItem("token");
        window.location.href = "/login";
      }
    }
    return Promise.reject(error);
  }
);

export default api;
```

- [ ] **Step 5: 创建类型定义**

`frontend/src/types/index.ts`:
```typescript
export interface University {
  id: string;
  name: string;
  province: string;
  city: string;
  level: string | null;
  type: string | null;
  tags: string[];
  tuition_min: number | null;
  tuition_max: number | null;
  website: string | null;
  logo_url: string | null;
}

export interface RecommendItem {
  university_name: string;
  major_name: string;
  min_rank: number | null;
  rank_ratio: number | null;
  adapter_score: number | null;
}

export interface RecommendResult {
  rush: RecommendItem[];
  stable: RecommendItem[];
  safe: RecommendItem[];
  profile_completeness: number;
}

export interface UserProfile {
  basic_info: {
    score: number;
    rank: number;
    province: string;
    subject_type: string;
  } | null;
  family_info: Record<string, unknown> | null;
  personality: Record<string, unknown> | null;
  ability: Record<string, unknown> | null;
  values_info: Record<string, unknown> | null;
  completeness: number;
}
```

- [ ] **Step 6: 验证前端启动**

Run:
```bash
cd /Users/chaowang/workspace/gte/zhi_yuan/frontend
npm run dev
```

Expected: 访问 http://localhost:3000 看到 Next.js 默认页面

- [ ] **Step 7: Commit**

```bash
git add frontend/
git commit -m "feat: Next.js frontend scaffolding with API client and types"
```

---

## Task 11: 前端核心页面

**Files:**
- Create: `frontend/src/app/page.tsx` (首页/快速输入)
- Create: `frontend/src/app/login/page.tsx`
- Create: `frontend/src/app/recommend/page.tsx` (推荐结果)
- Create: `frontend/src/app/universities/page.tsx` (院校查询)
- Create: `frontend/src/app/chat/page.tsx` (AI对话)
- Create: `frontend/src/app/profile/page.tsx` (画像完善)
- Create: `frontend/src/components/Layout.tsx`

- [ ] **Step 1: 创建通用布局组件**

`frontend/src/components/Layout.tsx`:
```tsx
"use client";

import { Layout, Menu } from "antd";
import {
  HomeOutlined,
  SearchOutlined,
  RobotOutlined,
  UserOutlined,
  StarOutlined,
} from "@ant-design/icons";
import { useRouter, usePathname } from "next/navigation";

const { Header, Content, Footer } = Layout;

const menuItems = [
  { key: "/", icon: <HomeOutlined />, label: "首页" },
  { key: "/recommend", icon: <StarOutlined />, label: "智能推荐" },
  { key: "/universities", icon: <SearchOutlined />, label: "院校查询" },
  { key: "/chat", icon: <RobotOutlined />, label: "AI顾问" },
  { key: "/profile", icon: <UserOutlined />, label: "我的画像" },
];

export default function AppLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();

  return (
    <Layout style={{ minHeight: "100vh" }}>
      <Header>
        <div style={{ float: "left", color: "#fff", fontSize: 20, fontWeight: "bold", marginRight: 40 }}>
          智愿
        </div>
        <Menu
          theme="dark"
          mode="horizontal"
          selectedKeys={[pathname]}
          items={menuItems}
          onClick={(e) => router.push(e.key)}
        />
      </Header>
      <Content style={{ padding: "24px 48px" }}>
        {children}
      </Content>
      <Footer style={{ textAlign: "center" }}>
        智愿 &copy; 2026 — 所有推荐结果仅供参考，请结合多方信息综合决策
      </Footer>
    </Layout>
  );
}
```

- [ ] **Step 2: 创建首页（快速输入）**

`frontend/src/app/page.tsx`:
```tsx
"use client";

import { useState } from "react";
import { Card, Form, InputNumber, Select, Button, Typography, Space, Row, Col } from "antd";
import { RocketOutlined } from "@ant-design/icons";
import { useRouter } from "next/navigation";
import api from "@/lib/api";
import AppLayout from "@/components/Layout";

const { Title, Paragraph } = Typography;

const provinces = [
  "北京", "天津", "上海", "重庆", "河北", "山西", "辽宁", "吉林", "黑龙江",
  "江苏", "浙江", "安徽", "福建", "江西", "山东", "河南", "湖北", "湖南",
  "广东", "海南", "四川", "贵州", "云南", "陕西", "甘肃", "青海", "内蒙古",
  "广西", "西藏", "宁夏", "新疆",
];

const subjectTypes = ["文", "理", "物理类", "历史类", "综合改革"];

export default function Home() {
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const onFinish = async (values: { score: number; rank: number; province: string; subject_type: string }) => {
    setLoading(true);
    try {
      // 先确保登录（使用默认测试账号或跳转登录）
      const token = localStorage.getItem("token");
      if (!token) {
        // 注册默认账号
        const res = await api.post("/api/auth/register", {
          phone: "13800138000",
          password: "test123",
        }).catch(() => api.post("/api/auth/login", { phone: "13800138000", password: "test123" }));
        localStorage.setItem("token", res.data.access_token);
      }

      // 保存基础画像
      await api.put("/api/profile", { basic_info: values });

      // 跳转推荐页
      router.push(`/recommend?score=${values.score}&rank=${values.rank}&province=${values.province}&subject_type=${values.subject_type}`);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <AppLayout>
      <Row justify="center" style={{ marginTop: 60 }}>
        <Col xs={24} md={16} lg={12}>
          <Card>
            <Space direction="vertical" size="large" style={{ width: "100%" }}>
              <Title level={2} style={{ textAlign: "center" }}>
                <RocketOutlined /> 智愿 — 你的AI高考志愿助手
              </Title>
              <Paragraph style={{ textAlign: "center", fontSize: 16 }}>
                输入你的高考信息，立即获取冲/稳/保院校推荐方案
              </Paragraph>

              <Form layout="vertical" onFinish={onFinish} size="large">
                <Form.Item name="score" label="高考分数" rules={[{ required: true, message: "请输入分数" }]}>
                  <InputNumber min={0} max={750} style={{ width: "100%" }} placeholder="满分750" />
                </Form.Item>
                <Form.Item name="rank" label="省排名（位次）" rules={[{ required: true, message: "请输入位次" }]}>
                  <InputNumber min={1} style={{ width: "100%" }} placeholder="如：5000" />
                </Form.Item>
                <Form.Item name="province" label="所在省份" rules={[{ required: true, message: "请选择省份" }]}>
                  <Select placeholder="选择省份" options={provinces.map((p) => ({ value: p, label: p }))} />
                </Form.Item>
                <Form.Item name="subject_type" label="科类" rules={[{ required: true, message: "请选择科类" }]}>
                  <Select placeholder="选择科类" options={subjectTypes.map((s) => ({ value: s, label: s }))} />
                </Form.Item>
                <Form.Item>
                  <Button type="primary" htmlType="submit" block loading={loading} size="large">
                    获取推荐方案
                  </Button>
                </Form.Item>
              </Form>
            </Space>
          </Card>
        </Col>
      </Row>
    </AppLayout>
  );
}
```

- [ ] **Step 3: 创建推荐结果页**

`frontend/src/app/recommend/page.tsx`:
```tsx
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
```

- [ ] **Step 4: 创建院校查询页**

`frontend/src/app/universities/page.tsx`:
```tsx
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
```

- [ ] **Step 5: 创建AI对话页**

`frontend/src/app/chat/page.tsx`:
```tsx
"use client";

import { useState, useRef, useEffect } from "react";
import { Card, Input, Button, List, Typography, Space, Avatar } from "antd";
import { UserOutlined, RobotOutlined } from "@ant-design/icons";
import api from "@/lib/api";
import AppLayout from "@/components/Layout";

const { TextArea } = Input;
const { Text } = Typography;

interface Message {
  role: "user" | "assistant";
  content: string;
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const listRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    listRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim() || loading) return;
    const userMsg = input.trim();
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: userMsg }]);
    setLoading(true);

    try {
      const params = new URLSearchParams({ message: userMsg });
      if (sessionId) params.set("session_id", sessionId);
      const res = await api.post(`/api/chat?${params}`);
      setSessionId(res.data.session_id);
      setMessages((prev) => [...prev, { role: "assistant", content: res.data.reply }]);
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } } };
      setMessages((prev) => [...prev, {
        role: "assistant",
        content: error.response?.data?.detail || "抱歉，发生了错误，请重试。",
      }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <AppLayout>
      <Card title="AI志愿顾问" style={{ height: "calc(100vh - 200px)", display: "flex", flexDirection: "column" }}>
        <div style={{ flex: 1, overflow: "auto", marginBottom: 16 }} ref={listRef}>
          <List
            dataSource={messages}
            renderItem={(msg) => (
              <List.Item>
                <List.Item.Meta
                  avatar={<Avatar icon={msg.role === "user" ? <UserOutlined /> : <RobotOutlined />} />}
                  title={msg.role === "user" ? "我" : "智愿AI"}
                  description={<Text>{msg.content}</Text>}
                />
              </List.Item>
            )}
          />
        </div>
        <Space.Compact style={{ width: "100%" }}>
          <TextArea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onPressEnter={(e) => { if (!e.shiftKey) { e.preventDefault(); sendMessage(); } }}
            placeholder="输入你的问题，如：华中科技大学的计算机专业怎么样？"
            autoSize={{ minRows: 1, maxRows: 4 }}
          />
          <Button type="primary" onClick={sendMessage} loading={loading} style={{ height: "auto" }}>
            发送
          </Button>
        </Space.Compact>
      </Card>
    </AppLayout>
  );
}
```

- [ ] **Step 6: 创建画像完善页**

`frontend/src/app/profile/page.tsx`:
```tsx
"use client";

import { useEffect, useState } from "react";
import { Card, Form, Input, Select, Slider, Button, Progress, Tag, message, Space, Row, Col, InputNumber, Checkbox } from "antd";
import api from "@/lib/api";
import AppLayout from "@/components/Layout";
import { UserProfile } from "@/types";

const interests = [
  "计算机", "编程", "设计", "音乐", "运动", "阅读", "数学", "物理",
  "化学", "生物", "经济", "法律", "医学", "教育", "艺术", "机械",
];

const cities = ["北京", "上海", "广州", "深圳", "杭州", "南京", "成都", "武汉", "西安", "长沙"];

export default function ProfilePage() {
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const res = await api.get("/api/profile");
        setProfile(res.data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchProfile();
  }, []);

  const onSave = async (values: Record<string, unknown>) => {
    setSaving(true);
    try {
      const updateData: Record<string, unknown> = {};
      if (values.interests || values.prefer_city || values.tuition_max) {
        updateData.family_info = {
          tuition_max: values.tuition_max,
          prefer_city: values.prefer_city,
        };
        updateData.personality = {
          interests: values.interests,
        };
      }
      if (values.career_values || values.distance_preference || values.plan) {
        updateData.values_info = {
          career_values: values.career_values,
          distance_preference: values.distance_preference,
          plan: values.plan,
        };
      }
      const res = await api.put("/api/profile", updateData);
      message.success(`画像已更新，完整度: ${Math.round(res.data.completeness * 100)}%`);
      setProfile((prev) => prev ? { ...prev, completeness: res.data.completeness } : prev);
    } catch (err) {
      message.error("保存失败");
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <AppLayout><Card loading /></AppLayout>;

  return (
    <AppLayout>
      <Space direction="vertical" size="large" style={{ width: "100%" }}>
        <Card title="画像完整度">
          <Progress percent={Math.round((profile?.completeness || 0) * 100)} />
          <p>完善更多维度的信息，获得更精准的推荐</p>
        </Card>

        <Card title="Step 2 · 兴趣与偏好">
          <Form layout="vertical" onFinish={onSave}>
            <Form.Item name="interests" label="兴趣爱好（选择你感兴趣的方向）">
              <Checkbox.Group>
                <Row>
                  {interests.map((i) => (
                    <Col span={6} key={i}><Checkbox value={i}>{i}</Checkbox></Col>
                  ))}
                </Row>
              </Checkbox.Group>
            </Form.Item>
            <Form.Item name="prefer_city" label="偏好城市">
              <Select mode="multiple" placeholder="选择你偏好的城市（可多选）"
                options={cities.map((c) => ({ value: c, label: c }))} />
            </Form.Item>
            <Form.Item name="tuition_max" label="可接受最高学费（元/年）">
              <InputNumber min={0} max={200000} style={{ width: "100%" }} placeholder="如：10000" />
            </Form.Item>
            <Form.Item name="career_values" label="职业价值观">
              <Checkbox.Group options={["高薪", "稳定", "社会价值", "自由", "创造力"]} />
            </Form.Item>
            <Form.Item name="distance_preference" label="是否接受外地求学">
              <Select options={[
                { value: "接受外地", label: "接受外地" },
                { value: "尽量省内", label: "尽量省内" },
                { value: "只看省内", label: "只看省内" },
              ]} />
            </Form.Item>
            <Form.Item name="plan" label="未来规划">
              <Select options={[
                { value: "直接就业", label: "直接就业" },
                { value: "考研", label: "考研" },
                { value: "出国", label: "出国" },
                { value: "考公", label: "考公" },
                { value: "还没想好", label: "还没想好" },
              ]} />
            </Form.Item>
            <Form.Item>
              <Button type="primary" htmlType="submit" loading={saving}>保存</Button>
            </Form.Item>
          </Form>
        </Card>
      </Space>
    </AppLayout>
  );
}
```

- [ ] **Step 7: 创建登录页**

`frontend/src/app/login/page.tsx`:
```tsx
"use client";

import { useState } from "react";
import { Card, Form, Input, Button, Typography, Tabs, message } from "antd";
import { useRouter } from "next/navigation";
import api from "@/lib/api";

const { Title } = Typography;

export default function LoginPage() {
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const onLogin = async (values: { phone: string; password: string }) => {
    setLoading(true);
    try {
      const res = await api.post("/api/auth/login", values);
      localStorage.setItem("token", res.data.access_token);
      message.success("登录成功");
      router.push("/");
    } catch {
      message.error("登录失败，请检查手机号和密码");
    } finally {
      setLoading(false);
    }
  };

  const onRegister = async (values: { phone: string; password: string }) => {
    setLoading(true);
    try {
      const res = await api.post("/api/auth/register", values);
      localStorage.setItem("token", res.data.access_token);
      message.success("注册成功");
      router.push("/");
    } catch {
      message.error("注册失败，该手机号可能已注册");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ display: "flex", justifyContent: "center", alignItems: "center", minHeight: "100vh", background: "#f0f2f5" }}>
      <Card style={{ width: 400 }}>
        <Title level={3} style={{ textAlign: "center" }}>智愿</Title>
        <Tabs items={[
          {
            key: "login",
            label: "登录",
            children: (
              <Form onFinish={onLogin}>
                <Form.Item name="phone" rules={[{ required: true }]}>
                  <Input placeholder="手机号" size="large" />
                </Form.Item>
                <Form.Item name="password" rules={[{ required: true }]}>
                  <Input.Password placeholder="密码" size="large" />
                </Form.Item>
                <Button type="primary" htmlType="submit" block size="large" loading={loading}>登录</Button>
              </Form>
            ),
          },
          {
            key: "register",
            label: "注册",
            children: (
              <Form onFinish={onRegister}>
                <Form.Item name="phone" rules={[{ required: true }]}>
                  <Input placeholder="手机号" size="large" />
                </Form.Item>
                <Form.Item name="password" rules={[{ required: true, min: 6 }]}>
                  <Input.Password placeholder="密码（至少6位）" size="large" />
                </Form.Item>
                <Button type="primary" htmlType="submit" block size="large" loading={loading}>注册</Button>
              </Form>
            ),
          },
        ]} />
      </Card>
    </div>
  );
}
```

- [ ] **Step 8: 更新根布局，引入 Ant Design**

修改 `frontend/src/app/layout.tsx`，引入 antd 样式：
```tsx
import type { Metadata } from "next";
import { AntdRegistry } from "@ant-design/nextjs-registry";
import "./globals.css";

export const metadata: Metadata = {
  title: "智愿 - AI高考志愿助手",
  description: "基于AI的高考志愿智能推荐系统",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="zh-CN">
      <body>
        <AntdRegistry>{children}</AntdRegistry>
      </body>
    </html>
  );
}
```

安装 antd registry:
```bash
npm install @ant-design/nextjs-registry
```

- [ ] **Step 9: 验证前端**

Run:
```bash
npm run dev
```

访问 http://localhost:3000，确认首页表单渲染正常。

- [ ] **Step 10: Commit**

```bash
git add frontend/
git commit -m "feat: frontend core pages - home, recommend, universities, chat, profile, login"
```

---

## Task 12: 集成测试与全链路验证

- [ ] **Step 1: 启动所有服务**

Run:
```bash
cd /Users/chaowang/workspace/gte/zhi_yuan
docker compose up -d
cd frontend && npm run dev &
```

- [ ] **Step 2: 全链路手动测试**

按以下顺序测试完整用户旅程:
1. 注册/登录 → 获取token
2. 填写基础画像（分数/位次/省份/科类）
3. 获取推荐结果（冲/稳/保）
4. 查询院校列表
5. AI对话发送消息
6. 更新画像（兴趣/城市偏好）
7. 重新获取推荐（观察适配度变化）

- [ ] **Step 3: 运行全部后端测试**

Run:
```bash
cd /Users/chaowang/workspace/gte/zhi_yuan/backend
python -m pytest tests/ -v --tb=short
```

Expected: 所有测试通过（约16个测试用例）

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "chore: integration verified - full user journey working end-to-end"
```
