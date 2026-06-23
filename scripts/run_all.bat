@echo off
echo Iniciando Formularios AI Assistant MVP...
cd /d "%~dp0\.."

if not exist ".venv" (
    echo El entorno virtual no existe. Ejecuta scripts\setup.bat primero.
    pause
    exit /b
)

echo Iniciando backend FastAPI localmente...
call .venv\Scripts\activate.bat
set PYTHONPATH=%cd%\backend
cd backend
start cmd /k "uvicorn app.main:app --reload --host 127.0.0.1 --port 8000"

echo Backend iniciado en puerto 8000.
echo Abre tu navegador en Chrome, carga la extension e ingresa a docs/formulario_prueba.html
pause
