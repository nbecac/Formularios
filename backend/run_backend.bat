@echo off
cd /d "%~dp0\.."
call .venv\Scripts\activate.bat
set PYTHONPATH=%cd%\backend
cd backend
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
