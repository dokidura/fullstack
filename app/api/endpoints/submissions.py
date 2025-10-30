from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status
from typing import List, Optional
from app.models.schemas import ExamFormSubmission, ExamFormResponse

router = APIRouter(prefix="/submissions", tags=["submissions"])

# Временное хранилище
submissions_db = []
submission_id_counter = 1

@router.post("/", response_model=ExamFormResponse)
async def create_submission(
    student_id: int = Form(...),
    exam_id: int = Form(...),
    form_data: str = Form(...),  # JSON string
    file: Optional[UploadFile] = File(None)
):
    global submission_id_counter
    
    # В реальном приложении парсить form_data и сохранять файл
    submission = {
        "id": submission_id_counter,
        "student_id": student_id,
        "exam_id": exam_id,
        "form_data": {"parsed": "form_data"},  # В реальности парсить JSON
        "file_path": f"uploads/{file.filename}" if file else None,
        "submission_date": "2024-01-01T00:00:00",
        "status": "submitted",
        "ai_processed": False
    }
    
    submissions_db.append(submission)
    submission_id_counter += 1
    
    return submission

@router.get("/", response_model=List[ExamFormResponse])
async def get_submissions(
    student_id: Optional[int] = None,
    exam_id: Optional[int] = None
):
    filtered_submissions = submissions_db
    
    if student_id:
        filtered_submissions = [s for s in filtered_submissions if s["student_id"] == student_id]
    
    if exam_id:
        filtered_submissions = [s for s in filtered_submissions if s["exam_id"] == exam_id]
    
    return filtered_submissions

@router.get("/{submission_id}", response_model=ExamFormResponse)
async def get_submission(submission_id: int):
    submission = next((s for s in submissions_db if s["id"] == submission_id), None)
    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Работа не найдена"
        )
    return submission