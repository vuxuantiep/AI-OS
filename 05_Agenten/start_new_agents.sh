#!/bin/bash
# Startet die 3 neuen Spezial-Agenten (Cal, Bubble, Higgsfield)
cd "$(dirname "$0")/agents"

echo "🚀 Starte 3 neue KI-Agenten..."
uvicorn cal_agent:app --port 5301 --reload &
uvicorn bubble_agent:app --port 5302 --reload &
uvicorn higgsfield_agent:app --port 5303 --reload &
echo "✅ Cal Agent: :5301 | Bubble Agent: :5302 | Higgsfield Agent: :5303"
wait
