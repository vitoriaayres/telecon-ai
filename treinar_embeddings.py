"""
treinar_embeddings.py
=====================
Treina um classificador semântico usando sentence-transformers.

Abordagem:
  1. Carrega o dataset real (CSV)
  2. Gera embeddings de cada reclamação usando um modelo multilíngue pré-treinado
     (paraphrase-multilingual-MiniLM-L12-v2 — ~120MB, suporta PT-BR nativamente)
  3. Treina um LogisticRegression sobre os embeddings
  4. Salva o classificador e os embeddings do treino

Vantagem sobre TF-IDF + RandomForest:
  - Entende semântica: "não refresca" ≈ "não gela"
  - Generaliza para reclamações nunca vistas
  - Não precisa de tokenização manual
"""

import os
import re
import unicodedata
import pandas as pd
import numpy as np
import joblib
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sentence_transformers import SentenceTransformer

DATASET_PATH = os.path.join(
    os.path.dirname(__file__),
    "DATASET",
    "dataset_consolidado_completo - dataset_consolidado_completo.csv.csv"
)

# Modelo leve ~90MB — rápido de baixar, funciona bem para frases técnicas curtas
# (Para produção futura, trocar por paraphrase-multilingual-MiniLM-L12-v2)
MODELO_EMBED = "all-MiniLM-L6-v2"
SAIDA_PKL    = "classificador_semantico.pkl"


def normalizar_label(texto: str) -> str:
    """Normaliza rótulos para fundir variantes ortográficas da mesma classe."""
    # Remove acentos
    t = unicodedata.normalize("NFD", texto)
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    # Minúsculas e strip
    t = t.lower().strip()
    # Colapsa espaços múltiplos
    t = re.sub(r"\s+", " ", t)
    # Abreviações comuns
    t = t.replace("c/", "com ").replace(" c/", " com ")
    t = re.sub(r"\brel[eé]\b", "rele", t)
    return t


# Mapa de normalização → label canônico legível (preserva a versão "bonita")
# Construído dinamicamente: para cada grupo normalizado, escolhe o label mais
# frequente como representante.
def canonizar_labels(series: pd.Series) -> pd.Series:
    """Substitui cada label pelo representante mais frequente de seu grupo."""
    norm = series.map(normalizar_label)
    freq = series.groupby(norm).apply(lambda g: g.value_counts().idxmax())
    return norm.map(freq)


def carregar_dados():
    df = pd.read_csv(DATASET_PATH)

    # Descarta linhas sem reclamação real
    df_util = df[
        df["descricao_defeito_reclamado"].notna() &
        (df["descricao_defeito_reclamado"] != "SEM_INFORMACAO")
    ].copy()

    # Label: usa _ref (normalizada) quando disponível; senão usa _diagnostico
    df_util["label"] = df_util["descricao_defeito_constatado_ref"].where(
        df_util["descricao_defeito_constatado_ref"].notna() &
        (df_util["descricao_defeito_constatado_ref"] != "DESCRICAO_NAO_ENCONTRADA"),
        other=df_util["descricao_defeito_constatado_diagnostico"]
    )

    df_util = df_util[
        df_util["label"].notna() &
        (df_util["label"].str.strip() != "")
    ].copy()
    df_util["label"] = df_util["label"].str.strip()

    # ── Normalização: funde variantes ortográficas ────────────────────────────
    df_util["label"] = canonizar_labels(df_util["label"])

    # Mantém classes com ≥ 3 exemplos (bom equilíbrio qualidade/volume)
    contagens = df_util["label"].value_counts()
    classes_validas = contagens[contagens >= 3].index
    df_util = df_util[df_util["label"].isin(classes_validas)]

    total_csv = len(df)
    print(f"📊 {len(df_util)} registros | {df_util['label'].nunique()} classes | {len(df_util)/total_csv*100:.1f}% do CSV total")
    print(f"   Média por classe: {len(df_util)/df_util['label'].nunique():.1f} amostras")
    return df_util["descricao_defeito_reclamado"].tolist(), df_util["label"].tolist()


def treinar(saida: str = SAIDA_PKL):
    X_textos, y = carregar_dados()

    # 1. Carrega o modelo de embeddings (baixa ~120MB na primeira vez)
    print(f"\n🔽 Carregando modelo: {MODELO_EMBED} ...")
    model = SentenceTransformer(MODELO_EMBED)

    # 2. Gera embeddings (vetores de 384 dimensões por frase)
    print("⚙️  Gerando embeddings (pode levar ~1-2 min no CPU)...")
    X_embeddings = model.encode(X_textos, show_progress_bar=True, batch_size=32)
    print(f"   Shape dos embeddings: {X_embeddings.shape}")

    # 3. Split treino/teste
    X_train, X_test, y_train, y_test = train_test_split(
        X_embeddings, y, test_size=0.2, random_state=42
    )

    # 4. Treina LogisticRegression (excelente com embeddings densos)
    print("\n🤖 Treinando LogisticRegression ...")
    clf = LogisticRegression(
        max_iter=1000,
        C=5.0,
        solver="lbfgs",
        random_state=42
    )
    clf.fit(X_train, y_train)

    # 5. Avaliação
    acc = clf.score(X_test, y_test)
    print(f"\n📈 Acurácia: {acc:.2%}")
    y_pred = clf.predict(X_test)
    print(classification_report(y_test, y_pred, zero_division=0))

    # 6. Salva modelo + encoder
    payload = {
        "modelo_embed": MODELO_EMBED,
        "clf": clf,
        "classes": clf.classes_.tolist(),
    }
    joblib.dump(payload, saida)
    print(f"\n✅ Salvo em '{saida}'")
    return payload


if __name__ == "__main__":
    treinar()
