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
    Base.metadata.create_all(bind=engine)
    
    # Crear carpeta temporal de material para tests AISLADA
    os.makedirs("test_material_tmp/E1", exist_ok=True)
    os.makedirs("test_material_tmp/E2", exist_ok=True)
    
    # E1: Contenido sobre modelo E-R y relaciones
    with open("test_material_tmp/E1/test.txt", "w", encoding="utf-8") as f:
        f.write(
            "Esto es una prueba de implementacion de la entrega E1.\n\n"
            "Hicimos un DCColo con 5 tablas.\n\n"
            "La relacion entre Socio y Beneficio es N a M, "
            "donde un socio puede acceder a muchos beneficios "
            "y un beneficio aplica a muchos socios.\n\n"
            "El modelo Entidad-Relacion incluye las entidades: "
            "Socio, Beneficio, Membresia, Pago, Actividad."
        )
    
    # E2: Contenido sobre pagos e implementacion
    with open("test_material_tmp/E2/test.txt", "w", encoding="utf-8") as f:
        f.write(
            "Implementacion de la Entrega 2.\n\n"
            "El sistema de pagos de membresias se resolvio "
            "mediante un archivo CSV proporcionado llamado "
            "pagos_membresias.csv del cual se extrajeron e importaron los datos.\n\n"
            "Se crearon indices en las tablas mas consultadas.\n\n"
            "Para la importacion masiva de datos se utilizaron "
            "los archivos pagos_membresias.csv e init_database.sql."
        )
    
    # Resumen clave (prioridad alta)
    with open("test_material_tmp/resumen_clave_proyecto.md", "w", encoding="utf-8") as f:
        f.write(
            "# Resumen Clave del Proyecto DCColo\n\n"
            "## E1 - Modelo E-R\n"
            "- 5 tablas principales: Socio, Beneficio, Membresia, Pago, Actividad\n"
            "- Relacion Socio-Beneficio: N a M\n"
            "- Relacion Socio-Membresia: 1 a N\n\n"
            "## E2 - Implementacion\n"
            "- Pagos importados desde pagos_membresias.csv\n"
            "- Se uso init_database.sql para crear tablas\n"
            "- Se agregaron indices secundarios en tabla pagos\n\n"
            "## E3 - Mejoras\n"
            "- Se normalizo la tabla beneficios\n"
            "- Se agregaron stored procedures\n"
        )
        
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

