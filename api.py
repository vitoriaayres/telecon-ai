from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import json
import re
import unicodedata
import joblib
import numpy as np
import pandas as pd
import asyncio
import threading
from ml import ClassificadorDefeitos
from typing import List
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="API Break FIX - Classificador de Defeitos")

# ── Constantes ────────────────────────────────────────────────────────────────
TOTAL_REGISTROS_TREINO = 164 # TODO: Tornar dinâmico a partir dos metadados do modelo

# CORS - permite chamadas do frontend Next.js
origins_str = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins_str.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
        print(f"[OK] Modelo semântico ({payload['modelo_embed']}) carregado")
    except Exception as e:
        print(f"[AVISO] Falha ao carregar modelo semântico: {e}")

# Fallback: RandomForest + TF-IDF
classificador = None
if modelo_tipo == "nenhum":
    try:
        if not os.path.exists(RANDOMFOREST_PKL):
            raise FileNotFoundError("Modelo não encontrado. Execute trainamento_modelo.py primeiro.")
        classificador = ClassificadorDefeitos(RANDOMFOREST_PKL)
        modelo_tipo = "randomforest"
        print("[OK] Modelo RandomForest carregado (fallback)")
    except Exception as e:
        print(f"[AVISO] Erro ao carregar modelo: {e}")

# ── Enriquecimento local (sem Azure/LLM externo) ────────────────────────────
print("[INFO] Enriquecimento LLM externo desativado — usando textos locais")


def _fallback_enriquecimento(candidatos: list) -> list:
    """Gera textos locais quando LLM externo não está disponível."""
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
    return _fallback_enriquecimento(candidatos)


FEEDBACK_LOG = []
CAMINHO_FEEDBACK = 'feedback_log.json'
_feedback_lock = threading.Lock()

def carregar_feedback():
    """Carrega feedback do arquivo se existir."""
    global FEEDBACK_LOG
    if os.path.exists(CAMINHO_FEEDBACK):
        try:
            with open(CAMINHO_FEEDBACK, 'r', encoding='utf-8') as f:
                FEEDBACK_LOG = json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"[AVISO] Não foi possível carregar o log de feedback: {e}")
            FEEDBACK_LOG = []

async def salvar_feedback():
    """Persiste feedback em arquivo de forma assíncrona e thread-safe."""
    def _write_file():
        # Usa um lock para evitar race conditions se duas requisições
        # tentarem escrever no arquivo ao mesmo tempo.
        with _feedback_lock:
            with open(CAMINHO_FEEDBACK, 'w', encoding='utf-8') as f:
                json.dump(FEEDBACK_LOG, f, indent=2, ensure_ascii=False)

    await asyncio.to_thread(_write_file)

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

def _normalizar_chave(texto: str) -> str:
    """Normaliza chaves para o dicionário de manuais, tratando acentos e caixa."""
    if not isinstance(texto, str):
        return texto
    # Remove acentos
    t = unicodedata.normalize("NFD", texto)
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    # Minúsculas e strip
    t = t.lower().strip()
    # Colapsa espaços múltiplos
    t = re.sub(r"\s+", " ", t)
    return t

MANUAIS_TECNICOS_NORMALIZADO = {_normalizar_chave(k): v for k, v in MANUAIS_TECNICOS.items()}


def _carregar_contexto_dataset() -> pd.DataFrame:
    """Carrega colunas mínimas dos datasets para enriquecer a busca web."""
    frames: list[pd.DataFrame] = []

    d1_path = os.path.join("DATASET", "dataset_1.csv")
    if os.path.exists(d1_path):
        d1 = pd.read_csv(d1_path, usecols=["descricao_defeito_reclamado", "descricao_defeito_constatado_ref"])
        d1 = d1.rename(
            columns={
                "descricao_defeito_reclamado": "reclamado",
                "descricao_defeito_constatado_ref": "constatado",
            }
        )
        frames.append(d1)

    d2_path = os.path.join("DATASET", "dataset_2.csv")
    if os.path.exists(d2_path):
        d2 = pd.read_csv(d2_path, usecols=["defeito_reclamado_descricao", "defeito_constatado_descricao"])
        d2 = d2.rename(
            columns={
                "defeito_reclamado_descricao": "reclamado",
                "defeito_constatado_descricao": "constatado",
            }
        )
        frames.append(d2)

    if not frames:
        return pd.DataFrame(columns=["reclamado", "constatado", "constatado_norm"])

    df = pd.concat(frames, ignore_index=True)
    df = df[df["reclamado"].notna() & df["constatado"].notna()].copy()
    df["constatado_norm"] = df["constatado"].astype(str).map(_normalizar_chave)
    return df


