from sqlalchemy.orm import Session
from . import models, schemas

def get_students(db: Session):
    return db.query(models.Student).all()

def get_student(db: Session, student_id: int):
    return db.query(models.Student).filter(models.Student.id == student_id).first()

def get_settings(db: Session):
    return db.query(models.Setting).all()

def create_history(db: Session, history: schemas.HistoryCreate):
    db_history = models.AnswerHistory(
        url=history.url,
        page_title=history.page_title,
        student_id=history.student_id,
        detected_fields_json=history.detected_fields_json,
        generated_answers_json=history.generated_answers_json
    )
    db.add(db_history)
    db.commit()
    db.refresh(db_history)
    return db_history
