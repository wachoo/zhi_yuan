import os
from functools import lru_cache
from pathlib import Path

from dotenv import dotenv_values
from pydantic_settings import BaseSettings, SettingsConfigDict

# backend/ 目录的绝对路径
_BASE_DIR = Path(__file__).resolve().parent.parent

# 环境配置文件映射
_ENV_FILES = {
    "local": ".env.local",
    "dev": ".env.dev",
    "test": ".env.test",
    "prod": ".env.prod",
}


def _resolve_app_env() -> str:
    """确定当前环境：优先读系统环境变量 APP_ENV，其次读 .env 中的 APP_ENV"""
    app_env = os.getenv("APP_ENV")
    if app_env:
        return app_env

    base_env = _BASE_DIR / ".env"
    if base_env.exists():
        values = dotenv_values(base_env)
        return values.get("APP_ENV", "local")

    return "local"


class Settings(BaseSettings):
    # App
    APP_ENV: str = "local"
    APP_NAME: str = "智愿"
    DEBUG: bool = True

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

    model_config = SettingsConfigDict(extra="ignore")


@lru_cache()
def get_settings() -> Settings:
    app_env = _resolve_app_env()
    env_filename = _ENV_FILES.get(app_env, ".env.local")
    # 使用绝对路径，避免受 CWD 影响
    env_files = (
        str(_BASE_DIR / ".env"),
        str(_BASE_DIR / env_filename),
    )
    return Settings(
        APP_ENV=app_env,
        _env_file=env_files,  # 基础配置兜底，环境文件覆盖
    )