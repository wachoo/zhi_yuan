import uuid
import secrets

import bcrypt
from fastapi import HTTPException
from jose import jwt
from datetime import datetime, timedelta, timezone

from app.config import get_settings
from app.dao.user import UserDAO
from app.dao.profile import ProfileDAO
from app.dao.refresh_token import RefreshTokenDAO
from app.models.user import User, UserProfile

settings = get_settings()


def _hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def _verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


def _create_access_token(user_id: uuid.UUID) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": str(user_id), "exp": expire, "type": "access"}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def _create_refresh_token_value() -> str:
    """生成一个不可预测的 refresh token 字符串"""
    return secrets.token_urlsafe(48)


class AuthService:
    """认证相关业务：注册、登录、修改密码、刷新令牌、登出"""

    async def register(self, phone: str, password: str) -> dict:
        existing = await UserDAO().get_by_phone(phone)
        if existing:
            raise HTTPException(status_code=400, detail="该手机号已注册")

        user = User(
            id=uuid.uuid4(),
            phone=phone,
            password_hash=_hash_password(password),
        )
        await UserDAO().create_user(user)

        profile = UserProfile(id=uuid.uuid4(), user_id=user.id)
        await ProfileDAO().create_profile(profile)

        access_token = _create_access_token(user.id)
        refresh_token_value = _create_refresh_token_value()
        expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        await RefreshTokenDAO().create(user.id, refresh_token_value, expires_at)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token_value,
            "user_id": user.id,
        }

    async def login(self, phone: str, password: str) -> dict:
        user = await UserDAO().get_by_phone(phone)
        if not user or not _verify_password(password, user.password_hash):
            raise HTTPException(status_code=401, detail="手机号或密码错误")

        # 登录时清理旧过期 token
        await RefreshTokenDAO().cleanup_expired(user.id)

        access_token = _create_access_token(user.id)
        refresh_token_value = _create_refresh_token_value()
        expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        await RefreshTokenDAO().create(user.id, refresh_token_value, expires_at)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token_value,
            "user_id": user.id,
        }

    async def refresh(self, refresh_token_value: str) -> dict:
        """用 refresh token 换取新的 access + refresh token（轮换模式）"""
        rt_dao = RefreshTokenDAO()
        rt = await rt_dao.get_by_token(refresh_token_value)

        if not rt:
            raise HTTPException(status_code=401, detail="无效的 refresh token")

        if rt.revoked:
            # 检测到已被吊销的 token 被使用 → 可能是盗用，吊销该用户全部 token
            await rt_dao.revoke_all_for_user(rt.user_id)
            raise HTTPException(status_code=401, detail="refresh token 已被吊销，请重新登录")

        if rt.expires_at < datetime.now(timezone.utc):
            raise HTTPException(status_code=401, detail="refresh token 已过期，请重新登录")

        # 轮换：吊销旧 refresh token，发一个新的
        if settings.REFRESH_TOKEN_ROTATION:
            await rt_dao.revoke(refresh_token_value)

        # 验证用户仍然存在
        user = await UserDAO().get_by_id(rt.user_id)
        if not user:
            raise HTTPException(status_code=401, detail="用户不存在")

        new_access = _create_access_token(user.id)
        new_refresh = _create_refresh_token_value()
        new_expires = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        await rt_dao.create(user.id, new_refresh, new_expires)

        return {
            "access_token": new_access,
            "refresh_token": new_refresh,
            "user_id": user.id,
        }

    async def logout(self, user_id: uuid.UUID, refresh_token_value: str | None = None) -> None:
        """登出：吊销当前 refresh token，或全部"""
        rt_dao = RefreshTokenDAO()
        if refresh_token_value:
            await rt_dao.revoke(refresh_token_value)
        else:
            # 无 refresh token 时吊销全部
            await rt_dao.revoke_all_for_user(user_id)

    async def change_password(self, user_id: uuid.UUID, old_password: str, new_password: str):
        user = await UserDAO().get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        if not _verify_password(old_password, user.password_hash):
            raise HTTPException(status_code=400, detail="原密码错误")
        await UserDAO().update_password(user_id, _hash_password(new_password))
        # 修改密码后吊销所有 refresh token，强制重新登录
        await RefreshTokenDAO().revoke_all_for_user(user_id)
