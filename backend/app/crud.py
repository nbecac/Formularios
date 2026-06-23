import csv
import io
from sqlalchemy.orm import Session
from . import models, schemas

def get_students(db: Session):
    """
    Retorna todos los estudiantes registrados.
    """
    return db.query(models.Student).all()

def get_student(db: Session, student_id: int):
    """
    Retorna un estudiante filtrado por ID.
    """
    return db.query(models.Student).filter(models.Student.id == student_id).first()

def create_student(db: Session, student: schemas.StudentCreate):
    """
    Inserta un nuevo estudiante en la base de datos.
    """
    db_student = models.Student(**student.model_dump())
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student

def update_student(db: Session, student_id: int, student: schemas.StudentUpdate):
    """
    Actualiza datos básicos de un estudiante existente de forma parcial.
    """
    db_student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not db_student:
        return None
        
    update_data = student.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_student, key, value)
        
    db.commit()
    db.refresh(db_student)
    return db_student

def delete_student(db: Session, student_id: int):
    """
    Borra un estudiante y todas sus observaciones asociadas (cascada definida en modelo).
    """
    db_student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not db_student:
        return None
        
    db.delete(db_student)
    db.commit()
    return db_student

def get_student_observations(db: Session, student_id: int):
    """
    Recupera todas las observaciones para un estudiante dado.
    """
    return db.query(models.Observation).filter(models.Observation.student_id == student_id).all()

def create_observation(db: Session, student_id: int, observation: schemas.ObservationCreate):
    """
    Agrega una nueva observación a un estudiante en específico.
    """
    db_obs = models.Observation(**observation.model_dump(), student_id=student_id)
    db.add(db_obs)
    db.commit()
    db.refresh(db_obs)
    return db_obs

def update_observation(db: Session, observation_id: int, observation: schemas.ObservationUpdate):
    """
    Actualiza la categoría o contenido de una observación existente.
    """
    db_obs = db.query(models.Observation).filter(models.Observation.id == observation_id).first()
    if not db_obs:
        return None
        
    update_data = observation.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_obs, key, value)
        
    db.commit()
    db.refresh(db_obs)
    return db_obs

def delete_observation(db: Session, observation_id: int):
    """
    Borra directamente una observación puntual.
    """
    db_obs = db.query(models.Observation).filter(models.Observation.id == observation_id).first()
    if not db_obs:
        return None
        
    db.delete(db_obs)
    db.commit()
    return db_obs

def import_students_csv(db: Session, csv_text: str) -> dict:
    """
    Importa masivamente estudiantes usando formato CSV delimitado por comas o punto y coma.
    Soporta encoding utf-8-sig para evadir BOM characters.
    Hace Upsert basado en la llave natural (name, course).
    """
    # Intentamos detectar delimitador si viene con ;
    delimiter = ';' if ';' in csv_text.split('\n')[0] else ','
    
    # Preparamos el lector
    reader = csv.DictReader(io.StringIO(csv_text), delimiter=delimiter)
    
    creados = 0
    actualizados = 0
    obs_creadas = 0
    errores = []
    
    for idx, row in enumerate(reader, start=1):
        try:
            name = row.get('name', '').strip()
            course = row.get('course', '').strip()
            
            # Name y course son obligatorios para el upsert
            if not name or not course:
                errores.append({"row_index": idx, "error": "name y course son obligatorios en cada fila"})
                continue
                
            level = row.get('level', '').strip()
            notes = row.get('notes', '').strip()
            
            # Buscar el estudiante por llave natural
            student = db.query(models.Student).filter(
                models.Student.name == name, 
                models.Student.course == course
            ).first()
            
            if student:
                # Update
                if level:
                    student.level = level
                if notes:
                    student.notes = notes
                actualizados += 1
            else:
                # Create
                student = models.Student(
                    name=name, 
                    course=course, 
                    level=level, 
                    notes=notes
                )
                db.add(student)
                db.flush() # Importante para poder asignar observaciones en el mismo paso
                creados += 1
                
            obs_cat = row.get('observation_category', '').strip()
            obs_content = row.get('observation_content', '').strip()
            
            if obs_cat and obs_content:
                obs = models.Observation(
                    student_id=student.id, 
                    category=obs_cat, 
                    content=obs_content
                )
                db.add(obs)
                obs_creadas += 1
                
        except Exception as e:
            errores.append({"row_index": idx, "error": f"Excepcion importando fila: {str(e)}"})
            
    db.commit()
    
    return {
        "alumnos_creados": creados,
        "alumnos_actualizados": actualizados,
        "observaciones_creadas": obs_creadas,
        "errores": errores
    }

def get_settings(db: Session):
    return db.query(models.Setting).all()

def update_setting(db: Session, key: str, value: str):
    setting = db.query(models.Setting).filter(models.Setting.key == key).first()
    if setting:
        setting.value = value
    else:
        setting = models.Setting(key=key, value=value)
        db.add(setting)
    db.commit()
    return setting

def create_history(db: Session, history: schemas.HistoryCreate):
    db_hist = models.History(
        url=history.url,
        page_title=history.page_title,
        student_id=history.student_id,
        detected_fields_json=history.detected_fields_json,
        generated_answers_json=history.generated_answers_json
    )
    db.add(db_hist)
    db.commit()
    db.refresh(db_hist)
    return db_hist
