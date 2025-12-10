from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status, Depends
from typing import List, Optional
import json
from datetime import datetime
from app.models.schemas import ExamFormSubmission, ExamFormResponse, UserResponse
from app.core.deps import get_current_user, require_role

router = APIRouter(prefix="/submissions", tags=["submissions"])

# Временное хранилище (оставляем — для MVP подойдёт)
submissions_db = []
submission_id_counter = 1

# Вспомогательная функция для поиска работы по ID
def get_submission_by_id(submission_id: int):
    return next((s for s in submissions_db if s["id"] == submission_id), None)

# --- CREATE ---
@router.post("/", response_model=ExamFormResponse)
async def create_submission(
    student_id: int = Form(...),
    exam_id: int = Form(...),
    file: UploadFile = File(...),
    current_user: UserResponse = Depends(require_role("student"))
):
    global submission_id_counter

    # Студент может отправлять работу только от своего имени
    if current_user.id != student_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only submit exams for yourself"
        )

    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Файл не загружен или имеет пустое имя"
        )

    file_path = f"uploads/{file.filename}"

    submission = {
        "id": submission_id_counter,
        "student_id": student_id,
        "exam_id": exam_id,
        "form_data": {},
        "file_path": file_path,
        "submission_date": datetime.utcnow(),
        "status": "submitted",
        "ai_processed": False,
        "updated_at": None
    }

    submissions_db.append(submission)
    submission_id_counter += 1
    return submission

# --- READ all ---
@router.get("/", response_model=List[ExamFormResponse])
async def get_submissions(
    exam_id: Optional[int] = None,
    current_user: UserResponse = Depends(get_current_user)
):
    result = submissions_db

    if current_user.role == "student":
        # Студент видит только свои работы
        result = [s for s in result if s["student_id"] == current_user.id]
    elif current_user.role == "teacher":
        # Преподаватель видит работы по конкретному экзамену (если указан)
        if exam_id is not None:
            result = [s for s in result if s["exam_id"] == exam_id]
        else:
            result = []  # Без указания exam_id — не показываем ничего
    # Админ видит всё

    return result

# --- READ one ---
@router.get("/{submission_id}", response_model=ExamFormResponse)
async def get_submission(
    submission_id: int,
    current_user: UserResponse = Depends(get_current_user)
):
    submission = get_submission_by_id(submission_id)
    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Работа не найдена"
        )

    # Проверка доступа
    if current_user.role == "student" and submission["student_id"] != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own submissions"
        )
    # Преподаватель и админ могут смотреть любую работу (в MVP)

    return submission

# --- UPDATE (PUT) ---
@router.put("/{submission_id}", response_model=ExamFormResponse)
async def update_submission(
    submission_id: int,
    form_data: Optional[str] = Form(None),
    status: Optional[str] = Form(None),
    ai_processed: Optional[bool] = Form(None),
    current_user: UserResponse = Depends(require_role("teacher"))  # или "admin"
):
    submission = get_submission_by_id(submission_id)
    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Работа не найдена"
        )

    # Обновляем только допустимые поля
    if form_data is not None:
        try:
            submission["form_data"] = json.loads(form_data)
        except json.JSONDecodeError as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid form_data JSON: {str(e)}"
            )
    if status is not None:
        submission["status"] = status
    if ai_processed is not None:
        submission["ai_processed"] = ai_processed

    submission["updated_at"] = datetime.utcnow()
    return submission

# --- DELETE ---
@router.delete("/{submission_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_submission(
    submission_id: int,
    current_user: UserResponse = Depends(require_role("admin"))
):
    global submissions_db
    submission = get_submission_by_id(submission_id)
    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Работа не найдена"
        )
    submissions_db = [s for s in submissions_db if s["id"] != submission_id]
    return