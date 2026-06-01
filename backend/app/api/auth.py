from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.user import UserRegister, UserLogin, PasswordChange, TokenResponse, UserInfo, RefreshRequest, LogoutRequest
from app.services.auth_service import AuthService

router = APIRouter(prefix="/api/auth", tags=["认证"])


@router.post("/register", response_model=TokenResponse)
async def register(data: UserRegister):
    return await AuthService().register(data.phone, data.password)


@router.post("/login", response_model=TokenResponse)
async def login(data: UserLogin):
    return await AuthService().login(data.phone, data.password)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(data: RefreshRequest):
    """用 refresh token 换取新的 access token 和 refresh token"""
    return await AuthService().refresh(data.refresh_token)


@router.post("/logout")
async def logout(data: LogoutRequest = LogoutRequest(), user: User = Depends(get_current_user)):
    """登出当前用户，吊销指定的 refresh token（或全部）"""
    await AuthService().logout(user.id, refresh_token_value=data.refresh_token)
    return {"message": "已成功登出"}


@router.get("/me", response_model=UserInfo)
async def get_me(user: User = Depends(get_current_user)):
    return user


@router.put("/password")
async def change_password(data: PasswordChange, user: User = Depends(get_current_user)):
    await AuthService().change_password(user.id, data.old_password, data.new_password)
    return {"message": "密码修改成功，请重新登录"}
