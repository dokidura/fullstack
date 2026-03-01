from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import StreamingResponse
from typing import List, Optional
import csv
import io

from app.models.schemas import GradebookResponse, UserResponse
from app.core.deps import get_current_user, require_teacher

router = APIRouter()

# Временное хранилище
gradebooks_db = []
gradebook_id_counter = 1


@router.get("/", response_model=List[GradebookResponse])
async def get_gradebook_entries(
    exam_id: Optional[int] = None,
    student_id: Optional[int] = None,
    current_user: UserResponse = Depends(get_current_user),
):
    filtered_entries = gradebooks_db

    # student → только свои записи (и нельзя подставить чужой student_id)
    if current_user.role == "student":
        student_id = current_user.id

    if exam_id is not None:
        filtered_entries = [e for e in filtered_entries if e["exam_id"] == exam_id]

    if student_id is not None:
        filtered_entries = [e for e in filtered_entries if e["student_id"] == student_id]

    return filtered_entries


@router.get("/export/{exam_id}")
async def export_gradebook(
    exam_id: int,
    current_user: UserResponse = Depends(require_teacher()),
):
    # teacher-only
    entries = [e for e in gradebooks_db if e["exam_id"] == exam_id]

    if not entries:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ведомость не найдена",
        )

    output = io.StringIO()
    output.write("\ufeff")  # UTF-8 BOM для Excel
    writer = csv.writer(output)

    writer.writerow([
        "Работа",
        "Ученик",
        "Предмет",
        "Оценка",
        "Правильных ответов",
        "Всего вопросов",
        "Комментарий",
    ])

    for e in entries:
        processed = e.get("processed_data", {})
        writer.writerow([
            e.get("submission_id"),
            e.get("student_name"),
            e.get("exam_name"),
            e.get("grade"),
            processed.get("correct_answers"),
            processed.get("total_questions"),
            e.get("comments", ""),
        ])

    output.seek(0)

    filename = f"gradebook_exam_{exam_id}.csv"

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
