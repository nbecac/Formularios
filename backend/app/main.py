from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

from . import models, schemas, crud, form_analyzer, ai_agent
from .database import engine, get_db
from .config import settings

# Crear todas las tablas en la base de datos
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Formularios AI Assistant API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    """
    Endpoint de salud del backend para comprobar si está online.
    """
    return {"status": "ok", "service": "formularios-backend"}

@app.get("/api/students", response_model=List[schemas.StudentResponse])
def get_students(db: Session = Depends(get_db)):
    """
    Obtener la lista completa de alumnos.
    """
    students = crud.get_students(db)
    return students

@app.get("/api/students/{student_id}", response_model=schemas.StudentDetail)
def get_student(student_id: int, db: Session = Depends(get_db)):
    """
    Obtener los detalles de un alumno específico, incluyendo observaciones.
    """
    student = crud.get_student(db, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student

@app.post("/api/students", response_model=schemas.StudentResponse)
def create_student(student: schemas.StudentCreate, db: Session = Depends(get_db)):
    """
    Crear un nuevo alumno en la base de datos.
    """
    return crud.create_student(db, student)

@app.put("/api/students/{student_id}", response_model=schemas.StudentResponse)
def update_student(student_id: int, student: schemas.StudentUpdate, db: Session = Depends(get_db)):
    """
    Actualizar datos básicos de un alumno.
    """
    db_student = crud.update_student(db, student_id, student)
    if not db_student:
        raise HTTPException(status_code=404, detail="Student not found")
    return db_student

@app.delete("/api/students/{student_id}")
def delete_student(student_id: int, db: Session = Depends(get_db)):
    """
    Eliminar un alumno (y en cascada sus observaciones).
    """
    db_student = crud.delete_student(db, student_id)
    if not db_student:
        raise HTTPException(status_code=404, detail="Student not found")
    return {"status": "success", "detail": "Student deleted"}

@app.get("/api/students/{student_id}/observations", response_model=List[schemas.ObservationResponse])
def get_student_observations(student_id: int, db: Session = Depends(get_db)):
    """
    Obtener todas las observaciones de un alumno.
    """
    student = crud.get_student(db, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return crud.get_student_observations(db, student_id)

@app.post("/api/students/{student_id}/observations", response_model=schemas.ObservationResponse)
def create_observation(student_id: int, observation: schemas.ObservationCreate, db: Session = Depends(get_db)):
    """
    Agregar una observación nueva a un alumno.
    """
    student = crud.get_student(db, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return crud.create_observation(db, student_id, observation)

@app.put("/api/observations/{observation_id}", response_model=schemas.ObservationResponse)
def update_observation(observation_id: int, observation: schemas.ObservationUpdate, db: Session = Depends(get_db)):
    """
    Modificar una observación existente.
    """
    db_obs = crud.update_observation(db, observation_id, observation)
    if not db_obs:
        raise HTTPException(status_code=404, detail="Observation not found")
    return db_obs

@app.delete("/api/observations/{observation_id}")
def delete_observation(observation_id: int, db: Session = Depends(get_db)):
    """
    Eliminar una observación.
    """
    db_obs = crud.delete_observation(db, observation_id)
    if not db_obs:
        raise HTTPException(status_code=404, detail="Observation not found")
    return {"status": "success", "detail": "Observation deleted"}

@app.post("/api/import/students-csv", response_model=schemas.ImportSummaryResponse)
async def import_students_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Importar alumnos vía CSV. Soporta encoding utf-8-sig y delimitadores , o ;.
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV")
    
    content = await file.read()
    try:
        csv_text = content.decode('utf-8-sig')
    except UnicodeDecodeError:
        try:
            csv_text = content.decode('utf-8')
        except UnicodeDecodeError:
            raise HTTPException(status_code=400, detail="Invalid encoding. Use UTF-8")
            
    summary = crud.import_students_csv(db, csv_text)
    return summary

@app.get("/api/settings")
def get_settings(db: Session = Depends(get_db)):
    """
    Obtener configuraciones del sistema guardadas en BD.
    """
    db_settings = crud.get_settings(db)
    result = {s.key: s.value for s in db_settings}
    
    # Asegurar compatibilidad para frontend/tests que buscan "ai_provider" (minúsculas)
    if "AI_PROVIDER" in result:
        result["ai_provider"] = result["AI_PROVIDER"]
        
    return result

@app.get("/api/debug/status")
def debug_status(db: Session = Depends(get_db)):
    """
    Obtener estado extendido del backend para diagnóstico.
    """
    try:
        students_count = db.query(models.Student).count()
        settings_count = db.query(models.Setting).count()
        ai_provider = settings.AI_PROVIDER.lower() if settings.AI_PROVIDER else "mock"
        
        has_key = False
        key_source = "missing"
        if ai_provider == "openai" and settings.OPENAI_API_KEY:
            has_key = True
            key_source = "OPENAI_API_KEY"
        elif ai_provider == "gemini" and settings.ACTIVE_GEMINI_KEY:
            has_key = True
            key_source = settings.GEMINI_KEY_SOURCE
            
        return {
            "status": "ok",
            "database": "connected",
            "students_count": students_count,
            "settings_count": settings_count,
            "ai_provider": ai_provider,
            "ai_model": settings.AI_MODEL,
            "ai_configured": has_key,
            "key_source": key_source,
            "service": "formularios-backend"
        }
    except Exception as e:
        return {
            "status": "error",
            "database": "disconnected",
            "error": str(e),
            "service": "formularios-backend"
        }

@app.post("/api/ai/test", response_model=schemas.AITestResponse)
def test_ai(req: schemas.AITestRequest, db: Session = Depends(get_db)):
    """
    Endpoint para probar la IA sin rellenar un formulario.
    """
    provider = req.provider or settings.AI_PROVIDER.lower() or "mock"
    
    # Crear un campo dummy
    dummy_field = schemas.FormAnalyzeResponseField(
        fieldId="test_field",
        normalizedLabel=req.text or "Observación general",
        normalizedType="textarea",
        options=[],
        required=False,
        confidence=1.0,
        warnings=[]
    )
    
    student = None
    if req.student_id:
        student = crud.get_student(db, req.student_id)
        
    if not student:
        student = models.Student(name="Alumno de Prueba", course="Test", level="Test", notes="Test notes")
        
    page_context = {"url": "test://localhost", "title": "Test Form"}
    
    # Usar el config genérico o forzar el provider
    class TempSettings:
        AI_PROVIDER = provider
        AI_MODEL = settings.AI_MODEL
        OPENAI_API_KEY = settings.OPENAI_API_KEY
        GEMINI_API_KEY = settings.GEMINI_API_KEY

    temp_settings = TempSettings()
    
    try:
        answers = ai_agent.generate_answers([dummy_field], student, page_context, temp_settings)
        if not answers:
            return schemas.AITestResponse(provider=provider, answer="", fallback=True, error="Empty response")
            
        ans = answers[0]
        fallback = ans.source == "mock_fallback" or ans.source == "mock_ai"
        return schemas.AITestResponse(provider=provider, answer=ans.answer, fallback=fallback)
    except Exception as e:
        return schemas.AITestResponse(provider=provider, answer="", fallback=True, error=str(e))


@app.post("/api/forms/analyze", response_model=schemas.FormAnalyzeResponse)
def analyze_form(req: schemas.FormAnalyzeRequest):
    """
    Procesar los campos crudos extraídos de la web y devolver versión normalizada.
    """
    normalized = form_analyzer.normalize_fields(req.fields)
    return schemas.FormAnalyzeResponse(fields=normalized)

@app.post("/api/forms/generate", response_model=schemas.FormGenerateResponse)
def generate_form(req: schemas.FormGenerateRequest, db: Session = Depends(get_db)):
    """
    Generar respuestas sugeridas para un alumno particular usando AI.
    """
    student = crud.get_student(db, req.student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
        
    page_context = {
        "url": req.url,
        "title": req.page_title,
        "context": req.context or ""
    }
    
    answers = ai_agent.generate_answers(req.fields, student, page_context, settings)
    return schemas.FormGenerateResponse(answers=answers)

@app.post("/api/history")
def create_history(req: schemas.HistoryCreate, db: Session = Depends(get_db)):
    """
    Registrar en el historial cuando se rellena un formulario.
    """
    history = crud.create_history(db, req)
    return {"status": "success", "id": history.id}

@app.post("/api/knowledge/import-folder", response_model=schemas.KnowledgeImportSummary)
def import_knowledge(base_folder: str = "Material para responder", db: Session = Depends(get_db)):
    """
    Importar la carpeta 'Material para responder' al conocimiento local.
    """
    summary = crud.import_knowledge_folder(db, base_folder)
    return summary

@app.post("/api/knowledge/search")
def search_knowledge(req: schemas.KnowledgeSearchRequest, db: Session = Depends(get_db)):
    """
    Buscar en los chunks de conocimiento importados.
    """
    chunks = crud.search_knowledge(db, req.query, req.max_results, req.preferred_sections)
    return [
        {
            "id": c.id,
            "section": c.section,
            "source": c.source.title,
            "content": c.content
        } for c in chunks
    ]

@app.post("/api/ai/canvas", response_model=schemas.CanvasQuestionResponse)
def handle_canvas_question(req: schemas.CanvasQuestionRequest, db: Session = Depends(get_db)):
    """
    Endpoint dedicado para resolver preguntas de Canvas usando el material del curso.
    """
    return ai_agent.answer_project_question(req, db, settings)
