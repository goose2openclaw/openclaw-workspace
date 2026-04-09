#!/usr/bin/env python3
"""
🪿 GO2SE 认证API
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from app.core.database import get_db
from app.models.models import User
from app.auth.auth import AuthService, get_current_active_user

router = APIRouter(prefix="/auth", tags=["认证"])


class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    vip_level: str
    status: str
    created_at: str


@router.post("/register", response_model=UserResponse)
async def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """用户注册"""
    try:
        user = AuthService.register(db, request.username, request.email, request.password)
        return UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            vip_level=user.vip_level,
            status=user.status,
            created_at=user.created_at.isoformat()
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login", response_model=LoginResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """用户登录"""
    try:
        result = AuthService.login(db, form_data.username, form_data.password)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_active_user)):
    """退出登录"""
    return {"message": "退出成功"}


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_active_user)):
    """获取当前用户信息"""
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        vip_level=current_user.vip_level,
        status=current_user.status,
        created_at=current_user.created_at.isoformat()
    )


@router.post("/change-password")
async def change_password(
    old_password: str,
    new_password: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """修改密码"""
    success = AuthService.change_password(db, current_user, old_password, new_password)
    if success:
        return {"message": "密码修改成功"}
    raise HTTPException(status_code=400, detail="密码修改失败")
