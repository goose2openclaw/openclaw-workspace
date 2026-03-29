#!/usr/bin/env python3
"""
🪿 API认证工具
"""
import hashlib
import secrets
import uuid
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import User

security = HTTPBearer(auto_error=False)


def generate_api_key() -> tuple[str, str, str]:
    """生成API密钥
    Returns: (full_key, prefix, hashed)
    """
    raw = str(uuid.uuid4()).replace("-", "") + secrets.token_hex(16)
    key = f"GO2SE_{raw[:48]}"
    prefix = key[:16]
    hashed = hashlib.sha256(key.encode()).hexdigest()
    return key, prefix, hashed


def hash_key(key: str) -> str:
    return hashlib.sha256(key.encode()).hexdigest()


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """可选认证 - 不强制要求登录"""
    if not credentials:
        return None
    if credentials.scheme.lower() != "bearer":
        return None
    hashed = hash_key(credentials.credentials)
    user = db.query(User).filter(User.hashed_api_key == hashed, User.is_active == True).first()
    return user


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """强制认证"""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未提供API密钥",
            headers={"WWW-Authenticate": "Bearer"}
        )
    if credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证方式",
            headers={"WWW-Authenticate": "Bearer"}
        )
    hashed = hash_key(credentials.credentials)
    user = db.query(User).filter(User.hashed_api_key == hashed, User.is_active == True).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效或已停用的API密钥",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return user
