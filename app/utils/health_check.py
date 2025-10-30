from datetime import datetime
from app.models.schemas import HealthCheck

async def perform_health_check() -> HealthCheck:
    """
    Выполняет комплексную проверку здоровья системы
    """
    health_status = "healthy"
    
    # Здесь можно добавить проверки различных сервисов
    database_status = "connected"  # В реальности проверять подключение к БД
    ai_service_status = "available"  # В реальности проверять доступность AI сервиса
    
    # Если какие-то сервисы недоступны, меняем статус
    if database_status != "connected" or ai_service_status != "available":
        health_status = "degraded"
    
    return HealthCheck(
        status=health_status,
        timestamp=datetime.now(),
        version="1.0.0",
        database_status=database_status,
        ai_service_status=ai_service_status
    )