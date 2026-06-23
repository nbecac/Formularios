from .database import engine, SessionLocal
from . import models

def seed():
    models.Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    try:
        if db.query(models.Setting).count() == 0:
            db.add(models.Setting(key="ai_provider", value="mock"))
            
        if db.query(models.Student).count() == 0:
            s1 = models.Student(name="Juan Pérez", course="3ro Medio A", level="Media", notes="Buen comportamiento, participa en clases pero tiene dificultad en matemáticas. Requiere apoyo adicional en ciencias exactas.")
            s2 = models.Student(name="María González", course="1ro Medio B", level="Media", notes="Excelente alumna, muy responsable. Destaca en lenguaje.")
            s3 = models.Student(name="Pedro Sánchez", course="8vo Básico A", level="Básica", notes="Inquieto, a veces distrae a sus compañeros. Promedio general bueno.")
            
            db.add_all([s1, s2, s3])
            db.commit()
            
            o1 = models.Observation(student_id=s1.id, category="académico", content="Ha mejorado sus notas en el último semestre.")
            o2 = models.Observation(student_id=s2.id, category="comportamiento", content="Siempre dispuesta a ayudar.")
            o3 = models.Observation(student_id=s3.id, category="académico", content="Necesita prestar más atención en clases teóricas.")
            
            db.add_all([o1, o2, o3])
            db.commit()
            print("Database seeded successfully.")
        else:
            print("Database already seeded.")
            
    finally:
        db.close()

if __name__ == "__main__":
    seed()
