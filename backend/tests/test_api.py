import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.database import engine, Base
from app import seed_data
from app.config import settings

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    seed_data.seed()
    yield

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_api_students():
    response = client.get("/api/students")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 3

def test_api_settings():
    response = client.get("/api/settings")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "ai_provider" in data

def test_api_debug_status():
    response = client.get("/api/debug/status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["database"] == "connected"
    assert "students_count" in data
    assert "settings_count" in data

def test_forms_analyze():
    req_payload = {
        "fields": [
            {"fieldId": "test1", "type": "text", "label": "Nombre", "options": [], "required": True}
        ]
    }
    response = client.post("/api/forms/analyze", json=req_payload)
    assert response.status_code == 200
    data = response.json()
    assert "fields" in data
    assert len(data["fields"]) == 1
    assert data["fields"][0]["normalizedLabel"] == "Nombre"

def test_forms_generate():
    req_payload = {
        "fields": [
            {"fieldId": "test1", "normalizedLabel": "Nombre", "normalizedType": "text", "options": [], "required": True, "confidence": 0.9, "warnings": []}
        ],
        "student_id": 1,
        "url": "http://test.com",
        "page_title": "Test"
    }
    response = client.post("/api/forms/generate", json=req_payload)
    assert response.status_code == 200
    data = response.json()
    assert "answers" in data
    assert len(data["answers"]) == 1
    assert data["answers"][0]["fieldId"] == "test1"
    assert data["answers"][0]["answer"] != ""
