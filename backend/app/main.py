from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

from . import models, schemas, crud, form_analyzer, ai_agent
from .database import engine, get_db
from .config import settings

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
    return {"status": "ok", "service": "formularios-backend"}

@app.get("/api/students", response_model=List[schemas.StudentResponse])
def get_students(db: Session = Depends(get_db)):
    students = crud.get_students(db)
    return students

@app.get("/api/students/{student_id}", response_model=schemas.StudentDetail)
def get_student(student_id: int, db: Session = Depends(get_db)):
    student = crud.get_student(db, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student

@app.post("/api/students", response_model=schemas.StudentResponse)
def create_student(student: schemas.StudentCreate, db: Session = Depends(get_db)):
    return crud.create_student(db, student)

@app.put("/api/students/{student_id}", response_model=schemas.StudentResponse)
def update_student(student_id: int, student: schemas.StudentUpdate, db: Session = Depends(get_db)):
    db_student = crud.update_student(db, student_id, student)
    if not db_student:
        raise HTTPException(status_code=404, detail="Student not found")
    return db_student

@app.delete("/api/students/{student_id}")
def delete_student(student_id: int, db: Session = Depends(get_db)):
    db_student = crud.delete_student(db, student_id)
    if not db_student:
        raise HTTPException(status_code=404, detail="Student not found")
    return {"status": "success", "detail": "Student deleted"}

@app.get("/api/students/{student_id}/observations", response_model=List[schemas.ObservationResponse])
def get_student_observations(student_id: int, db: Session = Depends(get_db)):
    student = crud.get_student(db, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return crud.get_student_observations(db, student_id)

@app.post("/api/students/{student_id}/observations", response_model=schemas.ObservationResponse)
def create_observation(student_id: int, observation: schemas.ObservationCreate, db: Session = Depends(get_db)):
    student = crud.get_student(db, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return crud.create_observation(db, student_id, observation)

@app.put("/api/observations/{observation_id}", response_model=schemas.ObservationResponse)
def update_observation(observation_id: int, observation: schemas.ObservationUpdate, db: Session = Depends(get_db)):
    db_obs = crud.update_observation(db, observation_id, observation)
    if not db_obs:
        raise HTTPException(status_code=404, detail="Observation not found")
    return db_obs

@app.delete("/api/observations/{observation_id}")
def delete_observation(observation_id: int, db: Session = Depends(get_db)):
    db_obs = crud.delete_observation(db, observation_id)
    if not db_obs:
        raise HTTPException(status_code=404, detail="Observation not found")
    return {"status": "success", "detail": "Observation deleted"}

@app.post("/api/import/students-csv", response_model=schemas.ImportSummaryResponse)
async def import_students_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
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
    db_settings = crud.get_settings(db)
    return {s.key: s.value for s in db_settings}

@app.get("/api/debug/status")
def debug_status(db: Session = Depends(get_db)):
    try:
        students_count = db.query(models.Student).count()
        settings_count = db.query(models.Setting).count()
        ai_provider = settings.AI_PROVIDER
        
        return {
            "status": "ok",
            "database": "connected",
            "students_count": students_count,
            "settings_count": settings_count,
            "ai_provider": ai_provider,
            "service": "formularios-backend"
        }
    except Exception as e:
        return {
            "status": "error",
            "database": "disconnected",
            "error": str(e),
            "service": "formularios-backend"
        }

@app.post("/api/forms/analyze", response_model=schemas.FormAnalyzeResponse)
def analyze_form(req: schemas.FormAnalyzeRequest):
    normalized = form_analyzer.normalize_fields(req.fields)
    return schemas.FormAnalyzeResponse(fields=normalized)

@app.post("/api/forms/generate", response_model=schemas.FormGenerateResponse)
def generate_form(req: schemas.FormGenerateRequest, db: Session = Depends(get_db)):
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
    history = crud.create_history(db, req)
    return {"status": "success", "id": history.id}
