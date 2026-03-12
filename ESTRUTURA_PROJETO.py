"""
Estrutura Final do Projeto Telecontrol
========================================

Este arquivo descreve a estrutura completa após integração com Azure ML
"""

PROJECT_STRUCTURE = """
telecontrol/
│
├── 🐍 CÓDIGO PYTHON (LOCAL)
│   ├── api.py                           [API FastAPI completa]
│   ├── ml.py                            [Classificador de ML]
│   ├── classificador.py                 [LLM alternativo (LangChain)]
│   ├── trainamento_modelo.py            [Script de treinamento]
│   └── azure_ml_integration.py          [Integração com Azure ML]
│
├── ☁️ AZURE ML & INFRASTRUCTURE
│   ├── setup_azure_ml.py               [Cria RG, Storage, ML Workspace]
│   ├── upload_dados.py                 [Upload CSVs para Azure]
│   ├── training_pipeline.py            [AutoML no Azure ML]
│   └── deploy_aci.py                   [Deploy em Container Instances]
│
├── 🧪 TESTES & VALIDAÇÃO
│   ├── test_integracao.py              [Testes de integração local]
│   ├── test_azure_integration.py       [Valida conectividade Azure]
│   └── test_tudo_antes_azure.py        [Checklist completo]
│
├── 🐳 DOCKER & CONTAINERS
│   ├── Dockerfile                      [Imagem da API]
│   └── docker-compose.yml              [Compose pra desenvolvimento]
│
├── 📋 CONFIGURAÇÃO
│   ├── requirements.txt                [Dependências Python]
│   ├── .env.azure                      [Variáveis Azure (PREENCHIR!)]
│   └── .gitignore                      [Arquivos a ignorar]
│
├── 📊 DADOS
│   ├── data/
│   │   ├── export_defeitos_constatados.csv
│   │   ├── export_defeitos_os.csv
│   │   ├── export_defeitos_reclamados.csv
│   │   ├── export_diagnosticos.csv
│   │   ├── export_os_base.csv
│   │   ├── export_os_defeito_solucao.csv
│   │   ├── export_os_sem_pecas.csv
│   │   ├── export_pecas_por_os.csv
│   │   └── export_produtos.csv
│   │
│   ├── classificador_defeitos.pkl      [Modelo treinado (gerado)]
│   └── feedback_log.json               [Log de feedback (gerado)]
│
├── 📚 DOCUMENTAÇÃO
│   ├── ARQUITETURA.md                  [Visão técnica geral]
│   ├── GUIA_AZURE_ML.md                [Passo-a-passo completo]
│   ├── RESUMO_IMPLEMENTACAO.md         [Resumo do que foi feito]
│   └── README.md                       [Este arquivo - instruções]
│
└── 🎯 WORKFLOW
    ├── Local Development
    │   └── python trainamento_modelo.py → uvicorn api:app --reload
    │
    ├── Setup Azure (uma vez)
    │   └── python setup_azure_ml.py → test_azure_integration.py
    │
    ├── Dados & Treinamento
    │   └── python upload_dados.py → python training_pipeline.py
    │
    └── Production Deploy
        └── docker build → deploy_aci.py → API em Azure
"""

# Descrição de cada arquivo

FILES_DESCRIPTION = {
    "api.py": """
    FastAPI Application
    - Endpoint POST /predict: Classifica defeitos
    - Endpoint POST /feedback: Registra acertos/erros
    - Endpoint GET /health: Status da API
    - Endpoint GET /metricas: Taxa de acerto
    - Integração com ml.py e azure_ml_integration.py
    """,
    
    "ml.py": """
    Módulo ML Core
    - ClassificadorDefeitos: Classe para predições
    - treinar_modelo_mock: Função testes
    - Usa SKLearn RandomForest + TF-IDF
    - Métodos: prever(), extrair_causa_raiz()
    """,
    
    "classificador.py": """
    Classificador LLM (Opcional)
    - Usa LangChain + OpenAI/Azure
    - Função analisar_reclamacao() estruturada
    - Para análise alternativa/complementar
    """,
    
    "trainamento_modelo.py": """
    Script de Treinamento Local
    - Treina modelo com dados de exemplo
    - Salva como classificador_defeitos.pkl
    - Usa train_test_split
    - Execute antes de rodar API local
    """,
    
    "azure_ml_integration.py": """
    Integração Azure ML
    - AzureMLClassificador: Wrapper para modelos Azure ML
    - AzureStorageFeedback: Persistência em Blob Storage
    - Mantém compatibilidade com ml.py local
    - Factory functions: get_classificador_azure()
    """,
    
    "setup_azure_ml.py": """
    Setup de Infraestrutura Azure
    - Cria Resource Group
    - Cria Storage Account + Containers
    - Cria Azure Container Registry
    - Cria ML Workspace
    - Execute UMA VEZ
    """,
    
    "upload_dados.py": """
    Upload de Dados
    - Envia CSVs de ./data/ para Azure Blob
    - Usa BlobServiceClient
    - Cria container "datasets"
    - Execute após setup_azure_ml.py
    """,
    
    "training_pipeline.py": """
    Pipeline AutoML Azure
    - Conecta ao ML Workspace
    - Configura AutoML com:
      * classification task
      * accuracy metric
      * 30min timeout
      * 5-fold cross-validation
    - Registra melhor modelo
    - Leva ~30 minutos
    """,
    
    "deploy_aci.py": """
    Deploy em Azure Container Instances
    - Build Docker
    - Push para Azure Container Registry
    - Deploy em ACI
    - Configura DNS, portas, CPU, memória
    - API fica no VPC 24/7
    """,
    
    "Dockerfile": """
    Imagem Docker da API
    - Base: python:3.11-slim
    - Instala dependências
    - Copia código e .env.azure
    - Treina modelo se necessário
    - Expõe porta 8000
    - Health check configurado
    """,
    
    "test_tudo_antes_azure.py": """
    Validação Completa ANTES do Deploy
    - Testa 10 aspectos do projeto:
      1. Imports
      2. Módulo ML
      3. Estrutura API
      4. Endpoints
      5. Treinamento
      6. Persistência
      7. Configs Azure
      8. Requirements
      9. Dockerfile
      10. Scripts Azure
    - Execute antes do primeiro deploy
    """,
}

