from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.routes import api_router
from app.core.user_store import init_user_store

app = FastAPI(
    title="Electronic Exam Forms API",
    description="API для системы электронных экзаменационных бланков",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔥 ВСЕ API ТЕПЕРЬ НА /api/v1
app.include_router(api_router, prefix="/api/v1")


@app.on_event("startup")
async def startup_event():
    # Создаёт app.db, таблицу users, сидит 4 пользователя (если пусто),
    # и загружает их в fake_users_db.
    init_user_store()


@app.get("/")
async def root():
    return {
        "message": "Добро пожаловать в систему электронных экзаменационных бланков",
        "version": "1.0.0",
        "docs": "/docs"
    }
