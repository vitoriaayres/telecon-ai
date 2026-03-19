"""
Script de teste local - valida se a arquitetura está integrada corretamente
"""
import sys
import os

def testar_imports():
    """Verifica se todos os imports funcionam"""
    print("=" * 60)
    print("[BUSCAR] TESTANDO IMPORTS")
    print("=" * 60)
    
    try:
        from ml import ClassificadorDefeitos, treinar_modelo_mock
        print("[OK] ml.py importado com sucesso")
    except ImportError as e:
        print(f"[ERRO] Erro ao importar ml.py: {e}")
        return False
    
    try:
        from trainamento_modelo import treinar_e_salvar_modelo
        print("[OK] trainamento_modelo.py importado com sucesso")
    except ImportError as e:
        print(f"[ERRO] Erro ao importar trainamento_modelo.py: {e}")
        return False
    
    try:
        from api import app, classificador
        print("[OK] api.py importado com sucesso")
    except ImportError as e:
        print(f"[ERRO] Erro ao importar api.py: {e}")
        return False
    
    return True

def testar_treinamento():
    """Testa o treinamento do modelo"""
    print("\n" + "=" * 60)
    print("[IA] TESTANDO TREINAMENTO")
    print("=" * 60)
    
    try:
        from trainamento_modelo import treinar_e_salvar_modelo
        treinar_e_salvar_modelo()
        print("[OK] Modelo treinado com sucesso")
        return True
    except Exception as e:
        print(f"[ERRO] Erro ao treinar: {e}")
        return False

def testar_predicao():
    """Testa a predição"""
    print("\n" + "=" * 60)
    print("[ALVO] TESTANDO PREDIÇÃO")
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
        print("[OK] Predição funcionando")
        return True
    except Exception as e:
        print(f"[ERRO] Erro na predição: {e}")
        import traceback
        traceback.print_exc()
        return False

def testar_api():
    """Testa os endpoints da API"""
    print("\n" + "=" * 60)
    print("[API] TESTANDO API ENDPOINTS")
    print("=" * 60)
    
    try:
        from fastapi.testclient import TestClient
        from api import app
        
        client = TestClient(app)
        
        # Teste /health
        print("\n[TESTE] Testando /health...")
        response = client.get("/health")
        print(f"Status: {response.status_code} - {response.json()}")
        assert response.status_code == 200
        print("[OK] /health OK")
        
        # Teste /predict
        print("\n[TESTE] Testando /predict...")
        response = client.post("/predict", json={"texto_cliente": "tela quebrada"})
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"Resultado: {response.json()}")
            print("[OK] /predict OK")
        else:
            print(f"[AVISO] /predict retornou: {response.json()}")
        
        # Teste /feedback
        print("\n[TESTE] Testando /feedback...")
        response = client.post("/feedback", json={
            "texto_cliente": "tela quebrada",
            "defeito_sugerido": "TELA_QUEBRADA",
            "defeito_correto": "TELA_QUEBRADA",
            "tecnico_id": "TEC001"
        })
        print(f"Status: {response.status_code} - {response.json()}")
        assert response.status_code == 200
        print("[OK] /feedback OK")
        
        # Teste /metricas
        print("\n[TESTE] Testando /metricas...")
        response = client.get("/metricas")
        print(f"Status: {response.status_code} - {response.json()}")
        assert response.status_code == 200
        print("[OK] /metricas OK")
        
        return True
    except Exception as e:
        print(f"[ERRO] Erro ao testar API: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Executa todos os testes"""
    print("\n" + "[START] INICIANDO TESTES DE INTEGRAÇÃO" + "\n")
    
    resultados = {
        "Imports": testar_imports(),
        "Treinamento": testar_treinamento(),
        "Predição": testar_predicao(),
        "API": testar_api()
    }
    
    print("\n" + "=" * 60)
    print("[DADOS] RESUMO DOS TESTES")
    print("=" * 60)
    
    for teste, resultado in resultados.items():
        status = "[OK] PASSOU" if resultado else "[ERRO] FALHOU"
        print(f"{teste}: {status}")
    
    todos_passaram = all(resultados.values())
    
    print("\n" + "=" * 60)
    if todos_passaram:
        print("[SUCESSO] TODOS OS TESTES PASSARAM - ARQUITETURA OK!")
    else:
        print("[AVISO] ALGUNS TESTES FALHARAM - VERIFIQUE OS ERROS")
    print("=" * 60 + "\n")
    
    return todos_passaram

if __name__ == "__main__":
    sucesso = main()
    sys.exit(0 if sucesso else 1)
