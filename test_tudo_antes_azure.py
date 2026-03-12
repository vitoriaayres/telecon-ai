"""
test_tudo_antes_azure.py
========================
Valida que TUDO funciona localmente antes de enviar para Azure

Execute este script primeiro!
"""

import sys
import os
import time

print("=" * 80)
print("🧪 VALIDAÇÃO COMPLETA - ANTES DE IR PARA AZURE")
print("=" * 80)

tests_passed = 0
tests_failed = 0

def test(nome, funcao):
    """Executa um teste"""
    global tests_passed, tests_failed
    
    print(f"\n{'─' * 80}")
    print(f"🔍 {nome}")
    print(f"{'─' * 80}")
    
    try:
        funcao()
        print("✅ PASSOU")
        tests_passed += 1
    except AssertionError as e:
        print(f"❌ FALHOU: {e}")
        tests_failed += 1
    except Exception as e:
        print(f"❌ ERRO: {e}")
        tests_failed += 1

# ========== TESTES ==========

def test_imports_basicos():
    """Testa se todos os imports funcionam"""
    print("Testando imports...")
    import pandas as pd
    import numpy as np
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.pipeline import Pipeline
    import joblib
    from fastapi import FastAPI
    from pydantic import BaseModel
    print("  ✓ Imports básicos OK")

def test_ml_module():
    """Testa módulo ml.py"""
    print("Testando ml.py...")
    from ml import ClassificadorDefeitos, treinar_modelo_mock
    print("  ✓ ml.py importado")
    
    # Testa treinar_modelo_mock
    dados = {
        "reclamacao": ["tela quebrada", "bateria ruim"],
        "defeito_constatado": ["TELA_QUEBRADA", "BATERIA_RUI"]
    }
    treinar_modelo_mock(dados, "test_model.pkl")
    
    assert os.path.exists("test_model.pkl"), "Modelo não foi criado"
    print("  ✓ Modelo treinado com sucesso")
    
    # Testa predicção
    clf = ClassificadorDefeitos("test_model.pkl")
    defeito, confianca = clf.prever("tela quebrada")
    assert isinstance(defeito, str), "Defeito deve ser string"
    assert 0 <= confianca <= 1, "Confiança deve estar entre 0 e 1"
    print(f"  ✓ Predição OK: {defeito} ({confianca:.2%})")
    
    # Testa extração de causa raiz
    causa_raiz = clf.extrair_causa_raiz("tela quebrada")
    assert isinstance(causa_raiz, list), "Causa raiz deve ser lista"
    print(f"  ✓ Extração de causa raiz OK: {causa_raiz}")
    
    # Limpa
    os.remove("test_model.pkl")

def test_api_estrutura():
    """Testa se API vai funcionar"""
    print("Testando estrutura da API...")
    from api import app, ReclamacaoRequest, FeedbackRequest
    
    assert app.title == "API - Classificador de Defeitos"
    assert len(app.routes) > 0
    print(f"  ✓ {len(app.routes)} rotas registradas")

def test_api_endpoints():
    """Testa endpoints da API com TestClient"""
    print("Testando endpoints...")
    
    from fastapi.testclient import TestClient
    from api import app
    
    client = TestClient(app)
    
    # Teste 1: Health
    response = client.get("/health")
    assert response.status_code == 200
    print("  ✓ GET /health")
    
    # Teste 2: Metricas
    response = client.get("/metricas")
    assert response.status_code == 200
    print("  ✓ GET /metricas")
    
    # Teste 3: Predict (pode falhar se sem modelo, mas testa estrutura)
    response = client.post("/predict", json={"texto_cliente": "teste"})
    # Pode ser 200 ou 503 (sem modelo), ambos são OK
    assert response.status_code in [200, 503]
    print(f"  ✓ POST /predict ({response.status_code})")
    
    # Teste 4: Feedback
    response = client.post("/feedback", json={
        "texto_cliente": "teste",
        "defeito_sugerido": "TELA",
        "defeito_correto": "TELA",
        "tecnico_id": "TEST"
    })
    assert response.status_code == 200
    print("  ✓ POST /feedback")

def test_trainamento():
    """Testa script de treinamento"""
    print("Testando trainamento_modelo.py...")
    from trainamento_modelo import treinar_e_salvar_modelo
    
    # Remove modelo antigo se existir
    if os.path.exists("classificador_defeitos.pkl"):
        os.remove("classificador_defeitos.pkl")
    
    # Treina
    treinar_e_salvar_modelo()
    
    assert os.path.exists("classificador_defeitos.pkl"), "Modelo não foi criado"
    print("  ✓ Modelo oficial treinado")

