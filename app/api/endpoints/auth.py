from fastapi import APIRouter, HTTPException, status
from datetime import datetime, timedelta
from typing import Dict, Any
from app.models.schemas import UserCreate, UserResponse, LoginRequest, Token
from app.core.security import verify_password, create_access_token, get_password_hash
from app.core.config import settings

router = APIRouter(prefix="/auth", tags=["authentication"])

# Временное хранилище (в реальном приложении использовать БД)
fake_users_db: Dict[str, Dict[str, Any]] = {}

@router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate):
    if user_data.email in fake_users_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким email уже существует"
        )
    
    # 🔐 Хешируем пароль перед сохранением!
    hashed_password = get_password_hash(user_data.password)
    
    # Создаём словарь пользователя
    user_dict = {
        "id": len(fake_users_db) + 1,
        "email": user_data.email,
        "full_name": user_data.full_name,
        "role": user_data.role,
        "hashed_password": hashed_password,
        "created_at": datetime.utcnow()
    }
    
    fake_users_db[user_data.email] = user_dict
    return user_dict

@router.post("/login", response_model=Token)
async def login(login_data: LoginRequest):
    user = fake_users_db.get(login_data.email)
    
    # 🔑 Правильная проверка пароля
    if not user or not verify_password(login_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверные учетные данные"
        )
    
    # Генерируем токен
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["email"]},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}