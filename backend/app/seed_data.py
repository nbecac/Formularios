from sqlalchemy.orm import Session
from . import models, database

def seed(db: Session):
    # Check if there are students
    if db.query(models.Student).first():
        return # already seeded

    s1 = models.Student(
        name="Juan Pérez", 
        course="3ro Medio A", 
        level="Media", 
        notes="Buen comportamiento, participa en clases pero tiene dificultad en matemáticas. Requiere apoyo adicional en ciencias exactas."
    )
    s2 = models.Student(
        name="María González", 
        course="1ro Medio B", 
        level="Media", 
        notes="Excelente alumna, muy responsable. Destaca en lenguaje."
    )
    s3 = models.Student(
        name="Pedro Sánchez", 
        course="8vo Básico A", 
        level="Básica", 
        notes="Inquieto, a veces distrae a sus compañeros. Promedio general bueno."
    )

    db.add_all([s1, s2, s3])
    db.commit()

    db.refresh(s1)
    db.refresh(s2)
    db.refresh(s3)

    obs1 = models.Observation(student_id=s1.id, category="académico", content="Ha mejorado sus notas en el último semestre.")
    obs2 = models.Observation(student_id=s2.id, category="comportamiento", content="Siempre dispuesta a ayudar.")
    obs3 = models.Observation(student_id=s3.id, category="académico", content="Necesita prestar más atención en clases teóricas.")

    db.add_all([obs1, obs2, obs3])
    db.commit()

    # Base settings
    set1 = models.Setting(key="ai_provider", value="mock")
    db.add(set1)
    db.commit()

if __name__ == "__main__":
    database.Base.metadata.create_all(bind=database.engine)
    db = database.SessionLocal()
    try:
        seed(db)
        print("Database seeded successfully.")
    finally:
        db.close()
