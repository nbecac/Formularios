from pydantic import BaseModel, Field
from typing import List, Optional, Any
from datetime import datetime

class ObservationBase(BaseModel):
    """
    Modelo base para Observaciones de estudiantes.
    Categorías soportadas: 'académico', 'comportamiento', 'apoyo', 'general'.
    """
    category: str = Field(..., description="Categoría de la observación")
    content: str = Field(..., description="Texto libre con el detalle")

class ObservationCreate(ObservationBase):
    """
    Datos para crear una nueva observación.
    """
    pass

class ObservationUpdate(BaseModel):
    """
    Datos para actualizar una observación existente.
    """
    category: Optional[str] = None
    content: Optional[str] = None

class ObservationResponse(ObservationBase):
    """
    Modelo de respuesta de Observaciones.
    """
    id: int
    created_at: datetime
    class Config:
        from_attributes = True

class StudentBase(BaseModel):
    """
    Datos base del alumno.
    """
    name: str = Field(..., description="Nombre completo")
    course: str = Field(..., description="Curso actual, ej: 4to Básico")
    level: str = Field(..., description="Nivel educativo, ej: Básica")
    notes: Optional[str] = Field(None, description="Notas breves o descriptivas")

class StudentCreate(StudentBase):
    """
    Datos para crear un alumno.
    """
    pass

class StudentUpdate(BaseModel):
    """
    Datos para actualizar un alumno de forma parcial.
    """
    name: Optional[str] = None
    course: Optional[str] = None
    level: Optional[str] = None
    notes: Optional[str] = None

class StudentResponse(StudentBase):
    """
    Respuesta básica de alumno, sin cargar observaciones.
    """
    id: int
    created_at: datetime
    class Config:
        from_attributes = True

class StudentDetail(StudentResponse):
    """
    Detalle completo de alumno, incluyendo sus observaciones en lista.
    """
    observations: List[ObservationResponse] = []

class FormField(BaseModel):
    """
    Estructura de campo reportada por la extensión (contentScript).
    """
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
    """
    Estructura de la sugerencia de IA a devolver a la extensión.
    """
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

class ImportCsvError(BaseModel):
    row_index: int
    error: str

class ImportSummaryResponse(BaseModel):
    alumnos_creados: int
    alumnos_actualizados: int
    observaciones_creadas: int
    errores: List[ImportCsvError]

class AITestRequest(BaseModel):
    student_id: Optional[int] = None
    text: Optional[str] = None
    provider: Optional[str] = None

class AITestResponse(BaseModel):
    provider: str
    answer: str
    fallback: bool
    error: Optional[str] = None

class KnowledgeImportSummary(BaseModel):
    fuentes_importadas: int
    chunks_creados: int
    archivos_omitidos: int
    errores: List[str]

class KnowledgeSearchRequest(BaseModel):
    query: str
    max_results: Optional[int] = 5
    preferred_sections: Optional[List[str]] = None

class KnowledgeSourceSnippet(BaseModel):
    section: str
    title: str
    filename: str
    snippet: str

class CanvasQuestionRequest(BaseModel):
    question: str
    options: Optional[List[str]] = None
    question_type: Optional[str] = None
    instructions: Optional[str] = None

class CanvasQuestionResponse(BaseModel):
    answer: str
    confidence: float
    sources: List[KnowledgeSourceSnippet] = []
    explanation: str
    mode: str
    needs_review: bool
