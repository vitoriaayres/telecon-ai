"""
deploy_aci.py
=============
Deploy da API em Azure Container Instances

Uso:
  python deploy_aci.py
"""

import os
import subprocess
from dotenv import load_dotenv

load_dotenv('.env.azure')

REGISTRY_NAME = os.getenv('AZURE_REGISTRY_NAME')
RESOURCE_GROUP = os.getenv('AZURE_RESOURCE_GROUP')
LOCATION = os.getenv('AZURE_LOCATION')
REGISTRY_USER = os.getenv('AZURE_REGISTRY_USERNAME')
REGISTRY_PASS = os.getenv('AZURE_REGISTRY_PASSWORD')

CONTAINER_NAME = "telecontrol-api"
IMAGE_NAME = f"{REGISTRY_NAME}.azurecr.io/telecontrol-api:latest"
DNS_PREFIX = "telecontrol-api"

print("=" * 70)
print("[START] DEPLOY EM AZURE CONTAINER INSTANCES")
print("=" * 70)

def executar_comando(cmd, descricao):
    """Executa comando"""
    print(f"\n[TESTE] {descricao}")
    print(f"   {cmd}\n")
    try:
        resultado = subprocess.run(cmd, shell=True, capture_output=False, text=True)
        return resultado.returncode == 0
    except Exception as e:
        print(f"[ERRO] Erro: {e}")
        return False

def main():
    """Fluxo principal"""
    
    print("\n[LISTA] PRÙ-REQUISITOS:")
    print("  [OK] setup_azure_ml.py executado")
    print("  [OK] Docker instalado")
    print("  [OK] az cli instalado")
    
    input("\n[>] Pressione ENTER para iniciar deploy...\n")
    
    # 1. Build da imagem
    if not executar_comando(
        f"docker build -t {CONTAINER_NAME}:latest .",
        "1/4: Build da imagem Docker"
    ):
        print("❌ Falha no build")
        return False
    
    # 2. Tag para registry
    if not executar_comando(
        f"docker tag {CONTAINER_NAME}:latest {IMAGE_NAME}",
        "2/4: Tagging para Azure Registry"
    ):
        print("❌ Falha no tagging")
        return False
    
    # 3. Login no registry
    if not executar_comando(
        f"az acr login --name {REGISTRY_NAME}",
        "3/4: Login no Azure Container Registry"
    ):
        print("❌ Falha no login")
        return False
    
    # 4. Push para registry
    if not executar_comando(
        f"docker push {IMAGE_NAME}",
        "4/4: Push da imagem para Azure"
    ):
        print("❌ Falha no push")
        return False
    
    # 5. Deploy em ACI
    print("\n📍 5/5: Deploy em Azure Container Instances")
    
    cmd_aci = (
        f"az container create "
        f"--resource-group {RESOURCE_GROUP} "
        f"--name {CONTAINER_NAME} "
        f"--image {IMAGE_NAME} "
        f"--cpu 1 --memory 1 "
        f"--registry-login-server {REGISTRY_NAME}.azurecr.io "
        f"--registry-username {REGISTRY_USER} "
        f"--registry-password {REGISTRY_PASS} "
        f"--dns-name-label {DNS_PREFIX} "
        f"--ports 8000 "
        f"--environment AZURE_SUBSCRIPTION_ID={os.getenv('AZURE_SUBSCRIPTION_ID')} "
        f"--environment AZURE_RESOURCE_GROUP={RESOURCE_GROUP} "
        f"--environment AZURE_ML_WORKSPACE_NAME={os.getenv('AZURE_ML_WORKSPACE_NAME')}"
    )
    
    if not executar_comando(cmd_aci, "Criando instância de container"):
        print("❌ Falha no deploy")
        return False
    
    print("\n" + "=" * 70)
    print("✅ DEPLOY COMPLETO!")
    print("=" * 70)
    
    print(f"\n🌐 API disponível em:")
    print(f"   http://{DNS_PREFIX}.{LOCATION}.azurecontainers.io:8000")
    
    print(f"\n📊 Endpoints:")
    print(f"   POST /predict")
    print(f"   POST /feedback")
    print(f"   GET  /health")
    print(f"   GET  /metricas")
    
    print(f"\n📋 Comandos úteis:")
    print(f"   Ver logs: az container logs -n {CONTAINER_NAME} -g {RESOURCE_GROUP}")
    print(f"   Deletar: az container delete -n {CONTAINER_NAME} -g {RESOURCE_GROUP}")

if __name__ == "__main__":
    main()
