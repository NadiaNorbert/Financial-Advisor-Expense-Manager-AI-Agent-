"""
backend/app/api/v1/auth.py
==========================
Authentication endpoints: register, login, profile, password change.
"""

from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException, status

from backend.app.schemas.all_schemas import (
    UserRegister,
    UserLogin,
    UserOut,
    Token,
    PasswordUpdate,
)
from backend.app.core.security import (
    create_access_token,
    get_current_user,
)
from backend.auth import (
    register_user,
    login_user,
    update_password,
    get_user_by_id,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=Token)
def register(data: UserRegister):
    res = register_user(data.username, data.email, data.password)
    if not res["success"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=res["message"])
    
    user_id = res["user_id"]
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="User creation error")
    
    access_token = create_access_token(data={"sub": str(user_id), "username": user["username"]})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user,
    }


@router.post("/login", response_model=Token)
def login(data: UserLogin):
    res = login_user(data.username, data.password)
    if not res["success"]:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=res["message"])
    
    user_id = res["user_id"]
    user = get_user_by_id(user_id)
    access_token = create_access_token(data={"sub": str(user_id), "username": user["username"]})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user,
    }


@router.get("/me", response_model=UserOut)
def get_me(current_user: dict = Depends(get_current_user)):
    return current_user


@router.post("/change-password")
def change_password(
    data: PasswordUpdate,
    current_user: dict = Depends(get_current_user),
):
    res = update_password(current_user["id"], data.old_password, data.new_password)
    if not res["success"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=res["message"])
    return {"success": True, "message": res["message"]}
