"""
Vercel Serverless Function - Endpoint /api/predict
Compatível com Vercel Python Runtime
Retorna mock data para evitar dependências pesadas em produção
"""

import json


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
        
        # Validação
        if not texto_cliente:
            return {
                "statusCode": 400,
                "headers": headers,
                "body": json.dumps({
                    "error": "Por favor, forneça a reclamação do cliente ou selecione pelo menos um filtro."
                }),
            }
        
        # Mock response com dados realistas
        response_data = {
            "resultados": [
                {
                    "rank": 1,
                    "defeito_sugerido": "Compressor com defeito",
                    "confianca": 0.85,
                    "confianca_pct": 85,
                    "documentacao": "https://suaempresa.com/manuais/compressor.pdf",
                    "descricao_llm": "Análise baseada em histórico de ordens de serviço similares.",
                    "acao_recomendada_llm": "Inspecionar funcionamento do compressor. Consultar manual técnico.",
                },
                {
                    "rank": 2,
                    "defeito_sugerido": "Termostato com defeito",
                    "confianca": 0.72,
                    "confianca_pct": 72,
                    "documentacao": "https://suaempresa.com/manuais/termostato.pdf",
                    "descricao_llm": "Possível falha no sensor de temperatura.",
                    "acao_recomendada_llm": "Verificar calibração do termostato.",
                },
                {
                    "rank": 3,
                    "defeito_sugerido": "Evaporador obstruído",
                    "confianca": 0.65,
                    "confianca_pct": 65,
                    "documentacao": "https://suaempresa.com/manuais/evaporador.pdf",
                    "descricao_llm": "Possível bloqueio no fluxo de ar.",
                    "acao_recomendada_llm": "Realizar limpeza preventiva do evaporador.",
                },
            ],
            "texto_analisado": texto_cliente,
            "total_classes": 15,
            "total_registros": 164,
            "modelo_ativo": "randomforest",
            "sugere_busca": False,
            "contexto_web": {
                "top_defeitos": ["Compressor com defeito", "Termostato com defeito"],
                "exemplos_dataset": [],
            }
        }
        
        return {
            "statusCode": 200,
            "headers": headers,
            "body": json.dumps(response_data, ensure_ascii=False),
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
