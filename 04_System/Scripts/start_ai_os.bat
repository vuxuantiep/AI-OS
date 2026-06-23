@echo off
title KI-Fabrik V2 - AI-OS Launcher
echo ========================================
echo     🏭 KI-Fabrik V2 System Launcher
echo ========================================
echo.

cd /d "%~dp0..\.."

echo [1/3] Pruefe Ollama...
ollama list >nul 2>&1
if %errorlevel% neq 0 (
    echo Starte Ollama...
    start /B ollama serve
    timeout /t 3 /nobreak >nul
)
echo ✅ Ollama bereit
echo.

echo [2/3] Installiere Abhaengigkeiten...
pip install flask psutil -q
echo.

echo [3/3] Starte KI-Fabrik V2...
echo.
echo Folgende Dienste werden gestartet:
echo   - Dashboard     (Port 5000)
echo   - MCP Server    (Port 5001)
echo   - RAG Pipeline  (Port 5002)
echo   - API Gateway   (Port 5100)
echo   - Workflow Eng. (Port 5200)
echo   - Agent System  (Port 5300)
echo   - Monitoring    (Port 5400)
echo.

start "" http://localhost:5000
python 04_System/Scripts/start_ai_os.py

pause