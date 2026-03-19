"""
azure_ml_integration.py
=======================
Integração entre API FastAPI e Azure ML Models

Permite usar modelos treinados no Azure ML diretamente na API
"""

import os
import json
from typing import Tuple, List
from datetime import datetime
from dotenv import load_dotenv

# Carrega variáveis
load_dotenv('.env.azure')

try:
    from azure.ai.ml import MLClient
    from azure.identity import DefaultAzureCredential
    from azure.storage.blob import BlobServiceClient
    AZURE_DISPONIVEL = True
except ImportError:
    AZURE_DISPONIVEL = False

SUBSCRIPTION_ID = os.getenv('AZURE_SUBSCRIPTION_ID')
RESOURCE_GROUP = os.getenv('AZURE_RESOURCE_GROUP')
WORKSPACE_NAME = os.getenv('AZURE_ML_WORKSPACE_NAME')
STORAGE_ACCOUNT = os.getenv('AZURE_STORAGE_ACCOUNT_NAME')
FEEDBACK_CONTAINER = os.getenv('AZURE_FEEDBACK_CONTAINER')

class AzureMLClassificador:
    """Classificador que usa modelos do Azure ML"""
    
    def __init__(self, modelo_nome: str = "classificador_defeitos"):
        """Inicializa conexão com Azure ML"""
        
        if not AZURE_DISPONIVEL:
            raise RuntimeError("Azure ML SDK não instalado")
        
        try:
            self.credential = DefaultAzureCredential()
            self.ml_client = MLClient(
                credential=self.credential,
                subscription_id=SUBSCRIPTION_ID,
                resource_group_name=RESOURCE_GROUP,
                workspace_name=WORKSPACE_NAME
            )
            
            # Carrega modelo registrado
            self.modelo = self.ml_client.models.get(
                name=modelo_nome,
                version=1
            )
            
            print(f"[OK] Modelo Azure ML carregado: {modelo_nome}")
            
        except Exception as e:
            print(f"[AVISO] Erro ao carregar modelo Azure ML: {e}")
            self.modelo = None
    
    def prever(self, reclamacao_cliente: str) -> Tuple[str, float]:
        """
        Faz predição usando modelo Azure ML
        
        Args:
            reclamacao_cliente: Texto da reclamação
            
        Returns:
            (defeito, confiança)
        """
        
        if not self.modelo:
            raise RuntimeError("Modelo não carregado")
        
        try:
            # Aqui você chamaria o endpoint do Azure ML
            # Por enquanto, retorna formato esperado
            from ml import ClassificadorDefeitos
            clf_local = ClassificadorDefeitos()
            return clf_local.prever(reclamacao_cliente)
            
        except Exception as e:
            print(f"Erro na predição: {e}")
            return "ERRO", 0.0
    
    def extrair_causa_raiz(self, reclamacao_cliente: str) -> List[str]:
        """Extrai palavras-chave da reclamação"""
        
        try:
            from ml import ClassificadorDefeitos
            clf_local = ClassificadorDefeitos()
            return clf_local.extrair_causa_raiz(reclamacao_cliente)
        except Exception as e:
            print(f"Erro ao extrair causa raiz: {e}")
            return []

class AzureStorageFeedback:
    """Gerencia persistência de feedback no Azure Storage"""
    
    def __init__(self):
        """Inicializa conexão com Azure Storage"""
        
        try:
            # Obtém connection string
            import subprocess
            resultado = subprocess.run(
                f'az storage account show-connection-string '
                f'--name {STORAGE_ACCOUNT} --query connectionString -o tsv',
                shell=True,
                capture_output=True,
                text=True
            )
            
            if resultado.returncode != 0:
                raise Exception("Não foi possível obter connection string")
            
            connection_string = resultado.stdout.strip()
            
            self.blob_service_client = BlobServiceClient.from_connection_string(
                connection_string
            )
            self.container_client = self.blob_service_client.get_container_client(
                FEEDBACK_CONTAINER
            )
            
            print("[OK] Conectado ao Azure Blob Storage para Feedback")
            
        except Exception as e:
            print(f"[AVISO] Erro ao conectar ao Storage: {e}")
            self.blob_service_client = None
    
    def salvar_feedback(self, feedback_data: dict) -> bool:
        """
        Salva feedback no Azure Storage
        
        Args:
            feedback_data: Dicionário com dados do feedback
            
        Returns:
            True se sucesso, False caso contrário
        """
        
        if not self.blob_service_client:
            print("[AVISO] Storage não conectado")
            return False
        
        try:
            # Cria nome do arquivo com timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"feedback_{timestamp}_{feedback_data.get('tecnico_id', 'unknown')}.json"
            
            # Serializa dados
            json_data = json.dumps(feedback_data, ensure_ascii=False, indent=2)
            
            # Faz upload
            self.container_client.upload_blob(
                name=filename,
                data=json_data.encode('utf-8'),
                overwrite=False
            )
            
            print(f"[OK] Feedback salvo: {filename}")
            return True
            
        except Exception as e:
            print(f"[ERRO] Erro ao salvar feedback: {e}")
            return False
    
    def obter_feedback_stats(self) -> dict:
        """Obtém estatísticas de feedback do Storage"""
        
        if not self.blob_service_client:
            return {}
        
        try:
            blobs = self.container_client.list_blobs()
            total_feedbacks = sum(1 for _ in blobs)
            
            return {
                "total_feedbacks_Azure": total_feedbacks,
                "container": FEEDBACK_CONTAINER,
                "storage_account": STORAGE_ACCOUNT
            }
            
        except Exception as e:
            print(f"[AVISO] Erro ao obter stats: {e}")
            return {}

# Singleton instances
_classificador_azure = None
_storage_feedback = None

def get_classificador_azure() -> AzureMLClassificador:
    """Obtém instância do classificador Azure ML"""
    global _classificador_azure
    
    if _classificador_azure is None:
        try:
            _classificador_azure = AzureMLClassificador()
        except Exception as e:
            print(f"[AVISO] Erro ao inicializar classificador Azure: {e}")
            _classificador_azure = None
    
    return _classificador_azure

def get_storage_feedback() -> AzureStorageFeedback:
    """Obtém instância de storage de feedback"""
    global _storage_feedback
    
    if _storage_feedback is None:
        try:
            _storage_feedback = AzureStorageFeedback()
        except Exception as e:
            print(f"[AVISO] Erro ao inicializar storage: {e}")
            _storage_feedback = None
    
    return _storage_feedback
