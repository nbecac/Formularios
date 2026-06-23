@echo off
echo Configurando el entorno para Formularios MVP...
cd /d "%~dp0\.."

if not exist ".venv" (
    echo Creando entorno virtual...
    python -m venv .venv
)

echo Activando entorno virtual e instalando dependencias...
call .venv\Scripts\activate.bat
pip install -r backend\requirements.txt

set PYTHONPATH=%cd%\backend
echo Inicializando base de datos con datos de prueba...
python -m app.seed_data

echo.
echo Configuracion completada con exito.
echo Para ejecutar el backend, utiliza: scripts\run_all.bat o backend\run_backend.bat
pause