DATASET_CONTEXTO_DF = _carregar_contexto_dataset()


def _extrair_exemplos_dataset(defeitos: list[str], limite: int = 3) -> list[str]:
    """Retorna exemplos de sintomas históricos alinhados aos defeitos sugeridos."""
    if DATASET_CONTEXTO_DF.empty or not defeitos:
        return []

    defeitos_norm = [_normalizar_chave(d) for d in defeitos if d]
    if not defeitos_norm:
        return []

    filtrado = DATASET_CONTEXTO_DF[DATASET_CONTEXTO_DF["constatado_norm"].isin(defeitos_norm)]
    if filtrado.empty:
        return []

    exemplos = []
    for texto in filtrado["reclamado"].astype(str).head(limite * 3):
        t = re.sub(r"\s+", " ", texto).strip()
        if t and t not in exemplos:
            exemplos.append(t)
        if len(exemplos) >= limite:
            break
    return exemplos


def _montar_query_busca_contextual(
    texto_cliente: str,
    tipo_produto: str | None,
    segmento: str | None,
    regiao: str | None,
    top_defeitos: list[str],
    exemplos_dataset: list[str],
) -> str:
    partes = [
        "Contexto: manutenção técnica de equipamentos de refrigeração comercial.",
        f"Sintoma relatado: {texto_cliente.strip()}",
    ]

    filtros = [f for f in [tipo_produto, segmento, regiao] if f and f.strip()]
    if filtros:
        partes.append("Filtros operacionais: " + ", ".join(f.strip() for f in filtros))

    if top_defeitos:
        partes.append("Hipóteses do classificador ML: " + ", ".join(top_defeitos[:3]))

    if exemplos_dataset:
        partes.append("Exemplos históricos do dataset: " + " | ".join(exemplos_dataset[:3]))

    partes.append(
        "Objetivo da busca: causas técnicas, testes de diagnóstico e ações corretivas para refrigeração comercial; ignorar conteúdos médicos, psicológicos ou fora de manutenção de equipamentos."
    )
    return "\n".join(partes)


def _montar_query_busca_sintoma(
    texto_cliente: str,
    tipo_produto: str | None,
    segmento: str | None,
) -> str:
    """Query alternativa focada no sintoma real para aumentar diversidade e utilidade."""
    partes = [
        "Busca técnica de manutenção em refrigeração comercial.",
        f"Sintoma principal: {texto_cliente.strip()}",
    ]
    if tipo_produto and tipo_produto.strip():
        partes.append(f"Equipamento: {tipo_produto.strip()}")
    if segmento and segmento.strip():
        partes.append(f"Cenário operacional: {segmento.strip()}")

    partes.append(
        "Retornar diagnóstico, checklist de inspeção e ações corretivas para equipamento de refrigeração. Excluir contexto médico e saúde humana."
    )
    return "\n".join(partes)


