@echo off
cd /d "%~dp0.."

echo Verificando entorno virtual...
if not exist ".venv" (
    echo [ERROR] No existe .venv.
    pause
    exit /b 1
)

echo Verificando .env...
if not exist ".env" (
    echo [INFO] .env no existe. Creando desde .env.example...
    copy .env.example .env >nul
    echo Completa GEMINI_API_KEY en .env y vuelve a correr
    pause
    exit /b 1
)

findstr /C:"GEMINI_API_KEY=" .env >nul
if %errorlevel% neq 0 (
    echo [WARN] No se encontro GEMINI_API_KEY en .env
) else (
    for /f "tokens=1,2 delims==" %%a in ('findstr /C:"GEMINI_API_KEY=" .env') do (
        if "%%b"=="" (
            echo [WARN] GEMINI_API_KEY esta vacia en .env
        )
    )
)

echo Iniciando backend...
call .\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload --app-dir backend
pause
