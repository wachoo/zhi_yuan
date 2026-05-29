from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.user import UserRegister, UserLogin, TokenResponse, UserInfo
from app.services.auth_service import AuthService

router = APIRouter(prefix="/api/auth", tags=["认证"])


@router.post("/register", response_model=TokenResponse)
async def register(data: UserRegister):
    return await AuthService().register(data.phone, data.password)


@router.post("/login", response_model=TokenResponse)
async def login(data: UserLogin):
    return await AuthService().login(data.phone, data.password)


@router.get("/me", response_model=UserInfo)
async def get_me(user: User = Depends(get_current_user)):
    return user
