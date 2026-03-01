from fastapi import APIRouter
from app.api.endpoints import auth, submissions, gradebooks, ai_processing
from app.utils.health_check import perform_health_check
from app.models.schemas import HealthCheck

api_router = APIRouter()

@api_router.get("/health", response_model=HealthCheck, tags=["health"])
async def health_check():
    return await perform_health_check()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(submissions.router, prefix="/submissions", tags=["submissions"])
api_router.include_router(ai_processing.router, prefix="/ai", tags=["ai"])
api_router.include_router(gradebooks.router, prefix="/gradebooks", tags=["gradebooks"])
