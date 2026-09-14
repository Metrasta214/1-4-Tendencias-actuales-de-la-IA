@echo off
title LinguaAI - Backend
if not exist ".venv\Scripts\python.exe" (
    echo No existe el entorno virtual.
    echo Ejecuta primero setup.bat
    pause
    exit /b 1
)
call .venv\Scripts\activate
uvicorn api.index:app --reload --port 8000
pause
