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
        # Verificar si ya existen estudiantes
        if db.query(models.Student).count() > 0:
            print("Database already seeded.")
            return

        # Crear un par de estudiantes de prueba
        s1 = models.Student(
            name="Juan Perez",
            course="4to Básico",
            level="Básica",
            notes="Alumno con déficit de atención."
        )
        s2 = models.Student(
            name="Maria Gonzalez",
            course="1ro Medio",
            level="Media",
            notes="Excelente alumna, participativa."
        )
        
        db.add(s1)
        db.add(s2)
        db.commit()
        db.refresh(s1)
        db.refresh(s2)

        # Crear observaciones de prueba para Juan
        obs1 = models.Observation(
            student_id=s1.id,
            category="comportamiento",
            content="Suele distraer a sus compañeros durante la clase de matemáticas."
        )
        obs2 = models.Observation(
            student_id=s1.id,
            category="apoyo",
            content="Requiere sentarse en las primeras filas."
        )
        
        # Crear observaciones de prueba para Maria
        obs3 = models.Observation(
            student_id=s2.id,
            category="academico",
            content="Destaca en ramos humanistas."
        )

        db.add_all([obs1, obs2, obs3])
        
        # Crear setting por defecto para AI_PROVIDER
        setting1 = models.Setting(key="AI_PROVIDER", value="mock")
        db.add(setting1)
        
        db.commit()
        print("Database seeded successfully.")
        
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed()
