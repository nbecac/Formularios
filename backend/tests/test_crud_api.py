import pytest
import io
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from backend.app.main import app
from backend.app.database import Base, get_db
from backend.app.schemas import FormAnalyzeResponseField

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_crud.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="module")
def client():
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)

def test_create_student(client):
    response = client.post("/api/students", json={
        "name": "Test Student",
        "course": "1A",
        "level": "Basic",
        "notes": "Test notes"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Student"
    assert "id" in data
    global test_student_id
    test_student_id = data["id"]

def test_get_student(client):
    response = client.get(f"/api/students/{test_student_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Student"

def test_edit_student(client):
    response = client.put(f"/api/students/{test_student_id}", json={
        "level": "Advanced"
    })
    assert response.status_code == 200
    assert response.json()["level"] == "Advanced"

def test_create_observation(client):
    response = client.post(f"/api/students/{test_student_id}/observations", json={
        "category": "academico",
        "content": "Muy buen rendimiento."
    })
    assert response.status_code == 200
    data = response.json()
    assert data["category"] == "academico"
    assert "id" in data
    global test_obs_id
    test_obs_id = data["id"]

def test_list_observations(client):
    response = client.get(f"/api/students/{test_student_id}/observations")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["category"] == "academico"

def test_edit_observation(client):
    response = client.put(f"/api/observations/{test_obs_id}", json={
        "content": "Rendimiento excelente."
    })
    assert response.status_code == 200
    assert response.json()["content"] == "Rendimiento excelente."

def test_generate_responses_with_real_obs(client):
    req_body = {
        "fields": [
            {
                "fieldId": "f1",
                "normalizedLabel": "Desempeño académico",
                "normalizedType": "textarea",
                "options": [],
                "required": False,
                "confidence": 0.9,
                "warnings": []
            }
        ],
        "student_id": test_student_id,
        "url": "http://test",
        "page_title": "Test"
    }
    response = client.post("/api/forms/generate", json=req_body)
    assert response.status_code == 200
    ans = response.json()["answers"][0]
    assert "Rendimiento excelente." in ans["answer"]
    assert ans["source"] == "mock_ai"

def test_delete_observation(client):
    response = client.delete(f"/api/observations/{test_obs_id}")
    assert response.status_code == 200
    resp2 = client.get(f"/api/students/{test_student_id}/observations")
    assert len(resp2.json()) == 0

def test_delete_student(client):
    client.post(f"/api/students/{test_student_id}/observations", json={"category":"test", "content":"t"})
    response = client.delete(f"/api/students/{test_student_id}")
    assert response.status_code == 200
    resp2 = client.get(f"/api/students/{test_student_id}")
    assert resp2.status_code == 404

def test_import_csv_and_upsert(client):
    csv_content = """name,course,level,notes,observation_category,observation_content
Importado,2B,Basico,,general,test
Importado,2B,Avanzado,Nueva nota,,
"""
    files = {'file': ('test.csv', io.BytesIO(csv_content.encode('utf-8')), 'text/csv')}
    response = client.post("/api/import/students-csv", files=files)
    assert response.status_code == 200
    data = response.json()
    assert data["alumnos_creados"] == 1
    assert data["alumnos_actualizados"] == 1
    assert data["observaciones_creadas"] == 1
    assert len(data["errores"]) == 0