def _filtrar_resultados_contextuais(
    resultados: list[dict],
    texto_cliente: str,
    top_defeitos: list[str],
    tipo_produto: str | None,
    exemplos_dataset: list[str],
) -> list[dict]:
    """
    Re-ranqueia resultados por aderência ao contexto técnico.
    Mantém variedade sem perder contexto de ML + dataset.
    """
    if not resultados:
        return []

    hard_domain_keywords = {
        "refriger", "geladeira", "freezer", "expositor", "evaporador", "compressor",
        "termostato", "rele", "relé", "camara fria", "câmara fria", "condensador", "refrigerante",
        "manutencao", "manutenção", "diagnostico", "diagnóstico",
    }
    tipo_norm = _normalizar_chave(tipo_produto) if tipo_produto and tipo_produto.strip() else ""

    stop_tokens = {
        "com", "sem", "motivo", "por", "para", "nao", "não", "defeito", "equipamento", "problema"
    }
    defeito_tokens: set[str] = set()
    for defeito in top_defeitos:
        d_norm = _normalizar_chave(defeito)
        for token in d_norm.split():
            if len(token) > 3 and token not in stop_tokens:
                defeito_tokens.add(token)

    sintomas_tokens: set[str] = set()
    for origem in [texto_cliente, " ".join(exemplos_dataset[:3])]:
        norm = _normalizar_chave(origem)
        for token in norm.split():
            if len(token) > 3 and token not in stop_tokens:
                sintomas_tokens.add(token)

    medical_keywords = {
        "ouvido", "zumbido", "hiperacusia", "tinnitus", "audi", "cefaleia", "dor de cabeca", "dor de cabeça", "psicolog"
    }

    scored: list[tuple[float, dict]] = []
    for item in resultados:
        texto = " ".join([
            str(item.get("title", "")),
            str(item.get("content", "")),
            str(item.get("url", "")),
        ])
        texto_norm = _normalizar_chave(texto)

        domain_hits = sum(1 for k in hard_domain_keywords if k in texto_norm)
        defect_hits = sum(1 for t in defeito_tokens if t in texto_norm)
        symptom_hits = sum(1 for t in sintomas_tokens if t in texto_norm)
        tipo_hit = 1 if (tipo_norm and tipo_norm in texto_norm) else 0
        medical_hits = sum(1 for m in medical_keywords if m in texto_norm)

        # Penaliza fortemente desvio médico sem qualquer evidência técnica.
        if medical_hits > 0 and domain_hits == 0 and defect_hits == 0 and tipo_hit == 0:
            continue

        # Peso maior para sintoma real e tipo de equipamento; ML atua como contexto, não dominância.
        score = (domain_hits * 2.5) + (defect_hits * 1.0) + (symptom_hits * 2.0) + (tipo_hit * 3.0)

        # Evita queda para fallback excessivo: aceita baixa aderência, mas prioriza melhor score.
        if score > 0:
            scored.append((score, item))

    if not scored:
        return []

    scored.sort(key=lambda x: x[0], reverse=True)

    selecionados: list[dict] = []
    seen = set()
    for _, item in scored:
        key = (str(item.get("url", "")).strip(), str(item.get("title", "")).strip())
        if key in seen:
            continue
        seen.add(key)
        selecionados.append(item)
        if len(selecionados) >= 4:
            break

    return selecionados


def _gerar_fallback_contextual(
    texto_cliente: str,
    top_defeitos: list[str],
    exemplos_dataset: list[str],
    resultados_brutos: list[dict] | None = None,
) -> list[dict]:
    """Gera resposta contextual dinâmica quando a web retorna fraca/fora de contexto."""
    defeitos_txt = ", ".join(top_defeitos[:3]) if top_defeitos else "sem hipótese definida"
    exemplos_txt = " | ".join(exemplos_dataset[:3]) if exemplos_dataset else "sem exemplos históricos disponíveis"

    checklist = []
    for defeito in top_defeitos[:3]:
        d = _normalizar_chave(defeito)
        if "compressor" in d:
            checklist.append("Verificar corrente do compressor, relé de partida e protetor térmico")
        elif "evaporador" in d:
            checklist.append("Inspecionar obstrução, gelo excessivo e circulação de ar no evaporador")
        elif "porta" in d:
            checklist.append("Checar alinhamento da porta, vedação e dobradiças")
        elif "termostato" in d:
            checklist.append("Validar calibração e resposta elétrica do termostato")
        elif "rele" in d or "relé" in d:
            checklist.append("Testar relé, continuidade e sinais de queima")

    if not checklist:
        checklist = ["Executar checklist elétrico e térmico padrão do equipamento"]

    fallback = [
        {
            "title": f"Resumo técnico contextual: {texto_cliente[:80]}",
            "url": "internal://dataset-context",
            "content": (
                f"Sintoma informado: {texto_cliente}. "
                f"Hipóteses do ML: {defeitos_txt}. "
                f"Evidências do dataset: {exemplos_txt}. "
                "Ação sugerida: validar em campo os componentes ligados às hipóteses do ML."
            ),
        },
        {
            "title": "Checklist técnico sugerido",
            "url": "internal://dataset-checklist",
            "content": " ; ".join(checklist[:3]),
        },
    ]

    # Inclui até 2 candidatos web brutos como referência auxiliar (não validados),
    # para reduzir repetição e abrir trilhas de investigação.
    if resultados_brutos:
        adicionados = 0
        for item in resultados_brutos:
            title = str(item.get("title", "")).strip()
            url = str(item.get("url", "")).strip()
            content = str(item.get("content", "")).strip()
            if not (title or content):
                continue
            fallback.append(
                {
                    "title": f"Referência externa auxiliar: {title or 'resultado web'}",
                    "url": url or "internal://web-candidate",
                    "content": (content[:320] + "...") if len(content) > 320 else content,
                }
            )
            adicionados += 1
            if adicionados >= 2:
                break

    return fallback

