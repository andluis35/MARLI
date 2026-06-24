import pandas as pd
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
CLEAN_DIR = BASE_DIR / "data" / "clean"
BASE_EDITAIS = CLEAN_DIR / "clean_base_editais.xlsx"
BASE_HOMOLOGACOES = CLEAN_DIR / "clean_base_homologacoes.xlsx"
BASE_LICITACOES = CLEAN_DIR / "clean_base_licitacoes.xlsx"
BASE_PARTICIPANTES = CLEAN_DIR / "clean_base_participantes.xlsx"

df_editais = pd.read_excel(BASE_EDITAIS)
df_homologacoes = pd.read_excel(BASE_HOMOLOGACOES)
df_licitacoes = pd.read_excel(BASE_LICITACOES)
df_participantes = pd.read_excel(BASE_PARTICIPANTES)
df_master = df_licitacoes.copy()
qtd_linhas_originais = df_master.shape[0]


def merge_homologacao(df_master):
    """
        Cruza os dados da base de Licitações com a base de Homologações
    """

    # Agrupa as licitações e soma o valor total de cada uma delas, já que uma
    # licitação pode ter vários itens homologados (várias linhas)
    df_homologacoes_agg = df_homologacoes.groupby('licitacao', as_index=False)['valor_homologacao'].sum()

    # Efetua o merge das bases em questão, usando a coluna 'licitacao' como chave.
    # how='left' adiciona as novas colunas de df_homologacoes_agg à direita de df_master.
    # Se uma licitação do df_master não existir na tabela de homologações, preenche com nulo
    # O teste booleano df_master.shape[0] == qtd_linhas_originais verifica se não houve duplicações indevidas.
    df_master = pd.merge(df_master, df_homologacoes_agg, on='licitacao', how='left')
    print(f"[MERGE 1] Homologação acoplada. Linhas mantidas: {df_master.shape[0] == qtd_linhas_originais}")

    return df_master


def merge_editais(df_master):
    pass


def merge_participantes(df_master):
    pass

    
if __name__ == "__main__":
    print("\n")
    print("-" * 50)
    print("INICIANDO FASE 2: CRUZAMENTO DAS BASES")
    print("-" * 50)

    df_master = merge_homologacao(df_master)
