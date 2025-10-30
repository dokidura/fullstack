from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    STUDENT = "student"
    TEACHER = "teacher"
    ADMIN = "admin"

class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    role: UserRole

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class ExamFormSubmission(BaseModel):
    student_id: int
    exam_id: int
    form_data: Dict[str, Any]
    file_path: Optional[str] = None

class ExamFormResponse(ExamFormSubmission):
    id: int
    submission_date: datetime
    status: str
    ai_processed: bool = False
    
    class Config:
        from_attributes = True

class AIProcessingRequest(BaseModel):
    submission_id: int
    image_data: Optional[str] = None  # base64 encoded image

class AIProcessingResponse(BaseModel):
    submission_id: int
    processed_data: Dict[str, Any]
    confidence: float
    status: str

class GradebookEntry(BaseModel):
    student_id: int
    exam_id: int
    submission_id: int
    grade: Optional[float] = None
    comments: Optional[str] = None

class GradebookResponse(GradebookEntry):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class HealthCheck(BaseModel):
    status: str
    timestamp: datetime
    version: str
    database_status: Optional[str] = None
    ai_service_status: Optional[str] = None