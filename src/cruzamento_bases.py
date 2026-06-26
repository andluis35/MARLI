import pandas as pd
from pathlib import Path
from time import sleep


# Definição de caminhos absolutos e DataFrames
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
    # how='left' adiciona as novas colunas de 'df_homologacoes_agg' à direita de 'df_master'.
    # Se uma licitação do 'df_master' não existir na tabela de homologações, preenche com nulo.
    df_master = pd.merge(df_master, df_homologacoes_agg, on='licitacao', how='left')

    # O teste booleano 'df_master.shape[0] == qtd_linhas_originais' verifica se não houve duplicações indevidas.
    print(f"[MERGE 1] Homologação acoplada. Linhas mantidas: {df_master.shape[0] == qtd_linhas_originais}")

    return df_master


def merge_editais(df_master):
    """
        Cruza os dados da base de Licitações com a base de Editais
    """

    # Remove duplicatas da base de editais
    df_editais_unique = df_editais.drop_duplicates(subset=['numeroedital'])

    # Efetua o merge das bases em questão.
    # left_on='numero_edital' indica que 'numero_edital' do 'df_master' será a chave de ligação.
    # right_on='numeroedital' indica que a coluna correspondente do 'df_editais_unique' se chama 'numeroedital'.
    # how='left' adiciona as novas colunas de 'df_editais_unique' à direita de 'df_master'.
    df_master = pd.merge(
        df_master,
        df_editais_unique,
        left_on='numero_edital',
        right_on='numeroedital',
        how='left'
    )

    # Remove a coluna duplicada do número do edital gerada pelo cruzamento
    if 'numeroedital' in df_master.columns:
        df_master = df_master.drop(columns=['numeroedital'])

    # O teste booleano 'df_master.shape[0] == qtd_linhas_originais' verifica se não houve duplicações indevidas.
    print(f"[MERGE 2] Editais acoplados. Linhas mantidas: {df_master.shape[0] == qtd_linhas_originais}")

    return df_master


def merge_participantes(df_master):
    """
        Cruza os dados da base de Licitações com a base de Participantes
    """

    # Inicialmente, 'df_participantes' ficará intacto e isolado na memória,
    # pois será utilizado futuramente para calcular e injetar as métricas de
    # Competitividade e Concentração de Vitórias diretamente no 'df_master'.
    # O merge não será feito para não multiplicar o número de linhas do 'df_master'.
    print(f"[STATUS] Base de Participantes reservada na memória para os cálculos heurísticos.")

    return df_master


if __name__ == "__main__":
    print("\n" * 50)
    print("-" * 50)
    print("INICIANDO FASE 2: CRUZAMENTO DAS BASES")
    print("-" * 50)

    df_master = merge_homologacao(df_master)
    df_master = merge_editais(df_master)
    df_master = merge_participantes(df_master)
    df_master.to_excel(CLEAN_DIR / "clean_base_master.xlsx", index=False)
    print("[OK] Bases acopladas e salvas com sucesso!")

    print("-" * 50)
    print("== RESUMO DO df_master APÓS CRUZAMENTOS ==\n")
    print(df_master.info())
    print("-" * 50)
    sleep(2)
    