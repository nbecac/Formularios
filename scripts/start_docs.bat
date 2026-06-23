@echo off
cd /d "%~dp0.."
echo Iniciando servidor de documentacion en http://127.0.0.1:5500
.\.venv\Scripts\python.exe -m http.server 5500 --directory docs
pause
