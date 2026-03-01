import re
from app.services.answers import CORRECT_ANSWERS, EXPECTED_QUESTIONS_COUNT

def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower().strip())

def parse_answers(text: str):
    answers = []

    for line in text.splitlines():
        match = re.match(
            r"^\s*(\d+)\s*[\.\-\)]?\s*(.+)$",
            line
        )
        if not match:
            continue

        q_num = int(match.group(1))
        recognized = match.group(2).strip()

        if q_num not in CORRECT_ANSWERS:
            continue

        correct = CORRECT_ANSWERS[q_num]
        is_correct = normalize(recognized) == normalize(correct)

        answers.append({
            "questionNumber": q_num,
            "recognizedText": recognized,
            "correctAnswer": correct,
            "isCorrect": is_correct,
            "confidence": 0.9
        })

    return answers
