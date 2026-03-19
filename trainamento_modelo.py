import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib
import os

BASE_DIR = os.path.dirname(__file__)
DATASET_1_PATH = os.path.join(BASE_DIR, "DATASET", "dataset_1.csv")
DATASET_2_PATH = os.path.join(BASE_DIR, "DATASET", "dataset_2.csv")

def treinar_e_salvar_modelo(caminho_saida: str = 'classificador_defeitos.pkl'):
    """
    Treina o modelo de classificação de defeitos com o dataset real e o salva.
    
    Args:
        caminho_saida: Caminho onde o modelo será salvo
    """
    print("[ARQUIVO] Carregando datasets...")
    df1 = pd.read_csv(DATASET_1_PATH)
    df2 = pd.read_csv(DATASET_2_PATH)
    df = pd.concat([df1, df2], ignore_index=True)
    print(f"   Total de registros (dataset_1 + dataset_2): {len(df)}")

    # 1. Limpeza e filtragem dos dados
    df_util = df[
        df['descricao_defeito_reclamado'].notna() &
        (df['descricao_defeito_reclamado'] != 'SEM_INFORMACAO') &
        df['descricao_defeito_constatado_ref'].notna() &
        (df['descricao_defeito_constatado_ref'] != 'DESCRICAO_NAO_ENCONTRADA')
    ].copy()
# Remove classes com menos de 3 exemplos
    contagens = df_util['descricao_defeito_constatado_ref'].value_counts()
    classes_validas = contagens[contagens >= 3].index
    df_util = df_util[df_util['descricao_defeito_constatado_ref'].isin(classes_validas)]

    print(f"   Registros úteis para treino: {len(df_util)}")
    print(f"   Classes únicas: {df_util['descricao_defeito_constatado_ref'].nunique()}")
    print()

    X = df_util['descricao_defeito_reclamado']
    y = df_util['descricao_defeito_constatado_ref']

    # 2. Criando o Pipeline (Vetorização TF-IDF + RandomForest)
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(
            ngram_range=(1, 2),
            min_df=1,
            stop_words=None,
            max_features=5000
        )),
        ('clf', RandomForestClassifier(
            n_estimators=300,
            random_state=42,
            class_weight='balanced'
        ))
    ])

    # 3. Treinamento com split estratificado
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    print("[IA] Treinando modelo...")
    pipeline.fit(X_train, y_train)

    # 4. Avaliação
    score = pipeline.score(X_test, y_test)
    print(f"\n[DADOS] Acurácia no teste: {score:.2%}")
    print("\nRelatório de classificação:")
    y_pred = pipeline.predict(X_test)
    print(classification_report(y_test, y_pred, zero_division=0))

    # 5. Salva o modelo e a lista de classes
    joblib.dump(pipeline, caminho_saida)
    
    # Salva lista de classes para uso na API
    classes = sorted(y.unique().tolist())
    joblib.dump(classes, caminho_saida.replace('.pkl', '_classes.pkl'))
    
    print(f"\n[OK] Modelo salvo em '{caminho_saida}'")
    print(f"[OK] Classes salvas em '{caminho_saida.replace('.pkl', '_classes.pkl')}'")
    return pipeline, classes

if __name__ == "__main__":
    treinar_e_salvar_modelo()