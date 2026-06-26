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

    print("[1/5] Competitividade calculada.")

    return df_m


def acoplar_desconto(df_m):
    """
        Acopla o cálculo da diferença percentual entre o valor estimado e o valor homologado do certame.
    """

    # Garante que as colunas monetárias sejam tratadas como números (float).
    # errors='coerce' converte valores inválidos para dados nulos em vez de travar a execução.
    df_m['valor_estimado'] = pd.to_numeric(df_m['valor_estimado'], errors='coerce')
    df_m['valor_homologacao'] = pd.to_numeric(df_m['valor_homologacao'], errors='coerce')

    # Calcula e acopla o percentual, verificando se valor_estimado > 0 para evitar erro de divisão por zero.
    # Se o valor estimado for zero, negativo ou nulo, o desconto é configurado como 0.
    # Fórmula: ((Estimado - Homologado) / Estimado) * 100
    df_m['percentual_desconto'] = np.where(
        df_m['valor_estimado'] > 0,
        ((df_m['valor_estimado'] - df_m['valor_homologacao']) / df_m['valor_estimado']) * 100,
        0
    )

    print("[2/5] Desconto obtido calculado.")

    return df_m


def acoplar_publicidade(df_m):
    """
        Acopla a verificação feita se o certame foi publicado oficialmente ou não.
    """

    # Verifica se o campo 'url_ultima_publicacao' está vazio. Se sim, o novo campo
    # 'sem_publicidade' é preenchido com VERDADEIRO; caso contrário, é preenchido
    # com FALSO.
    df_m['sem_publicidade'] = (
        df_m['url_ultima_publicacao'].isna() |
        (df_m['url_ultima_publicacao'].astype(str).str.strip() == '') |
        (df_m['url_ultima_publicacao'].astype(str).str.lower() == 'nan')
    )

    print("[3/5] Rastreio de publicidade finalizado.")

    return df_m


def acoplar_concentracao_vitorias(df_m, df_p):
    """
        Acopla o histórico de domínio das empresas participantes dos certames.
    """

    # 1. Isola apenas os registros de vitória na base de participantes.
    vencedores = df_p[df_p['situacao'].str.contains('vencedor', case=False, na=False)]

    # 2. Conta quantas vitórias totais cada empresa (hash_fornecedor) tem na base inteira.
    vitorias_totais = vencedores.groupby('hash_fornecedor').size().reset_index(name='historico_vitorias_empresa_vencedora')

    # 3. Cruza esse histórico de volta para a tabela de vencedores, acoplando e associando
    # a nova coluna 'historico_vitorias_empresa_vencedora' a cada fornecedor 'hash_fornecedor'
    vencedores_com_historico = pd.merge(vencedores, vitorias_totais, on='hash_fornecedor', how='left')

    # 4. Agrupa pela licitação. Se houve múltiplos vencedores (ex.: consórcio ou itens diferentes), pegamos
    # o "pior caso" (o valor máximo de histórico entre os vencedores) para carimbar o risco.
    # .reset_index() transforma o resultado em um novo DataFrame limpo.
    risco_vitorias = vencedores_com_historico.groupby('licitacao')['historico_vitorias_empresa_vencedora'].max().reset_index()

    # 5. Acopla o indicador no 'df_m' utilizando 'licitacao' como chave.
    # how='left' adiciona a nova coluna de 'historico_vitorias_empresa_vencedora' à direita de 'df_m'
    # .fillna(0) preenche com 0 as licitações que não tiverem um vencedor lançado.
    df_m = pd.merge(df_m, risco_vitorias, on='licitacao', how='left')
    df_m['historico_vitorias_empresa_vencedora'] = df_m['historico_vitorias_empresa_vencedora'].fillna(0)

    print("[4/5] Concentração de vitórias rastreada.")

    return df_m


def acoplar_risco_modalidade(df_m):
    """
        Acopla a verificação de risco da modalidade do certame.
    """

    # Converte as colunas para string e maiúsculo para evitar falhas por case sensitivity
    df_m['modalidade'] = df_m['modalidade'].astype(str).str.upper()
    df_m['objeto'] = df_m['objeto'].astype(str).str.upper()

    # Verifica se as palavras-chave existem em qualquer uma das duas colunas
    condicao_modalidade = df_m['modalidade'].str.contains('DISPENSA|INEXIGIBILIDADE', na=False, regex=True)
    condicao_objeto = df_m['objeto'].str.contains('DISPENSA|INEXIGIBILIDADE', na=False, regex=True)

    # Cria uma coluna booleana (VERDADEIRO se encontrar em qualquer um dos dois lugares; FALSO caso contrário)
    df_m['modalidade_de_risco'] = condicao_modalidade | condicao_objeto

    print("[5/5] Modalidades de risco identificadas e sinalizadas.")

    return df_m


if __name__ == "__main__":
    print("\n" * 50)
    print("-" * 50)
    print("INICIANDO FASE 3: CÁLCULO DAS HEURÍSTICAS DE RISCO")
    print("-" * 50)

    df_master = acoplar_competitividade(df_m=df_master, df_p=df_participantes)
    df_master = acoplar_desconto(df_m=df_master)
    df_master = acoplar_publicidade(df_m=df_master)
    df_master = acoplar_concentracao_vitorias(df_m=df_master, df_p=df_participantes)
    df_master = acoplar_risco_modalidade(df_m=df_master)
    df_master.to_excel(CLEAN_DIR / "clean_base_master.xlsx", index=False)

    print("-" * 50)
    print("== AMOSTRA DAS MÉTRICAS CALCULADAS ==\n")
    print(df_master[['licitacao', 'qtd_participantes', 'percentual_desconto', 'sem_publicidade', 'historico_vitorias_empresa_vencedora', 'modalidade_de_risco']].head())
    print("-" * 50)
    sleep(2)
