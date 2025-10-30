from fastapi import APIRouter, HTTPException, status
from typing import List, Optional
from app.models.schemas import GradebookEntry, GradebookResponse

router = APIRouter(prefix="/gradebooks", tags=["gradebooks"])

# Временное хранилище
gradebooks_db = []
gradebook_id_counter = 1

@router.post("/", response_model=GradebookResponse)
async def create_gradebook_entry(entry: GradebookEntry):
    global gradebook_id_counter
    
    # Проверка существования submission (в реальном приложении)
    
    gradebook_entry = {
        "id": gradebook_id_counter,
        **entry.dict(),
        "created_at": "2024-01-01T00:00:00",
        "updated_at": "2024-01-01T00:00:00"
    }
    
    gradebooks_db.append(gradebook_entry)
    gradebook_id_counter += 1
    
    return gradebook_entry

@router.get("/", response_model=List[GradebookResponse])
async def get_gradebook_entries(
    exam_id: Optional[int] = None,
    student_id: Optional[int] = None
):
    filtered_entries = gradebooks_db
    
    if exam_id:
        filtered_entries = [e for e in filtered_entries if e["exam_id"] == exam_id]
    
    if student_id:
        filtered_entries = [e for e in filtered_entries if e["student_id"] == student_id]
    
    return filtered_entries

@router.get("/export/{exam_id}")
async def export_gradebook(exam_id: int):
    """
    Экспорт ведомости в CSV формате
    """
    entries = [e for e in gradebooks_db if e["exam_id"] == exam_id]
    
    if not entries:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ведомость не найдена"
        )
    
    # В реальном приложении генерировать CSV файл
    return {
        "message": f"Ведомость для экзамена {exam_id} готова к выгрузке",
        "entries_count": len(entries),
        "download_url": f"/api/v1/gradebooks/download/{exam_id}"
    }