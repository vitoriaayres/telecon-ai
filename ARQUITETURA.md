"""
Fluxo de Arquitetura Refatorada - TELECONTROL
==============================================

📊 ARQUITETURA CORRIGIDA:
  
  1. TREINAMENTO
     └─ trainamento_modelo.py
        ├─ Carrega dados
        ├─ Cria pipeline (TF-IDF + RandomForest)
        └─ Salva em: classificador_defeitos.pkl

  2. MÓDULO DE ML
     └─ ml.py
        ├─ ClassificadorDefeitos (carrega modelo)
        ├─ prever() → (defeito, confiança)
        └─ extrair_causa_raiz() → lista de palavras-chave

  3. API REST
     └─ api.py
        ├─ Importa ClassificadorDefeitos de ml.py
        ├─ POST /predict → Predição com confiança
        ├─ POST /feedback → Registra acertos/erros
        ├─ GET /health → Status da API
        └─ GET /metricas → Taxa de acerto/erro

  4. LLM ALTERNATIVO (isolado)
     └─ classificador.py
        ├─ LangChain + OpenAI/Azure
        └─ Pode ser integrado depois se necessário


✅ MELHORIAS IMPLEMENTADAS:
  • Imports corrigidos em todos os arquivos
  • Integração entre módulos (api.py → ml.py)
  • Error handling com HTTPException
  • Persistência de feedback em arquivo JSON
  • Métricas de desempenho
  • Health check
  • Estrutura pronta para Azure


🚀 COMO USAR:

  1. Treinar o modelo:
     python trainamento_modelo.py

  2. Iniciar a API:
     uvicorn api:app --reload

  3. Testar endpoints:
     
     POST /predict
     {
       "texto_cliente": "clculo nao liga e queima"
     }

     POST /feedback
     {
       "texto_cliente": "celular nao liga",
       "defeito_sugerido": "PLACA_CURTO",
       "defeito_correto": "PLACA_CURTO",
       "tecnico_id": "TEC001"
     }

     GET /health
     GET /metricas


📝 PRÓXIMOS PASSOS PARA AZURE:
  • Migrar modelo para Azure ML
  • Usar Azure Storage para persistência
  • Integrar Azure Cognitive Services
  • Deployar como Azure Container Instance
"""
