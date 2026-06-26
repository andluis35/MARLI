import numpy as np
import pandas as pd
from pathlib import Path
from time import sleep


# Definição de caminhos absolutos e DataFrames
BASE_DIR = Path(__file__).resolve().parent.parent
CLEAN_DIR = BASE_DIR / "data" / "clean"
BASE_MASTER = CLEAN_DIR / "clean_base_master.xlsx"
BASE_PARTICIPANTES = CLEAN_DIR / "clean_base_participantes.xlsx"

df_master = pd.read_excel(BASE_MASTER)
df_participantes = pd.read_excel(BASE_PARTICIPANTES)


def acoplar_competitividade(df_m, df_p):
    """
        Acopla a contagem de fornecedores únicos que participaram do certame.
    """

    # 'df_p.groupby('licitacao')' agrupa os dados de 'df_p' com base na coluna 'licitacao'.
    # ['hash_fornecedor'].nunique() conta quantos fornecedores distintos existem em cada licitação.
    # .reset_index(name='qtd_participantes') transforma o resultado em um novo DataFrame limpo.
    competitividade = df_p.groupby('licitacao')['hash_fornecedor'].nunique().reset_index(name='qtd_participantes')
    
    # Acopla a base 'competitividade' gerada com o 'df_m', utilizando 'licitacao' como chave.
    # how='left' adiciona a nova coluna de 'competitivdade' à direita de 'df_m'
    df_m = pd.merge(df_m, competitividade, on='licitacao', how='left')

    # Preenche com '0' as licitações que não obtiverem informações sobre participantes
    df_m['qtd_participantes'] = df_m['qtd_participantes'].fillna(0)

    print("[1/4] Competitividade calculada.")

    return df_m


def acoplar_desconto(df_m):
    """
        Acopla o cálculo da diferença percentual entre o valor estimado e o valor homologado do certame.
    """

    # Garante que as colunas monetárias sejam tratadas como números (float).
    # errors='coerce' converte valores inválidos para dados nulos em vez de travar a execução.
    df_m['valor_estimado'] = pd.to_numeric(df_m['valor_estimado'], errors='coerce')
    df_m['valor_homologacao'] = pd.to_numeric(df_m['valor_homologacao'], errors='coerce')

    # Calcula o percentual, verificando se valor_estimado > 0 para evitar erro de divisão por zero.
    # Se o valor estimado for zero, negativo ou nulo, o desconto é configurado como 0.
    # Fórmula: ((Estimado - Homologado) / Estimado) * 100
    df_m['percentual_desconto'] = np.where(
        df_m['valor_estimado'] > 0,
        ((df_m['valor_estimado'] - df_m['valor_homologacao']) / df_m['valor_estimado']) * 100,
        0
    )

    print("[2/4] Desconto obtido calculado.")

    return df_m


def acoplar_publicidade(df_m):
    pass

def acoplar_concentracao_vitorias(df_m, df_p):
    pass


def acoplar_risco_modalidade(df_m):
    pass


def calcular_score_risco(df_m):
    pass


if __name__ == "__main__":
    print("\n" * 50)
    print("-" * 50)
    print("INICIANDO FASE 3: CÁLCULO DAS HEURÍSTICAS DE RISCO")
    print("-" * 50)

    df_master = acoplar_competitividade(df_m=df_master, df_p=df_participantes)
    df_master = acoplar_desconto(df_m=df_master)
