"""
Vercel Serverless Function - Endpoint /api/web-search
Compatível com Vercel Python Runtime
"""

import json


def handler(request):
    """
    Handler para busca web contextualizada.
    por enquanto retorna mock data para evitar chamadas desnecessárias
    """
    
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
        "Content-Type": "application/json",
    }
    
    if request.method == "OPTIONS":
        return {"statusCode": 200, "headers": headers}
    
    if request.method != "POST":
        return {
            "statusCode": 405,
            "headers": headers,
            "body": json.dumps({"error": "Método não permitido"}),
        }
    
    try:
        body = json.loads(request.body) if isinstance(request.body, str) else request.get_json()
        
        texto_cliente = body.get("texto_cliente", "").strip()
        
        if not texto_cliente:
            return {
                "statusCode": 400,
                "headers": headers,
                "body": json.dumps({"error": "texto_cliente obrigatório"}),
            }
        
        # Mock response (sem Tavily key em produção)
        response_data = {
            "status": "fallback_context",
            "resultados": [
                {
                    "title": "Diagnóstico baseado em histórico interno",
                    "url": "https://suaempresa.com/kb",
                    "content": "Análise contextualizada usando dados históricos de ordens de serviço..."
                }
            ]
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
            "body": json.dumps({"error": str(e)}),
        }
