from fastapi import APIRouter, HTTPException, status, Depends
from datetime import timedelta
from pydantic import BaseModel

from app.models.schemas import UserCreate, UserResponse, LoginRequest, Token
from app.core.security import verify_password, create_access_token, get_password_hash
from app.core.config import settings
from app.core.deps import get_current_user, require_admin
from app.core.user_store import fake_users_db, create_user, update_user_role

router = APIRouter()


@router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate):
    # роли в проекте: только student / teacher
    if user_data.role not in ("student", "teacher"):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid role. Allowed: student | teacher",
        )

    if user_data.email in fake_users_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким email уже существует",
        )

    hashed_password = get_password_hash(user_data.password)

    try:
        user_dict = create_user(
            email=user_data.email,
            full_name=user_data.full_name,
            role=user_data.role,
            hashed_password=hashed_password,
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким email уже существует",
        )

    return user_dict


@router.post("/login", response_model=Token)
async def login(login_data: LoginRequest):
    user = fake_users_db.get(login_data.email)

    if not user or not verify_password(login_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверные учетные данные",
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["email"]},
        expires_delta=access_token_expires,
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
async def me(current_user: UserResponse = Depends(get_current_user)):
    return current_user


# ---- Admin endpoint (требование лабораторной) ----
class RoleUpdate(BaseModel):
    role: str  # "student" | "teacher"


@router.patch("/users/{user_id}/role", response_model=UserResponse)
async def set_user_role(
    user_id: int,
    payload: RoleUpdate,
    admin_user: UserResponse = Depends(require_admin()),
):
    # доступно только администратору (учитель + email в settings.ADMIN_EMAILS)
    if payload.role not in ("student", "teacher"):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid role. Allowed: student | teacher",
        )

    try:
        updated = update_user_role(user_id=user_id, new_role=payload.role)
    except ValueError:
        raise HTTPException(status_code=404, detail="User not found")

    return UserResponse(**updated)
