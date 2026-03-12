import pandas as pd
import joblib
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from typing import List, Tuple

def treinar_modelo_mock(dados_treino: dict, caminho_saida: str = 'classificador_defeitos.pkl'):
    """
    Função utilitária: cria e salva um pipeline simplificado
    para testes da nossa arquitetura.
    """
    df = pd.DataFrame(dados_treino)
    
    # É fundamental nomear as etapas ('tfidf', 'clf')
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(stop_words=['e', 'de', 'com', 'o', 'a', 'nao', 'em'])),
        ('clf', RandomForestClassifier(n_estimators=100, random_state=42))
    ])
    
    pipeline.fit(df['reclamacao'], df['defeito_constatado'])
    joblib.dump(pipeline, caminho_saida)
    print(f"Modelo salvo: '{caminho_saida}'")


class ClassificadorDefeitos:
    def __init__(self, caminho_modelo: str = 'pipeline_clf_defeitos.pkl'):
        """Carrega o pipeline na memória."""
        self.pipeline = joblib.load(caminho_modelo)
        # Extrai os componentes para podermos inspecionar depois
        self.tfidf = self.pipeline.named_steps['tfidf']
        self.clf = self.pipeline.named_steps['clf']

    def prever(self, reclamacao_cliente: str) -> Tuple[str, float]:
        """Retorna o defeito constatado e a probabilidade (confiança)."""
        predicao = self.pipeline.predict([reclamacao_cliente])[0]
        probabilidades = self.pipeline.predict_proba([reclamacao_cliente])[0]
        confianca = max(probabilidades)
        return str(predicao), float(confianca)

    def extrair_causa_raiz(self, reclamacao_cliente: str, top_n: int = 3) -> List[str]:
        """
        Analisa a string de entrada e retorna os termos que obtiveram 
        o maior peso do vetor TF-IDF.
        """
        # Transforma o texto em um vetor
        vetor_esparso = self.tfidf.transform([reclamacao_cliente])
        
        # Converte para array
        vetor_denso = vetor_esparso.toarray()[0]
        nomes_features = self.tfidf.get_feature_names_out()
        
        # Pega os índices dos elementos com maior pontuação (do final para o começo)
        indices_top = vetor_denso.argsort()[-top_n:][::-1]
        
        # Extrai as palavras em que a pontuação é maior que 0
        palavras_chave = [
            nomes_features[i] for i in indices_top if vetor_denso[i] > 0
        ]
        
        return palavras_chave

# --- Bloco de Teste ---
if __name__ == "__main__":
    import pandas as pd # necessário apenas se rodar este bloco de teste

    # Mock de dados
    dados_mock = {
        "reclamacao": [
            "A tela quebrou em uma queda", 
            "Bateria viciada, não segura carga",
            "A imagem do display tem listras",
            "Não liga e sinto cheiro de queimado na placa"
        ],
        "defeito_constatado": ["TELA_QUEBRADA", "BATERIA_RUI", "TELA_QUEBRADA", "PLACA_CURTO"]
    }
    
    # 1. Treina o modelo inicial
    treinar_modelo_mock(dados_mock)
    
    # 2. Testa as funcionalidades da classe
    sistema = ClassificadorDefeitos()
    teste = "Caiu no chão e a tela não exibe imagem, apenas listras."
    
    defeito, confianca = sistema.prever(teste)
    causa_raiz = sistema.extrair_causa_raiz(teste)
    
    print("\n--- Teste Local ---")
    print(f"Entrada: {teste}")
    print(f"Defeito: {defeito} | Confiança: {confianca:.2f}")
    print(f"Causa Raiz (Top 3 TF-IDF): {causa_raiz}")