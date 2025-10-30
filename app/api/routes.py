from fastapi import APIRouter
from app.api.endpoints import auth, submissions, gradebooks, ai_processing
from app.utils.health_check import perform_health_check
from app.models.schemas import HealthCheck

api_router = APIRouter()

# Health check endpoint
@api_router.get("/health", response_model=HealthCheck, tags=["health"])
async def health_check():
    return await perform_health_check()

# Include all endpoint routers
api_router.include_router(auth.router)
api_router.include_router(submissions.router)
api_router.include_router(gradebooks.router)
api_router.include_router(ai_processing.router)