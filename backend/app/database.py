from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from .config import settings

# Conexión principal de SQLAlchemy
engine = create_engine(
    settings.DATABASE_URL, 
    connect_args={"check_same_thread": False}  # Necesario solo para SQLite
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """
    Dependencia de FastAPI para obtener una sesión de base de datos
    por cada petición web. Cierra automáticamente la sesión al terminar.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
