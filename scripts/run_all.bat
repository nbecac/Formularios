@echo off
echo Iniciando el ecosistema Formularios AI Assistant...
echo.
echo =======================================================
echo INSTRUCCIONES PARA LA EXTENSION DE CHROME:
echo 1. Abre Chrome y ve a chrome://extensions/
echo 2. Activa el "Modo Desarrollador" (arriba a la derecha)
echo 3. Haz clic en "Cargar descomprimida"
echo 4. Selecciona la carpeta: %~dp0..\extension
echo 5. Abre docs\formulario_prueba.html para probar.
echo =======================================================
echo.
echo Levantando el backend...
cd /d "%~dp0\.."
call backend\run_backend.bat
