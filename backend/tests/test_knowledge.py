import pytest
import os
import shutil
from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db, engine, Base
from sqlalchemy.orm import sessionmaker

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_teardown():
    # Setup
    Base.metadata.create_all(bind=engine)
    
    # Crear carpeta temporal de material para tests AISLADA
    os.makedirs("test_material_tmp/E1", exist_ok=True)
    with open("test_material_tmp/E1/test.txt", "w", encoding="utf-8") as f:
        f.write("Esto es una prueba de implementacion de la entrega E1.\n\nHicimos un DCColo con 5 tablas.")
        
    yield
    
    # Teardown
    if os.path.exists("test_material_tmp"):
        shutil.rmtree("test_material_tmp")
    
def test_import_knowledge():
    response = client.post("/api/knowledge/import-folder?base_folder=test_material_tmp")
    assert response.status_code == 200
    data = response.json()
    assert "fuentes_importadas" in data
    assert data["fuentes_importadas"] >= 1
    assert data["chunks_creados"] >= 1

def test_search_knowledge():
    client.post("/api/knowledge/import-folder?base_folder=test_material_tmp")
    
    response = client.post("/api/knowledge/search", json={"query": "DCColo", "max_results": 5})
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert "DCColo" in data[0]["content"]

def test_canvas_question_endpoint():
    client.post("/api/knowledge/import-folder?base_folder=test_material_tmp")
    
    response = client.post("/api/ai/canvas", json={
        "question": "¿Cuántas tablas tuvo el DCColo en E1?",
        "options": [
            {"label": "A", "text": "3 tablas"},
            {"label": "B", "text": "5 tablas"},
            {"label": "C", "text": "10 tablas"}
        ],
        "question_type": "multiple_choice",
        "selection_mode": "single"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "confidence" in data
    assert "sources" in data
    assert data["needs_review"] == True
    assert data["selected_option"] == "B"
    assert len(data["sources"]) >= 1
    assert "E1" in data["sources"][0]["section"]

def test_canvas_multiple_choice_tie_or_no_evidence():
    client.post("/api/knowledge/import-folder?base_folder=test_material_tmp")
    
    response = client.post("/api/ai/canvas", json={
        "question": "¿Cuántas tablas tuvo el DCColo en E1?",
        "options": [
            {"label": "A", "text": "algo nada que ver 1"},
            {"label": "B", "text": "algo nada que ver 2"}
        ],
        "question_type": "multiple_choice",
        "selection_mode": "single"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data.get("selected_option") is None
    assert "No hay evidencia" in data["answer"] or "Empate" in data["explanation"]

def test_canvas_question_low_confidence_fallback():
    response = client.post("/api/ai/canvas", json={
        "question": "zxcvbnmasdf qwerpoiu qawsedrf",
        "options": [],
        "question_type": "text"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["confidence"] <= 0.2
    assert "No se encontró evidencia" in data["answer"]