def test_canvas_clear_evidence_e1():
    """Caso con evidencia clara: relacion Socio-Beneficio debe sugerir B (N a M)."""
    client.post("/api/knowledge/import-folder?base_folder=test_material_tmp")
    
    response = client.post("/api/ai/canvas", json={
        "question": "En el Modelo Entidad-Relacion de la Entrega 1, como se modela la relacion entre Socio y Beneficio?",
        "options": [
            {"label": "A", "text": "Relacion 1 a 1, un socio solo puede tener un beneficio."},
            {"label": "B", "text": "Relacion N a M, donde un socio puede acceder a muchos beneficios y un beneficio aplica a muchos socios."},
            {"label": "C", "text": "Relacion jerarquica donde Beneficio hereda de Socio."},
            {"label": "D", "text": "Relacion 1 a N, un socio puede tener muchos beneficios, pero el beneficio es exclusivo de un socio."}
        ],
        "question_type": "multiple_choice",
        "selection_mode": "single"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["selected_option"] == "B"
    assert data["confidence"] >= 0.5
    assert len(data["sources"]) >= 1
    assert "option_scores" in data
    assert len(data["option_scores"]) == 4
    # B should have highest score
    scores_by_label = {s["label"]: s["score"] for s in data["option_scores"]}
    assert scores_by_label["B"] > scores_by_label["A"]
    assert scores_by_label["B"] > scores_by_label["C"]

def test_canvas_clear_evidence_e2():
    """Caso con evidencia clara en E2: pagos via CSV."""
    client.post("/api/knowledge/import-folder?base_folder=test_material_tmp")
    
    response = client.post("/api/ai/canvas", json={
        "question": "Como se resolvio el sistema de pagos de membresias en la Entrega 2?",
        "options": [
            {"label": "A", "text": "Se utilizo una API externa Transbank conectada directamente al backend."},
            {"label": "B", "text": "Mediante un archivo CSV proporcionado llamado pagos_membresias.csv del cual se extrajeron e importaron los datos."},
            {"label": "C", "text": "No se implemento sistema de pagos en la E2."},
            {"label": "D", "text": "Se creo un trigger automatico en la BD para generar pagos mensuales simulados."}
        ],
        "question_type": "multiple_choice",
        "selection_mode": "single"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["selected_option"] == "B"
    assert data["confidence"] >= 0.5

def test_canvas_no_evidence():
    """Caso sin evidencia: pregunta inventada de E4/React debe no sugerir."""
    client.post("/api/knowledge/import-folder?base_folder=test_material_tmp")
    
    response = client.post("/api/ai/canvas", json={
        "question": "Cual es el comando exacto para clonar el repositorio de React nativo utilizado en la interfaz de la E4?",
        "options": [
            {"label": "A", "text": "npx create-react-app frontend-dccolo"},
            {"label": "B", "text": "git clone https://github.com/dccolo/react-app.git"},
            {"label": "C", "text": "npm install react-native-cli"},
            {"label": "D", "text": "vue create frontend-app"}
        ],
        "question_type": "multiple_choice",
        "selection_mode": "single"
    })
    
    assert response.status_code == 200
    data = response.json()
    # Should NOT suggest any option since there's no React/E4 material
    assert data.get("selected_option") is None or data["confidence"] < 0.5

def test_canvas_tie():
    """Caso empate: dos opciones con score parecido no debe sugerir."""
    client.post("/api/knowledge/import-folder?base_folder=test_material_tmp")
    
    response = client.post("/api/ai/canvas", json={
        "question": "Cuantas tablas tuvo el DCColo en E1?",
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

def test_canvas_sources_deduped():
    """Las fuentes deben estar deduplicadas (max 5, sin repetidos)."""
    client.post("/api/knowledge/import-folder?base_folder=test_material_tmp")
    
    response = client.post("/api/ai/canvas", json={
        "question": "Que se hizo en la entrega E1 del proyecto DCColo?",
        "options": [
            {"label": "A", "text": "Se hizo un DCColo con 5 tablas incluyendo Socio y Beneficio"},
            {"label": "B", "text": "Nada relevante"}
        ],
        "question_type": "multiple_choice",
        "selection_mode": "single"
    })
    
    assert response.status_code == 200
    data = response.json()
    # Check no duplicate sources
    source_keys = [(s["section"], s["filename"]) for s in data["sources"]]
    assert len(source_keys) == len(set(source_keys)), "Sources have duplicates!"
    assert len(data["sources"]) <= 5

def test_canvas_option_scores_returned():
    """El response debe incluir option_scores con el score de cada alternativa."""
    client.post("/api/knowledge/import-folder?base_folder=test_material_tmp")
    
    response = client.post("/api/ai/canvas", json={
        "question": "Como se importaron los pagos?",
        "options": [
            {"label": "A", "text": "pagos_membresias.csv"},
            {"label": "B", "text": "API REST externa"}
        ],
        "question_type": "multiple_choice",
        "selection_mode": "single"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "option_scores" in data
    assert len(data["option_scores"]) == 2
    assert "label" in data["option_scores"][0]
    assert "score" in data["option_scores"][0]
    assert "text" in data["option_scores"][0]

def test_canvas_question_low_confidence_fallback():
    response = client.post("/api/ai/canvas", json={
        "question": "zxcvbnmasdf qwerpoiu qawsedrf",
        "options": [],
        "question_type": "text"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["confidence"] <= 0.2
    assert "No se encontr" in data["answer"]

def test_resumen_clave_imported():
    """El archivo resumen_clave_proyecto.md debe importarse con prioridad alta."""
    response = client.post("/api/knowledge/import-folder?base_folder=test_material_tmp")
    assert response.status_code == 200
    
    # Search for content that's only in the resumen
    search_resp = client.post("/api/knowledge/search", json={"query": "stored procedures", "max_results": 5})
    assert search_resp.status_code == 200
    data = search_resp.json()
    assert len(data) >= 1
    assert "stored procedures" in data[0]["content"].lower()
