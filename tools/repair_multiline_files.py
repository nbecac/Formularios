import os
from pathlib import Path

def repair_file(filepath):
    path = Path(filepath)
    if not path.exists():
        return
        
    with open(path, 'rb') as f:
        content = f.read()
        
    content = content.replace(b'\r\n', b'\n')
    
    with open(path, 'wb') as f:
        f.write(content)
    print(f"Reparado: {filepath}")

def main():
    print("Reparando archivos de forma deterministica...")
    files_to_repair = [
        "backend/app/main.py",
        "backend/app/config.py",
        "backend/app/database.py",
        "backend/app/models.py",
        "backend/app/schemas.py",
        "backend/app/crud.py",
        "backend/app/ai_agent.py",
        "backend/app/form_analyzer.py",
        "backend/app/seed_data.py",
        "backend/app/utils.py",
        "backend/requirements.txt",
        "backend/tests/test_api_manual.py",
        "backend/tests/test_crud_api.py",
        "extension/manifest.json",
        "extension/popup.js",
        "extension/popup.html",
        "extension/contentScript.js",
        "scripts/setup.bat",
        "scripts/run_all.bat",
        "backend/run_backend.bat",
        "docs/formulario_prueba.html",
        "docs/reporte_implementacion.md",
        "docs/admin.html"
    ]
    
    for f in files_to_repair:
        repair_file(f)
        
    print("Reparacion completa.")

if __name__ == "__main__":
    main()