# Carrega as classes treinadas (para categorização)
CLASSES_PATH = 'classificador_defeitos_classes.pkl'
CLASSES = joblib.load(CLASSES_PATH) if os.path.exists(CLASSES_PATH) else []


class ReclamacaoRequest(BaseModel):
    texto_cliente: str
    tipo_produto: str | None = None
    segmento: str | None = None
    regiao: str | None = None

class WebSearchRequest(BaseModel):
    texto_cliente: str
    tipo_produto: str | None = None
    segmento: str | None = None
    regiao: str | None = None
    top_defeitos: list[str] | None = None
    exemplos_dataset: list[str] | None = None

class FeedbackRequest(BaseModel):
    texto_cliente: str
    defeito_sugerido: str
    defeito_correto: str
    tecnico_id: str

@app.post("/predict")
async def prever_defeito(req: ReclamacaoRequest):
    """
    Prediz os 3 defeitos mais prováveis e indica se uma busca web é sugerida.
    """
    if modelo_tipo == "nenhum":
        raise HTTPException(status_code=503, detail="Nenhum modelo carregado")

    partes_texto = []
    if req.texto_cliente and req.texto_cliente.strip():
        partes_texto.append(req.texto_cliente.strip())
    
    filtros = [f for f in [req.tipo_produto, req.segmento, req.regiao] if f and f.strip()]
    if filtros:
        partes_texto.append("Filtros: " + ", ".join(filtros))
        
    texto_final = " | ".join(partes_texto)
    
    if not texto_final:
        raise HTTPException(status_code=400, detail="Por favor, forneça a reclamação do cliente ou selecione pelo menos um filtro.")

    try:
        # ── Classificação (Semântica ou RandomForest) ──
        if modelo_tipo == "semantico":
            embeddings = sentence_encoder.encode([texto_final], convert_to_tensor=False)
            probs = modelo_semantico.predict_proba(embeddings)[0]
            top_indices = np.argsort(probs)[-3:][::-1]
            candidatos = [
                {"defeito": modelo_semantico.classes_[i], "confianca": probs[i]}
                for i in top_indices
            ]
        else: # RandomForest
            candidatos = classificador.prever_top_3(texto_final)

        # ── Enriquecimento e Formatação ──
        top_candidatos_enriquecidos = enriquecer_todos_com_llm(
            texto_final,
            [{"defeito": c["defeito"], "confianca_pct": f"{c['confianca']:.0%}"} for c in candidatos]
        )

        resultados_finais = []
        for i, (cand, enriquecido) in enumerate(zip(candidatos, top_candidatos_enriquecidos)):
            chave_manual = _normalizar_chave(cand["defeito"])
            resultados_finais.append({
                "rank": i + 1,
                "defeito_sugerido": cand["defeito"],
                "confianca": cand["confianca"],
                "confianca_pct": round(float(cand["confianca"]) * 100, 1),
                "documentacao": MANUAIS_TECNICOS_NORMALIZADO.get(chave_manual, ""),
                "descricao_llm": enriquecido.get("descricao", ""),
                "acao_recomendada_llm": enriquecido.get("acao_recomendada", ""),
            })
        
        # ── Lógica para sugerir busca web ──
        confianca_principal = candidatos[0]['confianca'] if candidatos else 0
        limiar_busca = float(os.getenv("BREAKFIX_REFLECT_THRESHOLD", "0.8"))
        sugere_busca = bool(confianca_principal < limiar_busca)
        top_defeitos = [c["defeito"] for c in candidatos[:3]]
        exemplos_dataset = _extrair_exemplos_dataset(top_defeitos, limite=3)

        return {
            "resultados": resultados_finais,
            "sugere_busca": sugere_busca,
            "texto_analisado": texto_final,
            "contexto_web": {
                "top_defeitos": top_defeitos,
                "exemplos_dataset": exemplos_dataset,
            },
            "total_classes": len(CLASSES),
            "total_registros": TOTAL_REGISTROS_TREINO,
            "modelo_ativo": modelo_tipo,
        }

    except Exception as e:
        print(f"[ERRO] /predict: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno ao processar a predição: {e}")

