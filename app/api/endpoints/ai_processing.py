from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from datetime import datetime

from app.models.schemas import AIProcessingRequest, AIProcessingResponse, UserResponse
from app.services.ocr import recognize_text
from app.services.parser import parse_answers
from app.api.endpoints.gradebooks import gradebooks_db
from app.api.endpoints.submissions import submissions_db
from app.core.user_store import fake_users_db
from app.services.exams import EXAMS
from app.services.answers import EXPECTED_QUESTIONS_COUNT
from app.core.deps import get_current_user, require_teacher

router = APIRouter()

# Временное хранилище результатов AI
ai_results_db = []


def get_submission_by_id(submission_id: int):
    return next((s for s in submissions_db if s["id"] == submission_id), None)


def get_student_name(student_id: int) -> str:
    user = next((u for u in fake_users_db.values() if u["id"] == student_id), None)
    return user["full_name"] if user else f"ID {student_id}"


async def ai_processing(submission_id: int):
    submission = get_submission_by_id(submission_id)
    if not submission:
        return

    try:
        # 1️⃣ OCR
        text = recognize_text(submission["file_path"])

        # 2️⃣ Парсинг
        answers = parse_answers(text)

        correct = sum(1 for a in answers if a["isCorrect"])
        total = len(answers)

        # ❗ строгая проверка количества ответов
        if total != EXPECTED_QUESTIONS_COUNT:
            error_message = f"Найдено ответов: {total}, ожидалось: {EXPECTED_QUESTIONS_COUNT}"

            processed_data = {
                "answers": answers,
                "correct_answers": correct,
                "total_questions": total,
                "grade": 0,
                "error": error_message,
            }

            submission["status"] = "error"
            submission["processed_data"] = processed_data
            submission["updated_at"] = datetime.utcnow()

            # сохраняем в ведомость как ошибку (если ещё нет записи)
            if not any(g["submission_id"] == submission_id for g in gradebooks_db):
                student_name = get_student_name(submission["student_id"])
                exam_name = EXAMS.get(submission["exam_id"], f"Экзамен {submission['exam_id']}")

                gradebooks_db.append({
                    "id": len(gradebooks_db) + 1,
                    "submission_id": submission_id,
                    "student_id": submission["student_id"],
                    "student_name": student_name,
                    "exam_id": submission["exam_id"],
                    "exam_name": exam_name,
                    "grade": 0,
                    "comments": error_message,
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow(),
                    "processed_data": processed_data,
                })

            ai_results_db.append({
                "submission_id": submission_id,
                "processed_data": processed_data,
                "confidence": 0.0,
                "status": "error",
            })
            return

        # ✅ если бланк валиден — считаем оценку
        grade = 5 if correct == total else 4 if correct >= total * 0.7 else 3

        processed_data = {
            "answers": answers,
            "correct_answers": correct,
            "total_questions": total,
            "grade": grade,
        }

        # 3️⃣ Обновляем submission
        submission["status"] = "processed"
        submission["ai_processed"] = True
        submission["processed_data"] = processed_data
        submission["updated_at"] = datetime.utcnow()

        # 4️⃣ Создаём запись ведомости
        if not any(g["submission_id"] == submission_id for g in gradebooks_db):
            student_name = get_student_name(submission["student_id"])
            exam_name = EXAMS.get(submission["exam_id"], f"Экзамен {submission['exam_id']}")

            gradebooks_db.append({
                "id": len(gradebooks_db) + 1,
                "submission_id": submission_id,
                "student_id": submission["student_id"],
                "student_name": student_name,
                "exam_id": submission["exam_id"],
                "exam_name": exam_name,
                "grade": grade,
                "comments": "Оценка выставлена автоматически (OCR)",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "processed_data": processed_data,
            })

        ai_results_db.append({
            "submission_id": submission_id,
            "processed_data": processed_data,
            "confidence": 0.9,
            "status": "processed",
        })

    except Exception:
        submission["status"] = "error"
        submission["updated_at"] = datetime.utcnow()
        ai_results_db.append({
            "submission_id": submission_id,
            "processed_data": {},
            "confidence": 0.0,
            "status": "error",
        })


@router.post("/process", response_model=AIProcessingResponse)
async def process_submission(
    request: AIProcessingRequest,
    background_tasks: BackgroundTasks,
    current_user: UserResponse = Depends(require_teacher()),
):
    # teacher-only
    submission = get_submission_by_id(request.submission_id)
    if not submission:
        raise HTTPException(status_code=404, detail="Работа не найдена")

    if submission["status"] in ("processing", "processed"):
        return {
            "submission_id": request.submission_id,
            "processed_data": {},
            "confidence": 0.0,
            "status": submission["status"],
        }

    submission["status"] = "processing"
    submission["updated_at"] = datetime.utcnow()

    background_tasks.add_task(ai_processing, request.submission_id)

    return {
        "submission_id": request.submission_id,
        "processed_data": {},
        "confidence": 0.0,
        "status": "processing",
    }


@router.get("/results/{submission_id}", response_model=AIProcessingResponse)
async def get_processing_result(
    submission_id: int,
    current_user: UserResponse = Depends(get_current_user),
):
    # student → только свои результаты
    submission = get_submission_by_id(submission_id)
    if not submission:
        raise HTTPException(status_code=404, detail="Работа не найдена")

    if current_user.role == "student" and submission["student_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="You can only view your own results")

    result = next((r for r in ai_results_db if r["submission_id"] == submission_id), None)

    if not result:
        # если ещё в процессе
        if submission.get("status") == "processing":
            return {
                "submission_id": submission_id,
                "processed_data": {},
                "confidence": 0.0,
                "status": "processing",
            }

        raise HTTPException(status_code=404, detail="Результаты обработки не найдены")

    return result
