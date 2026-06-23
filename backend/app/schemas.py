from pydantic import BaseModel
from typing import List, Optional, Any
from datetime import datetime

class ObservationBase(BaseModel):
    category: str
    content: str

class ObservationResponse(ObservationBase):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True

class StudentBase(BaseModel):
    name: str
    course: str
    level: str
    notes: Optional[str] = None

class StudentResponse(StudentBase):
    id: int
    created_at: datetime
    observations: List[ObservationResponse] = []
    class Config:
        from_attributes = True

class FormField(BaseModel):
    fieldId: str
    type: str
    label: str
    placeholder: Optional[str] = None
    ariaLabel: Optional[str] = None
    nearbyText: Optional[str] = None
    options: Optional[List[str]] = []
    required: bool = False
    selector: Optional[str] = None

class FormAnalyzeRequest(BaseModel):
    fields: List[FormField]

class FormAnalyzeResponseField(BaseModel):
    fieldId: str
    normalizedLabel: str
    normalizedType: str
    options: List[str]
    required: bool
    confidence: float
    warnings: List[str] = []

class FormAnalyzeResponse(BaseModel):
    fields: List[FormAnalyzeResponseField]

class FormGenerateRequest(BaseModel):
    fields: List[FormAnalyzeResponseField]
    student_id: int
    url: str
    page_title: str
    context: Optional[str] = None

class GeneratedAnswer(BaseModel):
    fieldId: str
    answer: Any
    confidence: float
    source: str
    explanation: str

class FormGenerateResponse(BaseModel):
    answers: List[GeneratedAnswer]

class HistoryCreate(BaseModel):
    url: str
    page_title: str
    student_id: int
    detected_fields_json: str
    generated_answers_json: str
