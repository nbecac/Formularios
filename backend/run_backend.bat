@echo off
echo Iniciando el backend de Formularios AI...
cd /d "%~dp0"
if not exist "..\.venv" (
    echo El entorno virtual no existe. Por favor, ejecuta scripts\setup.bat primero.
    exit /b 1
)
call "..\.venv\Scripts\activate.bat"
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
pause
