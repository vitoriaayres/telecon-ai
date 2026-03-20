"""
Vercel Serverless Function - Endpoint /api/feedback
Compatível com Vercel Python Runtime
"""

import json


def handler(request):
    """
    Handler para registrar feedback.
    Em produção, integrar com banco de dados.
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
        
        # Log estruturado (em produção, enviar para serviço de logs)
        print(f"[feedback] {json.dumps(body)}")
        
        return {
            "statusCode": 200,
            "headers": headers,
            "body": json.dumps({"ok": True}),
        }
    
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": headers,
            "body": json.dumps({"error": str(e)}),
        }
