from imblearn.over_sampling import SMOTE
import nltk
from nltk.corpus import stopwords
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent.parent
CAMINHO_BASE_TRATADA = BASE_DIR / "data" / "processed" / "base_tratada.xlsx"


def isolar_variaveis(df):
    """
        Isola as variáveis PREDITIVAS das variáveis de ROTULAGEM, mantendo
        apenas o que era conhecido no momento da publicação do edital.
    """

    print("\n" * 50)
    print("-" * 50)
    print("Removendo variáveis de Data Leakage (ROTULAGEM)...")
    print("-" * 50)

    # Colunas que representam o desfecho, heurísticas ou identificadores textuais.
    colunas_para_remover = [
        'licitacao',
        'numero_edital',
        'valor_homologacao',
        'url_ultima_publicacao',
        'qtd_participantes',
        'percentual_desconto',
        'sem_publicidade',
        'historico_vitorias_empresa_vencedora',
        "modalidade_de_risco",
        'score_de_risco'
    ]

    # Mantém apenas: 'ano', 'mes', 'unidade_gestora', 'modalidade', 'objeto', 'valor_estimado' e 'risco'.
    df = df.drop(columns=colunas_para_remover, errors='ignore')

    print("[OK] Variáveis de Rotulagem removidas com sucesso!")

    return df


def tratar_nulos(df):
    """
        Trata valores faltantes remanescentes.
    """

    print("-" * 50)
    print("Tratando valores nulos...")
    print("-" * 50)

    # Preenche numéricos com a mediana para mitigar outliers.
    if 'valor_estimado' in df.columns:
        mediana_valor = df['valor_estimado'].median()
        df['valor_estimado'] = df['valor_estimado'].fillna(mediana_valor)

    # Preenche categóricos com "NAO_INFORMADO".
    colunas_categoricas = ['unidade_gestora', 'modalidade']
    for col in colunas_categoricas:
        if col in df.columns:
            df[col] = df[col].fillna('NAO_INFORMADO')

    print("[OK] Valores nulos tratados com sucesso!")
    
    return df


def codificar_categoricas(df):
    """
        Aplica Label Encoding para categóricas.
    """

    print("-" * 50)
    print("Realizando Encoding...")
    print("-" * 50)

    df = df.copy()
    le = LabelEncoder()
    colunas_categoricas = ['unidade_gestora', 'modalidade']
    mapeamento_risco = {'Baixo Risco': 0, 'Médio Risco': 1, 'Alto Risco': 2}

    # Encoding das categóricas 'unidade_gestora' e 'modalidade'.
    for col in colunas_categoricas:
        if col in df.columns:
            df[col] = le.fit_transform(df[col].astype(str))

    # Encoding da categórica 'risco'.
    df['risco'] = df['risco'].map(mapeamento_risco)

    print("[OK] Variáveis categóricas codificadas com sucesso!")

    return df


def normalizar_numericas(df):
    """
        Aplica normalização para numéricas.
    """

    print("-" * 50)
    print("Realizando Normalização...")
    print("-" * 50)

    df = df.copy()
    scaler = StandardScaler()

    if 'valor_estimado' in df.columns:
        df[['valor_estimado']] = scaler.fit_transform(df[['valor_estimado']])

    print("[OK] Variáveis numéricas normalizadas com sucesso!")

    return df


def dividir_bases(df, target_col='risco'):
    """
        Divide a base mantendo a proporção da variável alvo.
    """

    X = df.drop(columns=[target_col])
    y = df[target_col]

    return train_test_split(X, y, test_size=0.20, random_state=42, stratify=y)


def vetorizar_texto(X_train, X_test, coluna='objeto', max_features=50):
    """
        Transforma texto livre (nesse caso, o objeto do certame) 
        em colunas numéricas usando TF-IDF.
    """

    print("-" * 50)
    print(f"Aplicando TF-IDF na coluna '{coluna}'...")
    print("-" * 50)

    # Preenche possíveis objetos com valores nulos por string vazia.
    X_train = X_train.copy()
    X_test = X_test.copy()
    X_train[coluna] = X_train[coluna].fillna("")
    X_test[coluna] = X_test[coluna].fillna("")

    # Inicializa o TF-IDF ignorando palavras comuns do português (stopwords).
    try:
        stop_words_pt = stopwords.words('portuguese')
    except LookupError:
        nltk.download('stopwords')
        stop_words_pt = stopwords.words('portuguese')

    tf_idf = TfidfVectorizer(max_features=max_features, stop_words=stop_words_pt)

    # Treina e transforma no conjunto de treino
    matriz_train = tf_idf.fit_transform(X_train[coluna])

    # Apenas transforma no conjunto de teste
    matriz_test = tf_idf.transform(X_test[coluna])

    # Cria os nomes das novas colunas (ex.: 'tfidf_asfalto'; 'tfidf_medicamento')
    nomes_colunas = [f"tfidf_{palavra}" for palavra in tf_idf.get_feature_names_out()]

    # Converte as matrizes geradas de volta para DataFrames do Pandas
    df_tfidf_train = pd.DataFrame(matriz_train.toarray(), columns=nomes_colunas, index=X_train.index)
    df_tfidf_test = pd.DataFrame(matriz_test.toarray(), columns=nomes_colunas, index=X_test.index)

    # Junta as novas colunas com os dados originais e apaga a coluna de texto bruta
    X_train_final = pd.concat([X_train.drop(columns=[coluna]), df_tfidf_train], axis=1)
    X_test_final = pd.concat([X_test.drop(columns=[coluna]), df_tfidf_test], axis=1)

    print(f"[OK] Coluna '{coluna}' vetorizada com sucesso!")

    return X_train_final, X_test_final


def aplicar_smote(X_train, y_train):
    """
        Aplica o balanceamento sintético apenas na base de treino.
    """

    print("-" * 50)
    print("Aplicando SMOTE...")
    print("-" * 50)

    smote = SMOTE(random_state=42)

    print(f"[OK] SMOTE aplicado com sucesso!")

    return smote.fit_resample(X_train, y_train)


def executar_pipeline(caminho_base_tratada):
    """
        Orquestra toda a etapa de pré-processamento.
    """

    # 1. Carregamento da base tratada.
    df = pd.read_excel(caminho_base_tratada)

    # 2. Execução de transformações.
    df = isolar_variaveis(df)
    df = tratar_nulos(df)
    df = codificar_categoricas(df)
    df = normalizar_numericas(df)

    # 3. Divide as bases.
    X_train, X_test, y_train, y_test = dividir_bases(df)

    # 4. Vetoriza o texto da coluna 'objeto' com a base já dividida.
    X_train, X_test = vetorizar_texto(X_train, X_test, max_features=50)

    # 5. Aplica o SMOTE
    X_train_smote, y_train_smote = aplicar_smote(X_train, y_train)

    return X_train_smote, X_test, y_train_smote, y_test
