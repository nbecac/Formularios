import os
import sys
import urllib.request
import urllib.error
import json
import socket
from pathlib import Path

def print_ok(msg): print(f"[OK] {msg}")
def print_fail(msg): print(f"[FAIL] {msg}")
def print_warn(msg): print(f"[WARN] {msg}")

def check_port(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0

def main():
    print("--- Diagnóstico de Configuración ---")
    print(f"Python: {sys.version.split()[0]}")
    
    root = Path(__file__).resolve().parents[1]
    print(f"Raíz del proyecto: {root}")
    
    if (root / ".venv").exists():
        print_ok(".venv existe")
    else:
        print_fail(".venv no encontrado")

    env_path = root / ".env"
    if env_path.exists():
        print_ok(".env encontrado")
    else:
        print_fail(".env no encontrado")
        
    try:
        from dotenv import load_dotenv
        load_dotenv(env_path, override=True)
    except ImportError:
        print_warn("python-dotenv no está instalado. Intenta ejecutar: pip install python-dotenv")
        
    ai_provider = os.getenv("AI_PROVIDER", "mock")
    ai_model = os.getenv("AI_MODEL", "gpt-4o-mini")
    print_ok(f"AI_PROVIDER={ai_provider}")
    print_ok(f"AI_MODEL={ai_model}")
    
    gemini_key = os.getenv("GEMINI_API_KEY", "")
    google_key = os.getenv("GOOGLE_API_KEY", "")
    
    if gemini_key:
        print_ok(f"GEMINI_API_KEY configurada, len={len(gemini_key)}")
    elif google_key:
        print_ok(f"GOOGLE_API_KEY configurada, len={len(google_key)}")
    else:
        print_fail("GEMINI_API_KEY y GOOGLE_API_KEY están vacías")
        print("-> Completa GEMINI_API_KEY en .env y vuelve a correr")
        
    memoria_path = root / "Material para responder" / "memoria_maestra_proyecto.md"
    if memoria_path.exists():
        text = memoria_path.read_text(encoding="utf-8")
        print_ok(f"memoria_maestra_proyecto.md encontrada (chars={len(text)}, lineas={len(text.splitlines())})")
    else:
        print_fail("memoria_maestra_proyecto.md no encontrada")
        
    if check_port(8000):
        print_warn("Puerto 8000 está OCUPADO (Backend corriendo)")
        try:
            req = urllib.request.Request("http://127.0.0.1:8000/health")
            with urllib.request.urlopen(req) as response:
                print_ok("Backend responde a /health")
        except Exception as e:
            print_fail(f"Backend no responde bien a /health: {e}")
            
        try:
            req = urllib.request.Request("http://127.0.0.1:8000/api/debug/status")
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode())
                print_ok(f"Backend /api/debug/status: ai_configured={data.get('ai_configured')}, key_source={data.get('key_source')}")
        except Exception as e:
            print_fail(f"Backend no responde bien a /api/debug/status: {e}")
    else:
        print_ok("Puerto 8000 está LIBRE")
        
    if check_port(5500):
        print_warn("Puerto 5500 está OCUPADO (Docs corriendo)")
    else:
        print_ok("Puerto 5500 está LIBRE")

if __name__ == "__main__":
    main()
