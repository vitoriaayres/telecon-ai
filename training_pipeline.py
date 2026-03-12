"""
training_pipeline.py
====================
Pipeline de treinamento com Azure ML AutoML

Testa múltiplos modelos automaticamente e encontra o melhor

Uso:
  python training_pipeline.py
"""

import os
import json
from pathlib import Path
from dotenv import load_dotenv

# Carrega variáveis
load_dotenv('.env.azure')

# Imports Azure ML (instale com: pip install azure-ai-ml)
try:
    from azure.ai.ml import MLClient, automl, Input
    from azure.ai.ml.entities import Environment, Environment as ComputeEnvironment
    from azure.identity import DefaultAzureCredential
    AZURE_ML_INSTALADO = True
except ImportError:
    AZURE_ML_INSTALADO = False
    print("⚠️ Azure ML SDK não instalado")
    print("Instale com: pip install azure-ai-ml")

SUBSCRIPTION_ID = os.getenv('AZURE_SUBSCRIPTION_ID')
RESOURCE_GROUP = os.getenv('AZURE_RESOURCE_GROUP')
WORKSPACE_NAME = os.getenv('AZURE_ML_WORKSPACE_NAME')
STORAGE_CONTAINER = os.getenv('AZURE_STORAGE_CONTAINER')

print("=" * 70)
print("🤖 PIPELINE DE TREINAMENTO - AZURE ML AUTOML")
print("=" * 70)

def conectar_workspace():
    """Conecta ao Azure ML Workspace"""
    try:
        credential = DefaultAzureCredential()
        ml_client = MLClient(
            credential=credential,
            subscription_id=SUBSCRIPTION_ID,
            resource_group_name=RESOURCE_GROUP,
            workspace_name=WORKSPACE_NAME
        )
        print(f"✅ Conectado ao workspace: {WORKSPACE_NAME}")
        return ml_client
    except Exception as e:
        print(f"❌ Erro ao conectar: {e}")
        return None

def criar_pipeline_automl(ml_client):
    """Cria pipeline com AutoML"""
    
    print("\n📊 CONFIGURANDO AUTOML...\n")
    
    # Dados de entrada (CSV upladados)
    training_data = Input(
        type="uri_folder",
        path=f"azureml://subscriptions/{SUBSCRIPTION_ID}/resourcegroups/{RESOURCE_GROUP}/"
             f"providers/Microsoft.MachineLearningServices/workspaces/{WORKSPACE_NAME}/"
             f"datastores/workspaceblobstore/paths/datasets/"
    )
    
    # Configuração do AutoML
    automl_job = automl.classification(
        # Dados
        training_data=training_data,
        target_column_name="defeito_constatado",
        
        # Configuração geral
        primary_metric="accuracy",
        task="classification",
        
        # Limite de tempo
        timeout_minutes=30,
        
        # Modelos a testar
        allowed_training_algorithms=["logistic_regression", "random_forest", "xgboost", "svm"],
        
        # Cross-validation
        n_cross_validations=5,
    )
    
    # Submete o job
    print("⏳ Submetendo pipeline para Azure ML...")
    try:
        returned_job = ml_client.jobs.create_or_update(automl_job)
        print(f"✅ Pipeline criado: {returned_job.name}")
        print(f"   Link: https://ml.azure.com/jobs/{returned_job.name}")
        return returned_job
    except Exception as e:
        print(f"❌ Erro ao submeter: {e}")
        return None

def aguardar_conclusao(ml_client, job_id):
    """Aguarda conclusão do job"""
    
    print("\n⏳ Aguardando conclusão do treinamento...")
    print("(Você verá atualizações a cada iteração)\n")
    
    try:
        # Aguarda job
        ml_client.jobs.stream(job_id)
        
        # Obtém resultado
        job = ml_client.jobs.get(job_id)
        print(f"\n✅ Job concluído: {job.status}")
        
        # Obtém melhor modelo
        best_model = job.properties.get("best_model")
        print(f"\n🏆 Melhor Modelo: {best_model}")
        
        return job
    except Exception as e:
        print(f"❌ Erro ao aguardar: {e}")
        return None

def registrar_modelo(ml_client, job_id):
    """Registra o melhor modelo para uso"""
    
    print("\n📦 Registrando modelo...\n")
    
    try:
        # Obtém job
        job = ml_client.jobs.get(job_id)
        
        # Registra modelo
        modelo_registrado = ml_client.models.create_or_update(
            name="classificador_defeitos",
            version=1,
            path=f"azureml://jobs/{job_id}/outputs/model",
            type="custom_model",
            description="Classificador de Defeitos treinado com AutoML"
        )
        
        print(f"✅ Modelo registrado: {modelo_registrado.name}")
        print(f"   Versão: {modelo_registrado.version}")
        
        return modelo_registrado
    except Exception as e:
        print(f"⚠️ Alerta ao registrar: {e}")
        return None

def main():
    """Fluxo principal"""
    
    if not AZURE_ML_INSTALADO:
        print("\n⚠️ Azure ML SDK necessário!")
        print("Execute: pip install -r requirements.txt")
        return False
    
    print("\n📋 PRÉ-REQUISITOS:")
    print("  ✓ setup_azure_ml.py executado")
    print("  ✓ upload_dados.py executado")
    print("  ✓ Dados em Azure Storage")
    
    input("\n▶️ Pressione ENTER para iniciar o treinamento...")
    
    # Conecta
    ml_client = conectar_workspace()
    if not ml_client:
        return False
    
    # Cria pipeline
    job = criar_pipeline_automl(ml_client)
    if not job:
        return False
    
    # Aguarda conclusão (AVISO: pode levar 30min+)
    job_concluido = aguardar_conclusao(ml_client, job.name)
    if not job_concluido:
        return False
    
    # Registra modelo
    modelo = registrar_modelo(ml_client, job.name)
    
    print("\n" + "=" * 70)
    print("✅ TREINAMENTO COMPLETO!")
    print("=" * 70)
    
    print("\n🎯 PRÓXIMAS ETAPAS:\n")
    print("1. Visite Azure ML Studio:")
    print(f"   https://ml.azure.com/workspaces/{WORKSPACE_NAME}\n")
    
    print("2. Implante o melhor modelo como endpoint:")
    print("   python deploy_modelo.py\n")
    
    print("3. Atualize sua API com credenciais Azure")
    print("4. Deploy em Container Instances")
    
    print("\n📚 Recursos:")
    print("  - Métrica de sucesso: Acurácia")
    print("  - Versionamento: Azure ML Model Registry")
    print("  - Rastreamento: MLflow")
    
    return True

if __name__ == "__main__":
    main()
