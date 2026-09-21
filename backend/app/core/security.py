"""
backend/app/core/security.py
============================
JWT token generation, verification, and authentication dependencies.
"""

from __future__ import annotations
from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
import bcrypt

from backend.app.core.config import settings
from backend.auth import get_user_by_id

security_scheme = HTTPBearer(auto_error=False)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())
    except Exception:
        return False


def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def get_current_user_optional(
    token_auth: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
) -> Optional[dict]:
    """Return user dict if valid bearer token provided, else None."""
    if not token_auth:
        return None
    try:
        payload = jwt.decode(
            token_auth.credentials,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        user_id_str = payload.get("sub")
        if not user_id_str:
            return None
        user = get_user_by_id(int(user_id_str))
        return user
    except (JWTError, ValueError, Exception):
        return None


def get_current_user(
    token_auth: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
) -> dict:
    """Enforce authentication; raise 401 if missing or invalid token."""
    user = get_current_user_optional(token_auth)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials or token expired.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user
