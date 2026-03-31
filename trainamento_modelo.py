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


def _read_csv_robusto(caminho: str, usecols: list[str] | None = None) -> pd.DataFrame:
    """Lê CSV tolerando linhas malformadas para não perder o treino inteiro."""
    try:
        return pd.read_csv(caminho, usecols=usecols)
    except Exception:
        return pd.read_csv(caminho, usecols=usecols, engine="python", on_bad_lines="skip")


def _carregar_dataset_treino() -> pd.DataFrame:
    """Consolida dataset_1 e dataset_2 em colunas canônicas para treino."""
    frames: list[pd.DataFrame] = []

    if os.path.exists(DATASET_1_PATH):
        d1 = _read_csv_robusto(
            DATASET_1_PATH,
            usecols=[
                "descricao_defeito_reclamado",
                "descricao_defeito_constatado_ref",
            ],
        ).rename(
            columns={
                "descricao_defeito_reclamado": "reclamacao",
                "descricao_defeito_constatado_ref": "defeito_constatado",
            }
        )
        frames.append(d1)

    if os.path.exists(DATASET_2_PATH):
        d2 = _read_csv_robusto(
            DATASET_2_PATH,
            usecols=[
                "descricao_combinada",
                "defeito_reclamado_descricao",
                "defeito_constatado_descricao",
            ],
        )
        d2["reclamacao"] = d2["defeito_reclamado_descricao"].where(
            d2["defeito_reclamado_descricao"].notna()
            & (d2["defeito_reclamado_descricao"].astype(str).str.strip() != ""),
            other=d2["descricao_combinada"],
        )
        d2["defeito_constatado"] = d2["defeito_constatado_descricao"]
        d2 = d2[["reclamacao", "defeito_constatado"]]
        frames.append(d2)

    if not frames:
        raise FileNotFoundError("Nenhum dataset encontrado em DATASET/")

    return pd.concat(frames, ignore_index=True)

def treinar_e_salvar_modelo(caminho_saida: str = 'classificador_defeitos.pkl'):
    """
    Treina o modelo de classificação de defeitos com o dataset real e o salva.
    
    Args:
        caminho_saida: Caminho onde o modelo será salvo
    """
    print("[ARQUIVO] Carregando datasets...")
    df = _carregar_dataset_treino()
    print(f"   Total de registros consolidados (dataset_1 + dataset_2): {len(df)}")

    # 1. Limpeza e filtragem dos dados
    df_util = df[
        df['reclamacao'].notna() &
        (df['reclamacao'].astype(str).str.strip() != '') &
        (df['reclamacao'] != 'SEM_INFORMACAO') &
        df['defeito_constatado'].notna() &
        (df['defeito_constatado'].astype(str).str.strip() != '') &
        (df['defeito_constatado'] != 'DESCRICAO_NAO_ENCONTRADA')
    ].copy()
    # Remove classes com menos de 3 exemplos
    contagens = df_util['defeito_constatado'].value_counts()
    classes_validas = contagens[contagens >= 3].index
    df_util = df_util[df_util['defeito_constatado'].isin(classes_validas)]

    print(f"   Registros úteis para treino: {len(df_util)}")
    print(f"   Classes únicas: {df_util['defeito_constatado'].nunique()}")
    print()

    X = df_util['reclamacao']
    y = df_util['defeito_constatado']

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
        X, y, test_size=0.2, random_state=42, stratify=y
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