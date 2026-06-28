import pandas as pd
from time import sleep


def merge_homologacao(df_m, df_h, qtd_linhas_originais):
    """
        Cruza os dados da base Master com a base de Homologações.
    """

    # Agrupa as licitações e soma o valor total de cada uma delas, já que uma
    # licitação pode ter vários itens homologados (várias linhas).
    df_homologacoes_agg = df_h.groupby('licitacao', as_index=False)['valor_homologacao'].sum()

    # Efetua o merge das bases em questão, usando a coluna 'licitacao' como chave.
    # how='left' adiciona as novas colunas de 'df_homologacoes_agg' à direita de 'df_m'.
    # Se uma licitação do 'df_m' não existir na tabela de homologações, preenche com nulo.
    df_m = pd.merge(df_m, df_homologacoes_agg, on='licitacao', how='left')

    # O teste booleano 'df_m.shape[0] == qtd_linhas_originais' verifica se não houve duplicações indevidas.
    print(f"[MERGE 1] Homologação acoplada. Linhas mantidas: {df_m.shape[0] == qtd_linhas_originais}")

    return df_m


def merge_editais(df_m, df_e, qtd_linhas_originais):
    """
        Cruza os dados da base Master com a base de Editais.
    """

    # Remove duplicatas da base de editais.
    df_editais_unique = df_e.drop_duplicates(subset=['numeroedital'])

    # Efetua o merge das bases em questão.
    # left_on='numero_edital' indica que 'numero_edital' do 'df_m' será a chave de ligação.
    # right_on='numeroedital' indica que a coluna correspondente do 'df_editais_unique' se chama 'numeroedital'.
    # how='left' adiciona as novas colunas de 'df_editais_unique' à direita de 'df_m'.
    df_m = pd.merge(
        df_m,
        df_editais_unique,
        left_on='numero_edital',
        right_on='numeroedital',
        how='left'
    )

    # Remove a coluna duplicada do número do edital gerada pelo cruzamento.
    if 'numeroedital' in df_m.columns:
        df_m = df_m.drop(columns=['numeroedital'])

    # O teste booleano 'df_m.shape[0] == qtd_linhas_originais' verifica se não houve duplicações indevidas.
    print(f"[MERGE 2] Editais acoplados. Linhas mantidas: {df_m.shape[0] == qtd_linhas_originais}")

    return df_m


def merge_participantes(df_m, df_p):
    """
        Cruza os dados da base de Licitações com a base de Participantes
    """

    # Inicialmente, 'df_participantes' ficará intacto e isolado na memória,
    # pois será utilizado futuramente para calcular e injetar as métricas de
    # Competitividade e Concentração de Vitórias diretamente no 'df_master'.
    # O merge não será feito para não multiplicar o número de linhas do 'df_master'.
    print(f"[STATUS] Base de Participantes reservada na memória para os cálculos heurísticos.")

    return df_m


def executar_cruzamento(df_editais, df_homologacoes, df_licitacoes, df_participantes):
    """
        Realiza o cruzamento das bases já limpas.
    """
    
    print("\n" * 50)
    print("-" * 50)
    print("INICIANDO FASE 2: CRUZAMENTO DAS BASES")
    print("-" * 50)

    df_master = df_licitacoes.copy()
    qtd_linhas_originais = df_master.shape[0]

    df_master = merge_homologacao(df_m=df_master, df_h=df_homologacoes, qtd_linhas_originais=qtd_linhas_originais)
    df_master = merge_editais(df_m=df_master, df_e=df_editais, qtd_linhas_originais=qtd_linhas_originais)
    df_master = merge_participantes(df_m=df_master, df_p=df_participantes)
    print("[OK] Bases acopladas com sucesso!")

    print("-" * 50)
    print("== RESUMO DO df_master APÓS CRUZAMENTOS ==\n")
    print(df_master.info())
    print("-" * 50)
    sleep(2)

    return df_master
    