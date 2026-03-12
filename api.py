from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import json
import joblib
import numpy as np
from ml import ClassificadorDefeitos
from typing import List
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="API - Classificador de Defeitos")

# CORS - permite chamadas do frontend Next.js
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Carregamento dos modelos ──────────────────────────────────────────────────
# Tenta o modelo semântico (sentence-transformers) primeiro; cai no RandomForest

modelo_semantico = None
sentence_encoder = None
modelo_tipo = "nenhum"

SEMANTICO_PKL = "classificador_semantico.pkl"
RANDOMFOREST_PKL = "classificador_defeitos.pkl"

if os.path.exists(SEMANTICO_PKL):
    try:
        from sentence_transformers import SentenceTransformer
        payload = joblib.load(SEMANTICO_PKL)
        sentence_encoder = SentenceTransformer(payload["modelo_embed"])
        modelo_semantico = payload["clf"]
        modelo_tipo = "semantico"
        print(f"✅ Modelo semântico ({payload['modelo_embed']}) carregado")
    except Exception as e:
        print(f"⚠️  Falha ao carregar modelo semântico: {e}")

# Fallback: RandomForest + TF-IDF
classificador = None
if modelo_tipo == "nenhum":
    try:
        if not os.path.exists(RANDOMFOREST_PKL):
            raise FileNotFoundError("Modelo não encontrado. Execute trainamento_modelo.py primeiro.")
        classificador = ClassificadorDefeitos(RANDOMFOREST_PKL)
        modelo_tipo = "randomforest"
        print("✅ Modelo RandomForest carregado (fallback)")
    except Exception as e:
        print(f"⚠️ Erro ao carregar modelo: {e}")

# ── Groq LLM ─────────────────────────────────────────────────────────────────
groq_client = None
GROQ_MODEL  = "llama-3.1-8b-instant"

_groq_key = os.getenv("GROQ_API_KEY", "")
if _groq_key:
    try:
        from groq import Groq
        groq_client = Groq(api_key=_groq_key)
        print(f"✅ Groq ({GROQ_MODEL}) pronto")
    except Exception as e:
        print(f"⚠️  Groq não inicializado: {e}")
else:
    print("ℹ️  GROQ_API_KEY não definida — descrições serão geradas localmente")


def _fallback_enriquecimento(candidatos: list) -> list:
    """Gera textos locais quando Groq não está disponível."""
    return [
        {
            "descricao": f"Possível causa identificada com base em ordens de serviço anteriores com sintoma similar.",
            "acao_recomendada": f"Inspecionar o componente '{c['defeito']}'. Consultar manual técnico específico do equipamento."
        }
        for c in candidatos
    ]


def enriquecer_todos_com_llm(reclamacao: str, candidatos: list) -> list:
    """
    Enriquece todos os candidatos (top-3) com descrição e ação via Groq em uma única chamada.
    candidatos: list[dict] com chaves 'defeito' e 'confianca_pct'
    Retorna: list[dict] com chaves 'descricao' e 'acao_recomendada'
    """
    if not groq_client or not candidatos:
        return _fallback_enriquecimento(candidatos)

    lista_defeitos = "\n".join(
        [f"{i+1}. {c['defeito']}" for i, c in enumerate(candidatos)]
    )

    prompt = f"""Você é um técnico especialista em manutenção de equipamentos de refrigeração comercial (expositores, freezers, coolers de bebidas).

Um cliente relatou: "{reclamacao}"

Com base nessa reclamação, o sistema de IA identificou estes possíveis defeitos constatados:
{lista_defeitos}

Para cada defeito, escreva em português brasileiro:
- "descricao": explicação técnica direta em 1-2 frases de por que esse defeito causaria a reclamação do cliente
- "acao_recomendada": passo-a-passo conciso para o técnico de campo diagnosticar e resolver

Responda APENAS com um array JSON de {len(candidatos)} objetos, nesta ordem:
[
  {{"descricao": "...", "acao_recomendada": "..."}},
  {{"descricao": "...", "acao_recomendada": "..."}},
  {{"descricao": "...", "acao_recomendada": "..."}}
]
Sem texto adicional fora do JSON."""

    try:
        chat = groq_client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=600,
        )
        raw = chat.choices[0].message.content.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        parsed = json.loads(raw)
        # Garante que temos um item para cada candidato
        if isinstance(parsed, list) and len(parsed) >= len(candidatos):
            return parsed[:len(candidatos)]
        raise ValueError(f"Resposta com tamanho inesperado: {len(parsed)}")
    except Exception as e:
        print(f"⚠️  Erro Groq (enriquecer_todos): {e}")
        return _fallback_enriquecimento(candidatos)


