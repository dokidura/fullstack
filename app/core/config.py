# app/core/config.py
# Простой вариант настроек для MVP

class Settings:
    APP_NAME: str = "Electronic Exam Forms API"
    DEBUG: bool = True

    # JWT
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS / hosts (используется в main.py)
    ALLOWED_HOSTS: list = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
    ]

    # --- RBAC ---
    # "Администратор" в рамках этой лабораторной — это учитель,
    # чей email входит в белый список.
    # Роли в приложении при этом остаются только: student / teacher.
    ADMIN_EMAILS: list[str] = [
        # добавь сюда свой email, чтобы иметь доступ к админ-эндпоинтам
        "admin@mail.ru",
    ]


settings = Settings()
