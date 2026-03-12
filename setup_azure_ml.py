"""
setup_azure_ml.py
=================
Script para configurar Azure ML Workspace e todas as dependências

Prerequisitos:
  1. Az CLI instalado: https://aka.ms/azcli
  2. Autenticado: az login
  3. Variáveis no .env.azure preenchidas
"""

import os
import json
import subprocess
from pathlib import Path
from dotenv import load_dotenv

# Carrega variáveis do .env.azure
load_dotenv('.env.azure')

# Configurações
SUBSCRIPTION_ID = os.getenv('AZURE_SUBSCRIPTION_ID')
RESOURCE_GROUP = os.getenv('AZURE_RESOURCE_GROUP')
LOCATION = os.getenv('AZURE_LOCATION')
ML_WORKSPACE = os.getenv('AZURE_ML_WORKSPACE_NAME')
STORAGE_ACCOUNT = os.getenv('AZURE_STORAGE_ACCOUNT_NAME')
REGISTRY_NAME = os.getenv('AZURE_REGISTRY_NAME')

print("=" * 70)
print("🚀 CONFIGURANDO AZURE ML PARA TELECONTROL")
print("=" * 70)

def executar_comando(cmd, descricao):
    """Executa comando Azure CLI"""
    print(f"\n📍 {descricao}")
    print(f"   Comando: {cmd}")
    try:
        resultado = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if resultado.returncode == 0:
            print(f"   ✅ Sucesso")
            return resultado.stdout.strip()
        else:
            print(f"   ⚠️ Erro: {resultado.stderr}")
            return None
    except Exception as e:
        print(f"   ❌ Exceção: {e}")
        return None

# 1. Criar Resource Group
executar_comando(
    f'az group create -n {RESOURCE_GROUP} -l {LOCATION}',
    "1/5: Criando Resource Group"
)

# 2. Criar Storage Account
executar_comando(
    f'az storage account create -n {STORAGE_ACCOUNT} -g {RESOURCE_GROUP} -l {LOCATION} --sku Standard_LRS',
    "2/5: Criando Storage Account"
)

# 3. Criar Blob Containers
executar_comando(
    f'az storage container create -n {os.getenv("AZURE_STORAGE_CONTAINER")} '
    f'--account-name {STORAGE_ACCOUNT}',
    "3/5: Criando Container para Datasets"
)

executar_comando(
    f'az storage container create -n {os.getenv("AZURE_FEEDBACK_CONTAINER")} '
    f'--account-name {STORAGE_ACCOUNT}',
    "3/5: Criando Container para Feedback"
)

# 4. Criar Container Registry
executar_comando(
    f'az acr create -n {REGISTRY_NAME} -g {RESOURCE_GROUP} --sku Basic --admin-enabled true',
    "4/5: Criando Azure Container Registry"
)

# 5. Criar ML Workspace
cmd_ml = (
    f'az ml workspace create '
    f'--name {ML_WORKSPACE} '
    f'--resource-group {RESOURCE_GROUP} '
    f'--location {LOCATION} '
    f'--storage-account {STORAGE_ACCOUNT}'
)
executar_comando(cmd_ml, "5/5: Criando Azure ML Workspace")

print("\n" + "=" * 70)
print("✅ CONFIGURAÇÃO COMPLETA!")
print("=" * 70)

print("\n📋 PRÓXIMOS PASSOS:\n")
print("1. Instale SDK Azure ML:")
print("   pip install azure-ai-ml azure-storage-blob\n")

print("2. Upload seus dados CSV:")
print("   python upload_dados.py\n")

print("3. Crie o pipeline de treinamento:")
print("   python training_pipeline.py\n")

print("4. Integre com sua API:")
print("   Atualize api.py com credenciais Azure\n")

print("5. Deploy em Container:")
print("   docker build -t telecontrol-api .")
print("   az acr build -r {REGISTRY_NAME} -t telecontrol-api:latest .\n")

print("📚 Documentação:")
print("  - Azure ML: https://learn.microsoft.com/azure/machine-learning/")
print("  - MLflow: https://mlflow.org/docs/latest/tracking.html")