FLUXO_COMPLETO = """
╔══════════════════════════════════════════════════════════════════╗
║         FLUXO DE TRABALHO COMPLETO - TELECONTROL AZURE          ║
╚══════════════════════════════════════════════════════════════════╝

1️⃣ DESENVOLVIMENTO LOCAL (seu PC)
   ├─ Editar código Python (api.py, ml.py)
   ├─ Executar testes locais
   ├─ Testar endpoints com FastAPI
   └─ Validar tudo com: python test_tudo_antes_azure.py

2️⃣ PREPARAÇÃO AZURE (uma vez)
   ├─ Preencher .env.azure
   ├─ Executar: python setup_azure_ml.py
   │  └─ Cria Resource Group, Storage, ML Workspace
   └─ Validar: python test_azure_integration.py

3️⃣ DADOS & TREINAMENTO
   ├─ Enviar dados: python upload_dados.py
   │  └─ CSVs → Azure Blob Storage
   ├─ Treinar: python training_pipeline.py
   │  └─ AutoML testa múltiplos modelos (~30min)
   └─ Modelo fica registrado no Azure ML Registry

4️⃣ CONTAINERIZAÇÃO
   ├─ Build local: docker build -t telecontrol-api .
   ├─ Testar local: docker run -p 8000:8000 telecontrol-api
   └─ Validar endpoints

5️⃣ DEPLOY EM AZURE
   ├─ Executar: python deploy_aci.py
   │  ├─ Tag e push para Azure Container Registry
   │  └─ Deploy em Azure Container Instances
   └─ API disponível em: http://{dns}.azurecontainers.io:8000

6️⃣ MONITORAMENTO & FEEDBACK
   ├─ API recebe requisições
   ├─ POST /predict → Classifica defeitos
   ├─ POST /feedback → Registra em Azure Blob
   ├─ GET /metricas → Taxa de acerto
   └─ Logs em: az container logs -n telecontrol-api

7️⃣ CICLO DE MELHORIA
   ├─ Novos dados chegam (POST /feedback)
   ├─ python upload_dados.py (com dados atualizados)
   ├─ python training_pipeline.py (retreina com AutoML)
   └─ Deploy nova versão com melhor modelo

╚══════════════════════════════════════════════════════════════════╝
"""

# Comandos úteis

COMANDOS_UTEIS = """
╔══════════════════════════════════════════════════════════════════╗
║                   COMANDOS RÁPIDOS & UTEIS                       ║
╚══════════════════════════════════════════════════════════════════╝

🔐 AUTENTICAÇÃO AZURE
  az login                              # Login (browser)
  az logout                             # Logout
  az account show                       # Conta atual
  az account list                       # Todas as contas

☁️ VERIFICAR RECURSOS
  az resource group list -o table       # Ver Resource Groups
  az storage account list -o table      # Ver Storage Accounts
  az ml workspace list -o table         # Ver ML Workspaces
  az container list                     # Ver containers rodando

📊 DADOS
  az storage blob list -c datasets \
    --account-name {STORAGE}            # Listar dados uploaded
  az storage blob download -n dados.csv \
    -c datasets --account-name {STORAGE} # Download arquivo

🐳 DOCKER
  docker build -t telecontrol-api .     # Build local
  docker run -p 8000:8000 telecontrol-api  # Run local
  docker ps                             # Containers rodando
  docker logs {container}               # Ver logs
  docker stop {container}               # Parar container

📦 AZURE CONTAINER REGISTRY
  az acr login -n {REGISTRY}            # Login no registry
  docker push {registry}.azurecr.io/{image}  # Push imagem

🚀 PRODUCTION
  az container logs -n telecontrol-api  # Ver logs API
  az container restart -n telecontrol-api  # Restart API
  az container delete -n telecontrol-api    # Deletar
  az container show -n telecontrol-api -o table  # Ver detalhes

💾 BACKUP
  az storage blob download-batch \
    -s datasets -d ./backup --account-name {STORAGE}

💰 CUSTOS
  az consumption usage list --query "[].name,quantity,unit"
  https://azure.microsoft.com/en-us/pricing/details/container-instances/

╚══════════════════════════════════════════════════════════════════╝
"""

print(PROJECT_STRUCTURE)
print("\n" + "=" * 70 + "\n")
print(FLUXO_COMPLETO)
print("\n" + "=" * 70 + "\n")
print(COMANDOS_UTEIS)
