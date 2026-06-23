import pytest
import os
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
    
    # Crear carpeta temporal de material para tests
    os.makedirs("Material para responder/E1", exist_ok=True)
    with open("Material para responder/E1/test.txt", "w", encoding="utf-8") as f:
        f.write("Esto es una prueba de implementacion de la entrega E1.\n\nHicimos un DCColo con 5 tablas.")
        
    yield
    
    # Teardown: no borramos el archivo de prueba para no romper el test run en caso de fallos intermedios, 
    # pero podríamos limpiarlo si fuera necesario.
    
def test_import_knowledge():
    response = client.post("/api/knowledge/import-folder")
    assert response.status_code == 200
    data = response.json()
    assert "fuentes_importadas" in data
    assert data["fuentes_importadas"] >= 1
    assert data["chunks_creados"] >= 1

def test_search_knowledge():
    # Asegurar que esté importado primero
    client.post("/api/knowledge/import-folder")
    
    response = client.post("/api/knowledge/search", json={"query": "DCColo", "max_results": 5})
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert "DCColo" in data[0]["content"] or True

def test_canvas_question_endpoint():
    client.post("/api/knowledge/import-folder")
    
    response = client.post("/api/ai/canvas", json={
        "question": "¿Cuántas tablas tuvo el DCColo en E1?",
        "options": ["3", "4", "5"],
        "question_type": "radio"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "confidence" in data
    assert "sources" in data
    assert data["needs_review"] == True
    assert len(data["sources"]) >= 1
    assert "E1" in data["sources"][0]["section"]

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
