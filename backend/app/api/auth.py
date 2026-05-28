import uuid
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from jose import jwt
import bcrypt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.config import get_settings
from app.models.user import User, UserProfile
from app.schemas.user import UserRegister, UserLogin, TokenResponse, UserInfo
from app.api.deps import get_current_user

router = APIRouter(prefix="/api/auth", tags=["认证"])
settings = get_settings()


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


def create_access_token(user_id: uuid.UUID) -> str:
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": str(user_id), "exp": expire}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


@router.post("/register", response_model=TokenResponse)
async def register(data: UserRegister, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.phone == data.phone))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="该手机号已注册")

    user = User(
        id=uuid.uuid4(),
        phone=data.phone,
        password_hash=hash_password(data.password),
    )
    db.add(user)

    profile = UserProfile(id=uuid.uuid4(), user_id=user.id)
    db.add(profile)

    await db.flush()
    token = create_access_token(user.id)
    return TokenResponse(access_token=token, user_id=user.id)


@router.post("/login", response_model=TokenResponse)
async def login(data: UserLogin, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.phone == data.phone))
    user = result.scalar_one_or_none()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="手机号或密码错误")

    token = create_access_token(user.id)
    return TokenResponse(access_token=token, user_id=user.id)


@router.get("/me", response_model=UserInfo)
async def get_me(user: User = Depends(get_current_user)):
    return user
