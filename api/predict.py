"""
Vercel Serverless Function - Endpoint /api/predict
Compatível com Vercel Python Runtime
"""

import json
import os
import sys
from pathlib import Path

# Adiciona raiz do projeto ao path para importar módulos locais
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from ml import ClassificadorDefeitos
except ImportError:
    ClassificadorDefeitos = None


def handler(request):
    """
    Handler para Vercel Functions.
    request: objeto com método json() e atributos como method, headers
    """
    
    # CORS headers
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
        "Content-Type": "application/json",
    }
    
    # Preflight CORS
    if request.method == "OPTIONS":
        return {"statusCode": 200, "headers": headers}
    
    # Apenas POST
    if request.method != "POST":
        return {
            "statusCode": 405,
            "headers": headers,
            "body": json.dumps({"error": "Método não permitido"}),
        }
    
    try:
        # Parse JSON do body
        body = json.loads(request.body) if isinstance(request.body, str) else request.get_json()
        
        texto_cliente = body.get("texto_cliente", "").strip()
        tipo_produto = body.get("tipo_produto")
        segmento = body.get("segmento")
        regiao = body.get("regiao")
        
        # Validação
        has_text = len(texto_cliente) > 0
        has_filter = any([tipo_produto, segmento, regiao])
        
        if not has_text and not has_filter:
            return {
                "statusCode": 400,
                "headers": headers,
                "body": json.dumps({
                    "error": "Por favor, forneça a reclamação do cliente ou selecione pelo menos um filtro."
                }),
            }
        
        # Carrega classificador (simplificado para demo)
        # Em produção, você quer cachear isso ou usar modelo pré-treinado mínimo
        clf_path = os.path.join(project_root, "classificador_defeitos.pkl")
        
        if not os.path.exists(clf_path):
            return {
                "statusCode": 503,
                "headers": headers,
                "body": json.dumps({
                    "error": "Modelo não disponível em produção. Contacte administrador."
                }),
            }
        
        try:
            classificador = ClassificadorDefeitos(clf_path)
        except Exception as e:
            return {
                "statusCode": 503,
                "headers": headers,
                "body": json.dumps({
                    "error": f"Erro ao carregar modelo: {str(e)}"
                }),
            }
        
        # Predição
        try:
            resultado = classificador.prever(
                texto=texto_cliente,
                top_n=3
            )
            
            # Formata resposta
            response_data = {
                "resultados": [
                    {
                        "rank": i + 1,
                        "defeito_sugerido": r["defeito"],
                        "confianca": r.get("confianca", 0),
                        "confianca_pct": int(r.get("confianca", 0) * 100),
                        "documentacao": "https://suaempresa.com/manuais",
                        "descricao_llm": "Análise baseada no histórico de ordens de serviço.",
                        "acao_recomendada_llm": "Consultar manual técnico do equipamento.",
                    }
                    for i, r in enumerate(resultado)
                ],
                "texto_analisado": texto_cliente,
                "total_classes": 15,
                "total_registros": 164,
                "modelo_ativo": "randomforest",
                "sugere_busca": False,
                "contexto_web": {
                    "top_defeitos": [r["defeito"] for r in resultado],
                    "exemplos_dataset": [],
                }
            }
            
            return {
                "statusCode": 200,
                "headers": headers,
                "body": json.dumps(response_data),
            }
        
        except Exception as e:
            return {
                "statusCode": 500,
                "headers": headers,
                "body": json.dumps({
                    "error": f"Erro na predição: {str(e)}"
                }),
            }
    
    except json.JSONDecodeError:
        return {
            "statusCode": 400,
            "headers": headers,
            "body": json.dumps({"error": "JSON inválido no body"}),
        }
    
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": headers,
            "body": json.dumps({"error": str(e)}),
        }
