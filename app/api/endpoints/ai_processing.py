from fastapi import APIRouter, HTTPException, status, BackgroundTasks
from app.models.schemas import AIProcessingRequest, AIProcessingResponse

router = APIRouter(prefix="/ai", tags=["ai_processing"])

# Временное хранилище для результатов AI обработки
ai_results_db = []

async def mock_ai_processing(submission_id: int, image_data: str = None):
    """
    Заглушка для AI обработки рукописного текста
    В реальном приложении здесь будет интеграция с ML моделью
    """
    # Имитация обработки
    import time
    time.sleep(2)
    
    result = {
        "submission_id": submission_id,
        "processed_data": {
            "student_name": "Иванов Иван",
            "student_id": "12345",
            "answers": {
                "q1": "42",
                "q2": "Теорема Пифагора",
                "q3": "Синус угла"
            }
        },
        "confidence": 0.85,
        "status": "completed"
    }
    
    ai_results_db.append(result)
    return result

@router.post("/process", response_model=AIProcessingResponse)
async def process_submission(
    request: AIProcessingRequest,
    background_tasks: BackgroundTasks
):
    # Проверка существования submission (в реальном приложении)
    
    # Запускаем обработку в фоне
    background_tasks.add_task(mock_ai_processing, request.submission_id, request.image_data)
    
    return {
        "submission_id": request.submission_id,
        "processed_data": {},
        "confidence": 0.0,
        "status": "processing"
    }

@router.get("/results/{submission_id}", response_model=AIProcessingResponse)
async def get_processing_result(submission_id: int):
    result = next((r for r in ai_results_db if r["submission_id"] == submission_id), None)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Результаты обработки не найдены"
        )
    return result