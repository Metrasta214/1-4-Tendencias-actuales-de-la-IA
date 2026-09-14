@echo off
title LinguaAI - Instalacion
python -m venv .venv
call .venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
if not exist ".env" copy /Y .env.example .env
echo.
echo Instalacion terminada.
echo Agrega tu OPENAI_API_KEY dentro de .env
pause
