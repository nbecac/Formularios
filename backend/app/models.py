from sqlalchemy import Column, Integer, String, Text, ForeignKey, Float, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class Student(Base):
    """
    Entidad Estudiante. Almacena el registro principal.
    Tiene relación 1:N con Observation, y se borran en cascada.
    """
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    course = Column(String, index=True)
    level = Column(String)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relación de uno a muchos con borrado en cascada
    observations = relationship("Observation", back_populates="student", cascade="all, delete-orphan")

class Observation(Base):
    """
    Entidad Observación. 
    Contiene un texto libre asociado a una categoría (ej: "comportamiento").
    """
    __tablename__ = "observations"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), index=True)
    category = Column(String, index=True)
    content = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    student = relationship("Student", back_populates="observations")

class Setting(Base):
    """
    Configuraciones persistentes clave-valor en base de datos.
    """
    __tablename__ = "settings"
    
    key = Column(String, primary_key=True, index=True)
    value = Column(String)

class History(Base):
    """
    Historial de rellenado automático de formularios por parte del AI Agent.
    """
    __tablename__ = "history"
    
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, index=True)
    page_title = Column(String)
    student_id = Column(Integer)
    detected_fields_json = Column(Text)
    generated_answers_json = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