FEEDBACK_LOG = []
CAMINHO_FEEDBACK = 'feedback_log.json'

def carregar_feedback():
    """Carrega feedback do arquivo se existir"""
    global FEEDBACK_LOG
    if os.path.exists(CAMINHO_FEEDBACK):
        with open(CAMINHO_FEEDBACK, 'r') as f:
            FEEDBACK_LOG = json.load(f)

def salvar_feedback():
    """Persiste feedback em arquivo"""
    with open(CAMINHO_FEEDBACK, 'w') as f:
        json.dump(FEEDBACK_LOG, f, indent=2, ensure_ascii=False)

# Carrega feedback ao iniciar
carregar_feedback()


MANUAIS_TECNICOS = {
    "Rele Queimado":                      "https://suaempresa.com/manuais/rele-queimado.pdf",
    "Relé queimado":                      "https://suaempresa.com/manuais/rele-queimado.pdf",
    "Controlador com defeito":            "https://suaempresa.com/manuais/controlador.pdf",
    "Controlador":                        "https://suaempresa.com/manuais/controlador.pdf",
    "Compressor com defeito":             "https://suaempresa.com/manuais/compressor.pdf",
    "Fonte de led queimado":              "https://suaempresa.com/manuais/fonte-led.pdf",
    "Equipamento em curto":               "https://suaempresa.com/manuais/curto-eletrico.pdf",
    "Porta com defeito":                  "https://suaempresa.com/manuais/porta.pdf",
    "Evaporador com vazamento":           "https://suaempresa.com/manuais/evaporador.pdf",
    "Evaporador Obstruído":               "https://suaempresa.com/manuais/evaporador.pdf",
    "Bloqueio no Evaporador":             "https://suaempresa.com/manuais/evaporador.pdf",
    "Bandeja do Evaporador Danificada":   "https://suaempresa.com/manuais/bandeja.pdf",
    "Bandeja do Evaporador solta":        "https://suaempresa.com/manuais/bandeja.pdf",
    "Hélice de Micromotor Evaporador Quebrad": "https://suaempresa.com/manuais/micromotor.pdf",
    "Transformador queimado":             "https://suaempresa.com/manuais/transformador.pdf",
    "Termostato com defeito":             "https://suaempresa.com/manuais/termostato.pdf",
    "Grade quebrada":                     "https://suaempresa.com/manuais/grade.pdf",
    "Plug quebrado":                      "https://suaempresa.com/manuais/plug.pdf",
    "Falta de produto":                   "https://suaempresa.com/manuais/reposicao.pdf",
    "Contaminado":                        "https://suaempresa.com/manuais/higienizacao.pdf",
    "Contaminado por motivo pragas":      "https://suaempresa.com/manuais/dedetizacao.pdf",
    "Equipamento desnivelado":            "https://suaempresa.com/manuais/nivelamento.pdf",
    "Não tem defeito":                    "https://suaempresa.com/manuais/sem-defeito.pdf",
    "Sem defeito":                        "https://suaempresa.com/manuais/sem-defeito.pdf",
    "Vazamento de Gás Refrigerante":      "https://suaempresa.com/manuais/gas-refrigerante.pdf",
}

# Carrega as classes treinadas (para categorização)
CLASSES_PATH = 'classificador_defeitos_classes.pkl'
CLASSES = joblib.load(CLASSES_PATH) if os.path.exists(CLASSES_PATH) else []


class ReclamacaoRequest(BaseModel):
    texto_cliente: str

class FeedbackRequest(BaseModel):
    texto_cliente: str
    defeito_sugerido: str
    defeito_correto: str
    tecnico_id: str

