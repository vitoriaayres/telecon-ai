"""
test_azure_integration.py
=========================
Testa integração com Azure ML e Storage
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv('.env.azure')

print("=" * 70)
print("[TESTE] TESTANDO INTEGRAÇÃO AZURE")
print("=" * 70)

# 1. Verificar Az CLI
print("\n[1] Verificando Azure CLI...")
try:
    import subprocess
    resultado = subprocess.run("az --version", shell=True, capture_output=True, text=True)
    if resultado.returncode == 0:
        print("[OK] Az CLI instalado")
    else:
        print("[ERRO] Az CLI não encontrado")
        sys.exit(1)
except Exception as e:
    print(f"[ERRO] Erro: {e}")
    sys.exit(1)

# 2. Verificar autenticação
print("\n[2] Verificando autenticação Azure...")
try:
    resultado = subprocess.run(
        "az account show --query name -o tsv",
        shell=True,
        capture_output=True,
        text=True
    )
    if resultado.returncode == 0:
        print(f"[OK] Autenticado como: {resultado.stdout.strip()}")
    else:
        print("[ERRO] Não autenticado. Execute: az login")
        sys.exit(1)
except Exception as e:
    print(f"[ERRO] Erro: {e}")
    sys.exit(1)

# 3. Verificar SDK Azure ML
print("\n[3] Verificando Azure ML SDK...")
try:
    from azure.ai.ml import MLClient
    from azure.storage.blob import BlobServiceClient
    from azure.identity import DefaultAzureCredential
    print("[OK] Azure ML SDK instalado")
except ImportError as e:
    print(f"[ERRO] Falta dependência: {e}")
    print("   Execute: pip install -r requirements.txt")
    sys.exit(1)

# 4. Verificar variáveis de ambiente
print("\n[4] Verificando variáveis de ambiente (.env.azure)...")
required_vars = [
    'AZURE_SUBSCRIPTION_ID',
    'AZURE_RESOURCE_GROUP',
    'AZURE_ML_WORKSPACE_NAME',
    'AZURE_STORAGE_ACCOUNT_NAME'
]

all_set = True
for var in required_vars:
    value = os.getenv(var)
    if value:
        print(f"[OK] {var}: {value[:20]}...")
    else:
        print(f"[ERRO] {var}: não definido")
        all_set = False

if not all_set:
    print("\n[AVISO] Preenchaa .env.azure com todos os valores")
    sys.exit(1)

# 5. Testar credenciais
print("\n[5] Testando credenciais Azure...")
try:
    credential = DefaultAzureCredential()
    token = credential.get_token("https://management.azure.com/.default")
    print(f"[OK] Credenciais válidas (token: {str(token.token)[:20]}...)")
except Exception as e:
    print(f"[ERRO] Erro de credenciais: {e}")
    sys.exit(1)

# 6. Testar conexão ao ML Workspace
print("\n[6] Testando conexão ao ML Workspace...")
try:
    from azure.ai.ml import MLClient
    
    ml_client = MLClient(
        credential=credential,
        subscription_id=os.getenv('AZURE_SUBSCRIPTION_ID'),
        resource_group_name=os.getenv('AZURE_RESOURCE_GROUP'),
        workspace_name=os.getenv('AZURE_ML_WORKSPACE_NAME')
    )
    
    # Tenta listar recursos
    workspaces = list(ml_client.workspaces.list())
    print(f"[OK] Workspace acessível")
except Exception as e:
    print(f"[AVISO] Workspace não encontrado (criar com setup_azure_ml.py): {e}")

# 7. Testar Storage
print("\n[7] Testando Azure Storage...")
try:
    resultado = subprocess.run(
        f"az storage account show-connection-string "
        f"--name {os.getenv('AZURE_STORAGE_ACCOUNT_NAME')} "
        f"--query connectionString -o tsv",
        shell=True,
        capture_output=True,
        text=True
    )
    
    if resultado.returncode == 0:
        connection_string = resultado.stdout.strip()
        blob_service = BlobServiceClient.from_connection_string(connection_string)
        containers = list(blob_service.list_containers())
        print(f"[OK] Storage acessível ({len(containers)} containers)")
    else:
        print(f"[AVISO] Storage não encontrado (criar com setup_azure_ml.py)")
except Exception as e:
    print(f"[AVISO] Erro ao testar storage: {e}")

# 8. Verificar arquivos locais
print("\n[8] Verificando arquivos necessários...")
arquivos = [
    'api.py',
    'ml.py',
    'trainamento_modelo.py',
    'azure_ml_integration.py',
    'requirements.txt',
    'Dockerfile'
]

for arquivo in arquivos:
    if os.path.exists(arquivo):
        print(f"[OK] {arquivo}")
    else:
        print(f"[ERRO] {arquivo} não encontrado")

print("\n" + "=" * 70)
print("[OK] TESTES CONCLUÍDOS!")
print("=" * 70)

print("\n[ALVO] PRÓXIMOS PASSOS:\n")
print("1. Setup inicial:")
print("   python setup_azure_ml.py\n")
print("2. Upload dados:")
print("   python upload_dados.py\n")
print("3. Treinar modelo:")
print("   python training_pipeline.py\n")
print("4. Deploy:")
print("   python deploy_aci.py")
