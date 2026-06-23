@echo off
cd /d "%~dp0"
.\.venv\Scripts\python.exe scripts\test_end_to_end.py
pause
