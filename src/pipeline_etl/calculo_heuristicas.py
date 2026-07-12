import numpy as np
import pandas as pd
from time import sleep


def acoplar_desconto(df_m):
    """
        Acopla o cálculo da diferença percentual entre o valor estimado e o valor homologado do certame.
    """

    # Garante que as colunas monetárias sejam tratadas como números (float).
    # errors='coerce' converte valores inválidos para dados nulos em vez de travar a execução.
    df_m['ValorEstimado'] = pd.to_numeric(df_m['ValorEstimado'], errors='coerce')
    df_m['ValorHomologacao'] = pd.to_numeric(df_m['ValorHomologacao'], errors='coerce')

    # Calcula e acopla o percentual, verificando se ValorEstimado > 0 para evitar erro de divisão por zero.
    # Se o valor estimado for zero, negativo ou nulo, o desconto é configurado como 0.
    # Fórmula: ((Estimado - Homologado) / Estimado) * 100
    df_m['PercentualDesconto'] = np.where(
        df_m['ValorEstimado'] > 0,
        ((df_m['ValorEstimado'] - df_m['ValorHomologacao']) / df_m['ValorEstimado']) * 100,
        0
    )

    print("[1/3] Desconto obtido calculado.")

    return df_m


def acoplar_publicidade(df_m):
    """
        Acopla a verificação feita se o certame foi publicado oficialmente ou não.
    """

    # Verifica se o campo 'PublicacaoOficial' possui 'PNCP' como substring (requisito legal). 
    # Se sim, o novo campo 'SemPublicidadePNCP' é preenchido com VERDADEIRO; caso contrário, 
    # é preenchido com FALSO.
    df_m['SemPublicidadePNCP'] = ~df_m['PublicacaoOficial'].astype(str).str.contains('PNCP', case=False, na=False)

    print("[2/3] Rastreio de publicidade finalizado.")

    return df_m


def acoplar_risco_modalidade(df_m):
    """
        Acopla a verificação de risco da modalidade do certame.
    """

    # Converte as colunas para string e maiúsculo para evitar falhas por case sensitivity.
    df_m['Modalidade'] = df_m['Modalidade'].astype(str).str.upper()
    df_m['Objeto'] = df_m['Objeto'].astype(str).str.upper()

    # Verifica se as palavras-chave existem em qualquer uma das duas colunas.
    condicao_modalidade = df_m['Modalidade'].str.contains('DISPENSA|INEXIGIBILIDADE', na=False, regex=True)
    condicao_objeto = df_m['Objeto'].str.contains('DISPENSA|INEXIGIBILIDADE', na=False, regex=True)

    # Cria uma coluna booleana (VERDADEIRO se encontrar em qualquer um dos dois lugares; FALSO caso contrário).
    df_m['ModalidadeDeRisco'] = condicao_modalidade | condicao_objeto

    print("[3/3] Modalidades de risco identificadas e sinalizadas.")

    return df_m


def executar_heuristicas(df_marli):
    """
        Calcula e acopla as heurísticas no df_marli.
    """
    
    print("\n" * 50)
    print("-" * 50)
    print("INICIANDO FASE 2: CÁLCULO DAS HEURÍSTICAS DE RISCO")
    print("-" * 50)

    df_marli = acoplar_desconto(df_m=df_marli)
    df_marli = acoplar_publicidade(df_m=df_marli)
    df_marli = acoplar_risco_modalidade(df_m=df_marli)

    print("[OK] Heurísticas calculadas e acopladas com sucesso!")

    return df_marli