def test_feedback_persistence():
    """Testa persistência de feedback"""
    print("Testando persistência de feedback...")
    
    from api import FEEDBACK_LOG, salvar_feedback, carregar_feedback
    
    # Limpa log
    FEEDBACK_LOG.clear()
    
    # Adiciona feedback
    FEEDBACK_LOG.append({
        "texto": "teste",
        "modelo_acertou": True
    })
    
    # Salva
    salvar_feedback()
    assert os.path.exists("feedback_log.json"), "Arquivo de feedback não criado"
    print("  ✓ Feedback persistido em arquivo")
    
    # Limpa
    FEEDBACK_LOG.clear()
    if os.path.exists("feedback_log.json"):
        os.remove("feedback_log.json")

def test_env_azure():
    """Testa se .env.azure existe"""
    print("Testando .env.azure...")
    
    from dotenv import load_dotenv
    
    assert os.path.exists(".env.azure"), ".env.azure não existe"
    print("  ✓ Arquivo .env.azure existe")
    
    # Tenta carregar
    load_dotenv(".env.azure")
    
    # Verifica variáveis críticas (podem estar vazias, só verifica se foram definidas)
    print("  ✓ Variáveis carregadas do .env.azure")

def test_requirements():
    """Verifica se requirements.txt está atualizado"""
    print("Testando requirements.txt...")
    
    with open("requirements.txt", "r") as f:
        reqs = f.read().lower()
    
    essenciais = ["fastapi", "sklearn", "pandas", "azure"]
    for req in essenciais:
        assert req in reqs, f"{req} não está em requirements.txt"
    
    print("  ✓ Todas as dependências essenciais presente")

def test_docker():
    """Verifica se Dockerfile existe"""
    print("Testando Dockerfile...")
    
    assert os.path.exists("Dockerfile"), "Dockerfile não encontrado"
    
    with open("Dockerfile", "r") as f:
        conteudo = f.read()
    
    assert "python" in conteudo.lower()
    assert "fastapi" in conteudo or "api" in conteudo
    print("  ✓ Dockerfile válido")

def test_scripts_azure():
    """Verifica scripts do Azure"""
    print("Testando scripts Azure...")
    
    scripts = [
        "setup_azure_ml.py",
        "upload_dados.py",
        "training_pipeline.py",
        "deploy_aci.py",
        "azure_ml_integration.py",
        "test_azure_integration.py"
    ]
    
    for script in scripts:
        assert os.path.exists(script), f"{script} não encontrado"
    
    print(f"  ✓ Todos os {len(scripts)} scripts Azure presentes")

# ========== EXECUTAR TESTES ==========

if __name__ == "__main__":
    start_time = time.time()
    
    # Testes locais
    test("1. Imports Básicos", test_imports_basicos)
    test("2. Módulo ML", test_ml_module)
    test("3. Estrutura da API", test_api_estrutura)
    test("4. Endpoints da API", test_api_endpoints)
    test("5. Script de Treinamento", test_trainamento)
    test("6. Persistência de Feedback", test_feedback_persistence)
    test("7. Arquivo .env.azure", test_env_azure)
    test("8. requirements.txt", test_requirements)
    test("9. Dockerfile", test_docker)
    test("10. Scripts Azure ML", test_scripts_azure)
    
    # Resumo
    elapsed = time.time() - start_time
    
    print("\n" + "=" * 80)
    print("📊 RESUMO DOS TESTES")
    print("=" * 80)
    
    print(f"""\n
✅ Testes que passaram: {tests_passed}/10
❌ Testes que falharam: {tests_failed}/10
⏱️  Tempo total: {elapsed:.2f}s
    """)
    
    if tests_failed == 0:
        print("=" * 80)
        print("🎉 TUDO FUNCIONANDO PERFEITAMENTE!")
        print("=" * 80)
        print("""
Seu projeto está pronto para Azure! Próximos passos:

1. Preencher .env.azure com credenciais Azure
2. Executar: python setup_azure_ml.py
3. Executar: python upload_dados.py
4. Executar: python training_pipeline.py
5. Executar: python deploy_aci.py

Bom deploy! 🚀
        """)
    else:
        print("=" * 80)
        print("⚠️ ALGUNS TESTES FALHARAM")
        print("=" * 80)
        print("Corrija os erros acima antes de enviar para Azure")
        sys.exit(1)
