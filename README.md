<div align="center">

# Telecontrol AI

**Defect classification for technical support — hybrid ML + RAG + LLM system with a production API and web interface.**

*English* · [Português](#-português)

</div>

> 🇧🇷 **Português:** sistema de classificação de defeitos para atendimento técnico, combinando **RandomForest**, **RAG com busca vetorial FAISS** e **LLM (Azure OpenAI)** como fallback. Possui API FastAPI em produção, front-end Next.js e pipeline de treinamento completo.

## About

Telecontrol classifies customer-reported defects from free-text descriptions and returns a prediction with a confidence score. It combines a supervised model for speed and determinism with a retrieval-augmented generation layer that grounds answers in 164 historical cases, falling back to an LLM when needed.

## Architecture

```
Free-text description
        │
        ▼
┌───────────────────┐   ┌──────────────────────────┐
│ RandomForest      │   │ RAG — FAISS vector search│
│ classificador_    │   │ + 164 historical cases   │
│ defeitos.pkl      │   │ classificador_semantico  │
└─────────┬─────────┘   └────────────┬─────────────┘
          │                          │
          └──────────┬───────────────┘
                     ▼
        ┌────────────────────────┐
        │ Azure OpenAI fallback  │
        │ (gpt-4.1-mini)         │
        └───────────┬────────────┘
                    ▼
        prediction + confidence + explanation
```

## Components

| Layer | Technology |
|---|---|
| **API** | FastAPI + Python, 4 endpoints (`/predict`, `/health`, `/feedback`, `/metricas`) |
| **Frontend** | Next.js 14 + React + Tailwind CSS, real-time classification and history |
| **ML** | RandomForest classifier, semantic embeddings, FAISS vector store |
| **LLM** | Azure OpenAI `gpt-4.1-mini` as grounded fallback |
| **Dataset** | 164 historical defect cases |

## Deployment

| Service | Status | URL |
|---|---|---|
| Frontend | ✅ Vercel | https://telecontrol-ai.vercel.app |
| Backend | ✅ Azure Container Instance | API docs at `/docs` |

Also configured for **Railway** (`railway.toml`), **Docker** (`Dockerfile`, `docker-compose.yml`) and **Nginx** (`nginx.conf`).

## Repository layout

```
telecon-ai/
├── api.py                    # FastAPI application (main entry point)
├── classificador.py          # defect classification logic
├── rag_classifier.py         # RAG pipeline with FAISS
├── training_pipeline.py      # end-to-end training
├── trainamento_modelo.py     # model training
├── treinar_embeddings.py     # embedding generation
├── upload_dados.py           # dataset ingestion
├── ml.py / azure_ml_integration.py
├── requirements.txt
├── Dockerfile · docker-compose.yml · railway.toml · nginx.conf
├── tests/ (test_integracao.py, test_azure_*.py, verify_deployment.py)
└── docs (deployment and setup guides)
```

## Getting started

```bash
git clone https://github.com/vitoriaayres/telecon-ai.git
cd telecon-ai
pip install -r requirements.txt

# configure your keys
cp .env.example .env
#   OPENAI_API_KEY / AZURE_OPENAI_* credentials

# train the models
python training_pipeline.py

# run the API
uvicorn api:app --reload
```

Automated verification:

```bash
python verify_deployment.py     # checks env, dependencies, models, dataset and endpoints
```

## Configuration

Copy `.env.example` to `.env` (or `.env.azure_template` for Azure) and fill in the credentials. Model files (`*.pkl`) are committed; the FAISS vector store and dataset are rebuilt by `training_pipeline.py`.

## 🇧🇷 Português

- **O que é:** sistema híbrido de classificação de defeitos que une ML supervisionado, RAG com busca vetorial e LLM como fallback.
- **Como funciona:** RandomForest para previsão rápida e determinística, FAISS + 164 casos históricos para recuperação contextual e Azure OpenAI (`gpt-4.1-mini`) quando a confiança é baixa.
- **Stack:** FastAPI (back-end), Next.js 14 + Tailwind (front-end), Scikit-learn + FAISS (ML), Azure OpenAI (LLM).
- **Deploy:** front-end na Vercel, back-end em Azure Container Instance; também pronto para Railway e Docker.
- **Como rodar:** `pip install -r requirements.txt`, configure o `.env`, rode `training_pipeline.py` e inicie com `uvicorn api:app --reload`.
- **Validação:** `verify_deployment.py` confere ambiente, dependências, modelos, dataset e endpoints de uma vez.

## Author

[Vitoria AYRES](https://github.com/vitoriaayres)
