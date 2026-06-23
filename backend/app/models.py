from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    course = Column(String)
    level = Column(String)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    observations = relationship("Observation", back_populates="student")
    answer_histories = relationship("AnswerHistory", back_populates="student")

class Observation(Base):
    __tablename__ = "observations"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    category = Column(String)
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    student = relationship("Student", back_populates="observations")

class AnswerHistory(Base):
    __tablename__ = "answer_history"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String)
    page_title = Column(String)
    student_id = Column(Integer, ForeignKey("students.id"))
    detected_fields_json = Column(Text)
    generated_answers_json = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    student = relationship("Student", back_populates="answer_histories")

class Setting(Base):
    __tablename__ = "settings"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, index=True)
    value = Column(String)

class FormTemplate(Base):
    __tablename__ = "form_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    domain = Column(String)
    description = Column(Text)
    mapping_json = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
