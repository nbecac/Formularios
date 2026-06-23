from .database import engine, SessionLocal
from . import models

def seed():
    """
    Función para inicializar la base de datos con un set mínimo de datos de prueba
    útiles para el desarrollo local si la base de datos está vacía.
    """
    models.Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    try:
        # Verificar si ya existen estudiantes. Si el total es 3 o mas, salimos.
        # Esto permite ser idempotente si ejecutamos varias veces.
        if db.query(models.Student).count() >= 3:
            print("Database already seeded with enough students.")
            return

        # Estudiante 1
        s1 = db.query(models.Student).filter_by(name="Juan Perez", course="4to Básico").first()
        if not s1:
            s1 = models.Student(
                name="Juan Perez",
                course="4to Básico",
                level="Básica",
                notes="Alumno con déficit de atención."
            )
            db.add(s1)
            
        # Estudiante 2
        s2 = db.query(models.Student).filter_by(name="Maria Gonzalez", course="1ro Medio").first()
        if not s2:
            s2 = models.Student(
                name="Maria Gonzalez",
                course="1ro Medio",
                level="Media",
                notes="Excelente alumna, participativa."
            )
            db.add(s2)
            
        # Estudiante 3
        s3 = db.query(models.Student).filter_by(name="Pedro Sanchez", course="2do Básico").first()
        if not s3:
            s3 = models.Student(
                name="Pedro Sanchez",
                course="2do Básico",
                level="Básica",
                notes="Suele faltar los viernes."
            )
            db.add(s3)

        db.commit()
        db.refresh(s1)
        db.refresh(s2)
        db.refresh(s3)

        # Crear observaciones de prueba para Juan si no tiene
        if db.query(models.Observation).filter_by(student_id=s1.id).count() == 0:
            obs1 = models.Observation(student_id=s1.id, category="comportamiento", content="Suele distraer a sus compañeros durante la clase de matemáticas.")
            obs2 = models.Observation(student_id=s1.id, category="apoyo", content="Requiere sentarse en las primeras filas.")
            db.add_all([obs1, obs2])
        
        # Crear observaciones de prueba para Maria si no tiene
        if db.query(models.Observation).filter_by(student_id=s2.id).count() == 0:
            obs3 = models.Observation(student_id=s2.id, category="academico", content="Destaca en ramos humanistas.")
            db.add(obs3)
            
        # Crear observaciones de prueba para Pedro si no tiene
        if db.query(models.Observation).filter_by(student_id=s3.id).count() == 0:
            obs4 = models.Observation(student_id=s3.id, category="asistencia", content="No asiste los viernes.")
            obs5 = models.Observation(student_id=s3.id, category="apoyo", content="Necesita tiempo extra en evaluaciones.")
            db.add_all([obs4, obs5])

        # Crear setting por defecto para AI_PROVIDER si no existe
        setting_ai = db.query(models.Setting).filter_by(key="AI_PROVIDER").first()
        if not setting_ai:
            setting_ai = models.Setting(key="AI_PROVIDER", value="mock")
            db.add(setting_ai)
            
        db.commit()
        print("Database seeded successfully with 3 students.")
        
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed()
