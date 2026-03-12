"""
upload_dados.py
===============
Upload de dados CSV para Azure Data Lake Storage

Uso:
  python upload_dados.py
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient

# Carrega variáveis
load_dotenv('.env.azure')

STORAGE_ACCOUNT = os.getenv('AZURE_STORAGE_ACCOUNT_NAME')
CONTAINER = os.getenv('AZURE_STORAGE_CONTAINER')
LOCAL_DATA_DIR = 'data'

print("=" * 70)
print("📤 UPLOAD DE DADOS PARA AZURE STORAGE")
print("=" * 70)

def get_connection_string():
    """Obtém connection string da storage account"""
    try:
        import subprocess
        resultado = subprocess.run(
            f'az storage account show-connection-string '
            f'--name {STORAGE_ACCOUNT} '
            f'--query connectionString -o tsv',
            shell=True,
            capture_output=True,
            text=True
        )
        if resultado.returncode == 0:
            return resultado.stdout.strip()
        else:
            print(f"❌ Erro ao obter connection string: {resultado.stderr}")
            return None
    except Exception as e:
        print(f"❌ Exceção: {e}")
        return None

def upload_arquivos():
    """Faz upload dos arquivos CSV"""
    
    connection_string = get_connection_string()
    if not connection_string:
        print("\n❌ Não foi possível conectar ao Azure Storage")
        print("Verifique se você executou 'az login' e preencheu .env.azure")
        return False
    
    try:
        # Conecta ao Blob Storage
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        container_client = blob_service_client.get_container_client(CONTAINER)
        
        # Lista arquivos CSV locais
        csv_files = list(Path(LOCAL_DATA_DIR).glob('*.csv'))
        
        if not csv_files:
            print(f"\n⚠️ Nenhum arquivo .csv encontrado em '{LOCAL_DATA_DIR}/'")
            print("Coloque seus arquivos CSV nessa pasta e tente novamente")
            return False
        
        print(f"\n📁 {len(csv_files)} arquivo(s) encontrado(s)")
        
        # Faz upload de cada arquivo
        total_bytes = 0
        for i, csv_file in enumerate(csv_files, 1):
            filename = csv_file.name
            file_size = csv_file.stat().st_size
            total_bytes += file_size
            
            print(f"\n   {i}. {filename}")
            print(f"      Tamanho: {file_size / (1024*1024):.2f} MB")
            
            try:
                with open(csv_file, 'rb') as data:
                    container_client.upload_blob(
                        name=filename,
                        data=data,
                        overwrite=True
                    )
                print(f"      ✅ Enviado com sucesso")
            except Exception as e:
                print(f"      ❌ Erro: {e}")
                return False
        
        print(f"\n{'=' * 70}")
        print(f"✅ UPLOAD COMPLETO!")
        print(f"   Total de dados: {total_bytes / (1024*1024):.2f} MB")
        print(f"   Container: {CONTAINER}")
        print(f"{'=' * 70}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
        print("\nVERIFIQUE:")
        print("1. Az CLI instalado: az --version")
        print("2. Autenticado: az login")
        print("3. Connection String válida em .env.azure")
        return False

if __name__ == "__main__":
    print("\n📋 PRÉ-REQUISITOS:")
    print("  ✓ Az CLI instalado")
    print("  ✓ az login executado")
    print("  ✓ .env.azure preenchido")
    print("  ✓ Arquivos CSV em ./data/")
    
    input("\n▶️ Pressione ENTER para continuar...")
    
    sucesso = upload_arquivos()
    
    if sucesso:
        print("\n🎯 PRÓXIMO PASSO:")
        print("   Execute: python training_pipeline.py")
