@echo off
title Hermes - AI-OS Backend
cd /d "%~dp0"

echo ============================================
echo   Hermes - Autonomer Mitarbeiter des AI-OS
echo   Backend startet auf http://localhost:8000
echo ============================================
echo.

rem Browser oeffnen, sobald der Server hochgefahren ist (2s Vorlauf)
start /b cmd /c "timeout /t 3 /nobreak >nul && start "" http://localhost:8000/ui"

uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
pause
