# Dockerfile para API Telecontrol
# Deploy em Azure Container Instances

FROM python:3.11-slim

# Define diretório de trabalho
WORKDIR /app

# Instala dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copia arquivos de requirements
COPY requirements.txt .

# Instala dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia código da aplicação
COPY api.py .
COPY ml.py .
COPY breakfix_web_agent.py .
COPY DATASET ./DATASET

# Copia modelos pré-treinados (necessários para execução)
COPY classificador_defeitos.pkl .
COPY classificador_defeitos_classes.pkl .
COPY classificador_semantico.pkl . || true

# Expõe porta
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

# Comando para iniciar API
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
