import uuid

import bcrypt
from fastapi import HTTPException
from jose import jwt
from datetime import datetime, timedelta

from app.config import get_settings
from app.dao.user import UserDAO
from app.dao.profile import ProfileDAO
from app.models.user import User, UserProfile

settings = get_settings()


def _hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def _verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


def _create_access_token(user_id: uuid.UUID) -> str:
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": str(user_id), "exp": expire}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


class AuthService:
    """认证相关业务：注册、登录"""

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

        token = _create_access_token(user.id)
        return {"access_token": token, "user_id": user.id}

    async def login(self, phone: str, password: str) -> dict:
        user = await UserDAO().get_by_phone(phone)
        if not user or not _verify_password(password, user.password_hash):
            raise HTTPException(status_code=401, detail="手机号或密码错误")

        token = _create_access_token(user.id)
        return {"access_token": token, "user_id": user.id}
