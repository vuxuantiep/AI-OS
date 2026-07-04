@echo off
title AI-OS Dashboard
rem Startet NUR das Dashboard (Port 5000) mit dem venv-Python — unabhaengig von VSCode.
rem Ollama/LM Studio startet das Dashboard bei Bedarf selbst (LLM-Autostart),
rem alle weiteren Dienste lassen sich im Dashboard-Tab "Dienste" per Klick starten.

cd /d "%~dp0..\.."
set "AI_OS_ROOT=%CD%"

set "PY=%CD%\.venv\Scripts\python.exe"
if not exist "%PY%" set "PY=python"

start "" http://localhost:5000
"%PY%" "04_Infrastruktur\Gateway\ai_os_dashboard.py"
pause