@app.post("/predict")
async def prever_defeito(req: ReclamacaoRequest):
    """Prediz os 3 defeitos mais prováveis baseado na reclamação do cliente"""

    if modelo_tipo == "nenhum":
        raise HTTPException(status_code=503, detail="Nenhum modelo carregado")

    try:
        # ── Modelo semântico (sentence-transformers + LogisticRegression) ──
        if modelo_tipo == "semantico":
            emb = sentence_encoder.encode([req.texto_cliente])
            probs = modelo_semantico.predict_proba(emb)[0]
            classes = modelo_semantico.classes_
            top3_idx = np.argsort(probs)[::-1][:3]
            causa_raiz = []  # embeddings não têm palavras-chave explícitas

        # ── Fallback: RandomForest + TF-IDF ──
        else:
            pipeline = classificador.pipeline
            classes = pipeline.classes_
            probs = pipeline.predict_proba([req.texto_cliente])[0]
            top3_idx = np.argsort(probs)[::-1][:3]
            causa_raiz = classificador.extrair_causa_raiz(req.texto_cliente)

        resultados = []
        for rank, idx in enumerate(top3_idx, start=1):
            defeito = classes[idx]
            confianca = float(probs[idx])
            if confianca < 0.01:
                break
            resultados.append({
                "rank": rank,
                "defeito_sugerido": defeito,
                "confianca": round(confianca, 4),
                "confianca_pct": round(confianca * 100, 1),
                "documentacao": MANUAIS_TECNICOS.get(defeito, ""),
                "descricao_llm": "",
                "acao_recomendada_llm": ""
            })

        # ── Enriquecer todos os candidatos com LLM em uma única chamada ──────
        if resultados:
            candidatos = [{"defeito": r["defeito_sugerido"], "confianca_pct": r["confianca_pct"]} for r in resultados]
            enriched = enriquecer_todos_com_llm(req.texto_cliente, candidatos)
            for i, llm in enumerate(enriched):
                resultados[i]["descricao_llm"] = llm.get("descricao", "")
                resultados[i]["acao_recomendada_llm"] = llm.get("acao_recomendada", "")

        return {
            "resultados": resultados,
            "texto_analisado": req.texto_cliente,
            "total_classes": int(len(classes)),
            "total_registros": 164,
            "modelo_ativo": modelo_tipo
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro ao processar: {str(e)}")

@app.post("/feedback")
async def registrar_feedback(req: FeedbackRequest):
    """Registra feedback sobre a precisão da predição"""
    
    try:
        # Valida se o modelo acertou
        modelo_acertou = req.defeito_sugerido == req.defeito_correto
        
        # Estrutura do feedback
        feedback_entry = {
            "texto_cliente": req.texto_cliente,
            "defeito_sugerido": req.defeito_sugerido,
            "defeito_correto": req.defeito_correto,
            "modelo_acertou": modelo_acertou,
            "tecnico_id": req.tecnico_id
        }
        # Adiciona ao log
        FEEDBACK_LOG.append(feedback_entry)
        
        # Persiste em arquivo
        salvar_feedback()
        
        return {
            "status": "Feedback salvo com sucesso!",
            "modelo_acertou": modelo_acertou,
            "total_feedbacks": len(FEEDBACK_LOG)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro ao salvar feedback: {str(e)}")

@app.get("/health")
async def health_check():
    """Verifica saúde da API e disponibilidade do modelo"""
    return {
        "status": "ok",
        "modelo_carregado": modelo_tipo != "nenhum",
        "modelo_ativo": modelo_tipo,
        "total_feedbacks": len(FEEDBACK_LOG)
    }

@app.get("/metricas")
async def obter_metricas():
    """Retorna métricas de desempenho do modelo baseado em feedback"""
    if not FEEDBACK_LOG:
        return {"total_feedbacks": 0, "taxa_acerto": 0.0, "taxa_erro": 0.0}
    
    acertos = sum(1 for f in FEEDBACK_LOG if f["modelo_acertou"])
    total = len(FEEDBACK_LOG)
    
    return {
        "total_feedbacks": total,
        "acertos": acertos,
        "erros": total - acertos,
        "taxa_acerto": round(acertos / total, 2),
        "taxa_erro": round((total - acertos) / total, 2)
    }