"""
Script de teste local - valida se a arquitetura está integrada corretamente
"""
import sys
import os

def testar_imports():
    """Verifica se todos os imports funcionam"""
    print("=" * 60)
    print("🔍 TESTANDO IMPORTS")
    print("=" * 60)
    
    try:
        from ml import ClassificadorDefeitos, treinar_modelo_mock
        print("✅ ml.py importado com sucesso")
    except ImportError as e:
        print(f"❌ Erro ao importar ml.py: {e}")
        return False
    
    try:
        from trainamento_modelo import treinar_e_salvar_modelo
        print("✅ trainamento_modelo.py importado com sucesso")
    except ImportError as e:
        print(f"❌ Erro ao importar trainamento_modelo.py: {e}")
        return False
    
    try:
        from api import app, classificador
        print("✅ api.py importado com sucesso")
    except ImportError as e:
        print(f"❌ Erro ao importar api.py: {e}")
        return False
    
    return True

def testar_treinamento():
    """Testa o treinamento do modelo"""
    print("\n" + "=" * 60)
    print("🤖 TESTANDO TREINAMENTO")
    print("=" * 60)
    
    try:
        from trainamento_modelo import treinar_e_salvar_modelo
        treinar_e_salvar_modelo()
        print("✅ Modelo treinado com sucesso")
        return True
    except Exception as e:
        print(f"❌ Erro ao treinar: {e}")
        return False

def testar_predicao():
    """Testa a predição"""
    print("\n" + "=" * 60)
    print("🎯 TESTANDO PREDIÇÃO")
    print("=" * 60)
    
    try:
        if not os.path.exists('classificador_defeitos.pkl'):
            print("⚠️ Modelo não existe, treinando...")
            from trainamento_modelo import treinar_e_salvar_modelo
            treinar_e_salvar_modelo()
        
        from ml import ClassificadorDefeitos
        classificador = ClassificadorDefeitos('classificador_defeitos.pkl')
        
        teste = "celular nao liga e cheiro de queimado"
        defeito, confianca = classificador.prever(teste)
        causa_raiz = classificador.extrair_causa_raiz(teste)
        
        print(f"Entrada: '{teste}'")
        print(f"Defeito predito: {defeito}")
        print(f"Confiança: {confianca:.2%}")
        print(f"Causa raiz: {causa_raiz}")
        print("✅ Predição funcionando")
        return True
    except Exception as e:
        print(f"❌ Erro na predição: {e}")
        import traceback
        traceback.print_exc()
        return False

def testar_api():
    """Testa os endpoints da API"""
    print("\n" + "=" * 60)
    print("🌐 TESTANDO API ENDPOINTS")
    print("=" * 60)
    
    try:
        from fastapi.testclient import TestClient
        from api import app
        
        client = TestClient(app)
        
        # Teste /health
        print("\n📍 Testando /health...")
        response = client.get("/health")
        print(f"Status: {response.status_code} - {response.json()}")
        assert response.status_code == 200
        print("✅ /health OK")
        
        # Teste /predict
        print("\n📍 Testando /predict...")
        response = client.post("/predict", json={"texto_cliente": "tela quebrada"})
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"Resultado: {response.json()}")
            print("✅ /predict OK")
        else:
            print(f"⚠️ /predict retornou: {response.json()}")
        
        # Teste /feedback
        print("\n📍 Testando /feedback...")
        response = client.post("/feedback", json={
            "texto_cliente": "tela quebrada",
            "defeito_sugerido": "TELA_QUEBRADA",
            "defeito_correto": "TELA_QUEBRADA",
            "tecnico_id": "TEC001"
        })
        print(f"Status: {response.status_code} - {response.json()}")
        assert response.status_code == 200
        print("✅ /feedback OK")
        
        # Teste /metricas
        print("\n📍 Testando /metricas...")
        response = client.get("/metricas")
        print(f"Status: {response.status_code} - {response.json()}")
        assert response.status_code == 200
        print("✅ /metricas OK")
        
        return True
    except Exception as e:
        print(f"❌ Erro ao testar API: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Executa todos os testes"""
    print("\n" + "🚀 INICIANDO TESTES DE INTEGRAÇÃO" + "\n")
    
    resultados = {
        "Imports": testar_imports(),
        "Treinamento": testar_treinamento(),
        "Predição": testar_predicao(),
        "API": testar_api()
    }
    
    print("\n" + "=" * 60)
    print("📊 RESUMO DOS TESTES")
    print("=" * 60)
    
    for teste, resultado in resultados.items():
        status = "✅ PASSOU" if resultado else "❌ FALHOU"
        print(f"{teste}: {status}")
    
    todos_passaram = all(resultados.values())
    
    print("\n" + "=" * 60)
    if todos_passaram:
        print("🎉 TODOS OS TESTES PASSARAM - ARQUITETURA OK!")
    else:
        print("⚠️ ALGUNS TESTES FALHARAM - VERIFIQUE OS ERROS")
    print("=" * 60 + "\n")
    
    return todos_passaram

if __name__ == "__main__":
    sucesso = main()
    sys.exit(0 if sucesso else 1)
