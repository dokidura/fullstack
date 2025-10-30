from fastapi import APIRouter, Depends, HTTPException, status
from app.models.schemas import UserCreate, UserResponse, LoginRequest, Token
from app.core.security import verify_password, create_access_token, get_password_hash

router = APIRouter(prefix="/auth", tags=["authentication"])

# Временное хранилище (в реальном приложении использовать БД)
fake_users_db = {}

@router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate):
    if user_data.email in fake_users_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким email уже существует"
        )
    
    # В реальном приложении хешировать пароль
    user_dict = user_data.dict()
    user_dict["id"] = len(fake_users_db) + 1
    user_dict["created_at"] = "2024-01-01T00:00:00"  # В реальности использовать datetime.now()
    
    fake_users_db[user_data.email] = user_dict
    return user_dict

@router.post("/login", response_model=Token)
async def login(login_data: LoginRequest):
    user = fake_users_db.get(login_data.email)
    if not user or not verify_password(login_data.password, get_password_hash(login_data.password)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверные учетные данные"
        )
    
    access_token = create_access_token(data={"sub": user["email"]})
    return {"access_token": access_token, "token_type": "bearer"}