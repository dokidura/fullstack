# app/core/config.py - ПРОСТОЙ РАБОЧИЙ ВАРИАНТ
class Settings:
    APP_NAME: str = "Electronic Exam Forms API"
    DEBUG: bool = True
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALLOWED_HOSTS: list = ["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:8000"]

settings = Settings()