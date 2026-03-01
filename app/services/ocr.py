import pytesseract
import cv2
import os

# ⚠️ если Windows не видит tesseract — раскомментируй
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def recognize_text(image_path: str) -> str:
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"File not found: {image_path}")

    image = cv2.imread(image_path)
    if image is None:
        raise ValueError("Cannot read image")

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)[1]

    text = pytesseract.image_to_string(
        gray,
        lang="rus+eng",
        config="--psm 6"
    )

    return text.strip()
