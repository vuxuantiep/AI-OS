@echo off
REM Startet die 3 neuen Spezial-Agenten (Cal, Bubble, Higgsfield) unter Windows
cd /d "%~dp0agents"

echo 🚀 Starte 3 neue KI-Agenten...
start "Cal Agent (5301)" python cal_agent.py
start "Bubble Agent (5302)" python bubble_agent.py
start "Higgsfield Agent (5303)" python higgsfield_agent.py
echo ✅ Cal Agent: :5301 ^| Bubble Agent: :5302 ^| Higgsfield Agent: :5303
