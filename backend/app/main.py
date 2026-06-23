from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

from . import models, schemas, crud, form_analyzer, ai_agent
from .database import engine, get_db
from .config import settings

# Create tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Formularios AI Assistant API", version="1.0.0")

# CORS middleware required for Chrome Extension to communicate
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all origins for the extension
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

@app.get("/api/settings")
def get_settings(db: Session = Depends(get_db)):
    db_settings = crud.get_settings(db)
    return {s.key: s.value for s in db_settings}

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
