# Gemeinsames Image für die 3 Spezial-Agenten (Cal, Bubble, Higgsfield)
# Der konkrete Agent wird über das command in docker-compose.yml gewählt.
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Im Container läuft Ollama unter dem Service-Namen "ollama"
ENV OLLAMA_URL=http://ollama:11434
ENV AI_OS_ROOT=/app/ai-os

CMD ["uvicorn", "cal_agent:app", "--host", "0.0.0.0", "--port", "5301"]
