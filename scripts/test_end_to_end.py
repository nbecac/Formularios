import urllib.request
import urllib.error
import json
import sys

def post_json(url, data):
    req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        print(f"Error {e.code}: {e.read().decode()}")
        sys.exit(1)

def get_json(url):
    req = urllib.request.Request(url)
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        print(f"Error {e.code}: {e.read().decode()}")
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"No se pudo conectar a {url}. ¿Está corriendo el backend?")
        sys.exit(1)

def main():
    print("--- Prueba End-to-End ---")
    
    # 1. GET /health
    print("1. Probando GET /health...")
    health = get_json("http://127.0.0.1:8000/health")
    print(f"   -> OK: {health['status']}")
    
    # 2. GET /api/debug/status
    print("\n2. Probando GET /api/debug/status...")
    status = get_json("http://127.0.0.1:8000/api/debug/status")
    print(f"   -> ai_provider: {status.get('ai_provider')}")
    print(f"   -> ai_configured: {status.get('ai_configured')}")
    print(f"   -> key_source: {status.get('key_source')}")
    
    # 3. Diagnóstico claro
    if not status.get("ai_configured"):
        print("\n[ERROR] ai_configured: false")
        print("Solución: Falta configurar GEMINI_API_KEY en .env")
        sys.exit(1)
        
    # 4. Importar material
    print("\n4. Importando material...")
    import_res = post_json("http://127.0.0.1:8000/api/knowledge/import-folder?base_folder=Material%20para%20responder", {})
    print(f"   -> Importados: {import_res.get('fuentes_importadas')} fuentes, {import_res.get('chunks_creados')} chunks")
    
    # Helper para preguntas
    def probar_pregunta(nombre, pregunta, opciones):
        print(f"\nProbando pregunta: {nombre}")
        print(f"Pregunta: {pregunta}")
        res = post_json("http://127.0.0.1:8000/api/ai/canvas", {
            "question": pregunta,
            "options": opciones,
            "question_type": "multiple_choice",
            "selection_mode": "single"
        })
        print(f"   -> mode: {res.get('mode')}")
        print(f"   -> selected_option: {res.get('selected_option')}")
        print(f"   -> confidence: {res.get('confidence')}")
        print(f"   -> explanation: {res.get('explanation')}")
        fuentes = res.get('sources', [])
        usa_memoria = any(f.get('section') == 'memoria_maestra' for f in fuentes)
        print(f"   -> memoria_maestra usada: {'Sí' if usa_memoria else 'No'}")
        
    # 5. Pregunta E2 pagos
    probar_pregunta(
        "E2 Pagos", 
        "Según la implementación de la Entrega 2, ¿cómo se resolvió el sistema de pagos de membresías?",
        [
            {"label": "A", "text": "API externa Transbank"},
            {"label": "B", "text": "CSV pagos_membresias/datos cargados"},
            {"label": "C", "text": "No se implementó sistema de pagos"},
            {"label": "D", "text": "Trigger automático"}
        ]
    )

    # 6. Pregunta E1
    probar_pregunta(
        "E1 Socio-Beneficio", 
        "En el Modelo Entidad-Relación de la Entrega 1, ¿cómo se modela la relación entre Socio y Beneficio?",
        [
            {"label": "A", "text": "Relación 1 a 1"},
            {"label": "B", "text": "Relación N a M, donde un socio puede acceder a muchos beneficios y un beneficio aplica a muchos socios."},
            {"label": "C", "text": "Relación 1 a N"},
            {"label": "D", "text": "Herencia"}
        ]
    )
    
    # 7. Pregunta E3 PHP
    probar_pregunta(
        "E3 Arquitectura", 
        "¿Qué arquitectura y lenguaje se utilizó para la aplicación web en la Entrega 3?",
        [
            {"label": "A", "text": "React y Node.js"},
            {"label": "B", "text": "PHP y PostgreSQL sin framework React"},
            {"label": "C", "text": "Angular y MySQL"},
            {"label": "D", "text": "Vue y MongoDB"}
        ]
    )
    
    # 8. Pregunta trampa React/E4
    probar_pregunta(
        "Trampa React/E4", 
        "¿Cuál es el comando exacto para clonar el repositorio de React nativo utilizado en la interfaz de la E4?",
        [
            {"label": "A", "text": "npx create-react-app frontend-dccolo"},
            {"label": "B", "text": "git clone https://github.com/dccolo/react-app.git"},
            {"label": "C", "text": "npm install react-native-cli"},
            {"label": "D", "text": "vue create frontend-app"}
        ]
    )
    
    print("\n[OK] Fin de la prueba End-to-End.")

if __name__ == "__main__":
    main()