@app.post("/web-search")
async def buscar_na_web(req: WebSearchRequest):
    """Executa uma busca na web para a reclamação fornecida."""
    if not req.texto_cliente or not req.texto_cliente.strip():
        raise HTTPException(status_code=400, detail="O texto do cliente é obrigatório.")

    top_defeitos = req.top_defeitos or []
    exemplos_dataset = req.exemplos_dataset or []
    if not top_defeitos and not exemplos_dataset:
        raise HTTPException(
            status_code=400,
            detail="Contexto obrigatório ausente: execute /predict e envie top_defeitos ou exemplos_dataset.",
        )

    try:
        # O agente avalia a confiança e decide se busca ou não.
        # Como estamos em um endpoint dedicado, forçamos a busca.
        # A maneira mais simples é chamar o passo de busca diretamente.
        from breakfix_web_agent import web_search

        exemplos_dataset = exemplos_dataset or _extrair_exemplos_dataset(top_defeitos, limite=3)
        query_contextual = _montar_query_busca_contextual(
            texto_cliente=req.texto_cliente,
            tipo_produto=req.tipo_produto,
            segmento=req.segmento,
            regiao=req.regiao,
            top_defeitos=top_defeitos,
            exemplos_dataset=exemplos_dataset,
        )
        query_sintoma = _montar_query_busca_sintoma(
            texto_cliente=req.texto_cliente,
            tipo_produto=req.tipo_produto,
            segmento=req.segmento,
        )

        # Busca em duas estratégias para não repetir sempre o mesmo padrão.
        state_context = {"question": query_contextual}
        state_sintoma = {"question": query_sintoma}
        result_context = web_search(state_context)
        result_sintoma = web_search(state_sintoma)

        resultados_brutos = []
        resultados_brutos.extend(result_context.get("results", []))
        resultados_brutos.extend(result_sintoma.get("results", []))

        # Dedup inicial por URL+título
        vistos = set()
        unicos = []
        for item in resultados_brutos:
            key = (str(item.get("url", "")).strip(), str(item.get("title", "")).strip())
            if key in vistos:
                continue
            vistos.add(key)
            unicos.append(item)
        resultados_brutos = unicos

        resultados_contextuais = _filtrar_resultados_contextuais(
            resultados=resultados_brutos,
            texto_cliente=req.texto_cliente,
            top_defeitos=top_defeitos,
            tipo_produto=req.tipo_produto,
            exemplos_dataset=exemplos_dataset,
        )

        if not resultados_contextuais:
            resultados_contextuais = _gerar_fallback_contextual(
                texto_cliente=req.texto_cliente,
                top_defeitos=top_defeitos,
                exemplos_dataset=exemplos_dataset,
                resultados_brutos=resultados_brutos,
            )
            status = "fallback_context"
        else:
            status = "ok"
        
        return {
            "resultados": resultados_contextuais,
            "status": status,
            "query_usada": query_contextual,
            "query_secundaria": query_sintoma,
        }
    except Exception as e:
        print(f"[ERRO] /web-search: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno ao processar a busca na web: {e}")


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
        await salvar_feedback()
        
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

if __name__ == "__main__":
    import uvicorn
    print("[START] Subindo servidor Uvicorn em http://127.0.0.1:8000")
    uvicorn.run("api:app", host="127.0.0.1", port=8000, reload=True)