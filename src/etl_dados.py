import pandas as pd
import unicodedata
import re
from pathlib import Path


def padronizar_cabecalhos(df):
    """
        Padroniza os nomes das colunas para facilitar a manipulação
        EX.: 'Valor Homologação' vira 'valor_homologacao'
    """

    novas_colunas = []
    for col in df.columns:
        col_str = str(col)

        # Remove acentos (EX.: 'Licitação' vira 'Licitacao')
        col_str = unicodedata.normalize('NFKD', col_str).encode('ASCII', 'ignore').decode('utf-8')

        # Deixa tudi minúsculo, remove espaços extras nas pontas e substitui espaos internos por '_' (underscore)
        col_str = re.sub(r'\s+', '_', col_str.strip().lower())
        novas_colunas.append(col_str)

    df.columns = novas_colunas
    return df


def limpar_planilha_bi(caminho_arquivo):
    """
        Lê o arquivo Excel exportado do BI e remove sujeiras estruturais
    """
    print(f"Lendo e processando: {caminho_arquivo.name}...")

    try:
        if caminho_arquivo.suffix in ['.xlsx', '.xls']:
            df = pd.read_excel(caminho_arquivo, header=2)
        else:
            raise ValueError(f"Formato {caminho_arquivo.suffix} não suportado.")

    except Exception as e:
        print(f"Erro ao ler o arquivo {caminho_arquivo.name}: {e}")
        return None
    
    # 1. Remove colunas que estejam 100% vazias
    df = df.dropna(axis=1, how='all')

    # 2. Remove linhas que estejam 100% vazias
    df = df.dropna(axis=0, how='all')

    # 3. Padroniza os cabeçalhos para o padrão Python pré-estabelecido
    df = padronizar_cabecalhos(df)

    return df


def testar_chave_candidata(df, chave_candidata='licitacao'):
    '''
        Verifica se a coluna 'licitacao' possui valores únicos não-nulos, caracterizando-a como chave primária
    '''
    
    if chave_candidata in df.columns:
        eh_unique = df[chave_candidata].is_unique
        print(f"\n[DIAGNÓSTICO] A coluna '{chave_candidata}' é uma chave única perfeita? -> {eh_unique}")

        if not eh_unique:
            duplicadas = df.duplicated(subset=[chave_candidata]).sum()
            print(f"[ALERTA] Foram encontradas {duplicadas} linhas com IDs de licitação repetidos.\n")


if __name__ == "__main__":
    # Configuração de diretórios absolutos
    BASE_DIR = Path(__file__).resolve().parent.parent
    RAW_DIR = BASE_DIR / "data" / "raw"
    CLEAN_DIR = BASE_DIR / "data" / "clean"
    BASE_LICITACOES = RAW_DIR / "raw_base_licitacoes.xlsx"
    BASE_LICITACOES_HOMOLOGADAS = RAW_DIR / "raw_base_licitacoes_homologadas.xlsx"
    BASE_PARTICIPANTES = RAW_DIR / "raw_base_participantes.xlsx"
    BASE_EDITAIS = RAW_DIR / "raw_base_editais.xlsx"
    
    print("-" * 50)
    print("INICIANDO FASE 1: PIPELINE DE ETL (LIMPEZA)")
    print("-" * 50)

    # 1. Carrega e limpa as bases
    df_licitacoes = limpar_planilha_bi(BASE_LICITACOES)
    df_licitacoes_homologadas = limpar_planilha_bi(BASE_LICITACOES_HOMOLOGADAS)
    df_participantes = limpar_planilha_bi(BASE_PARTICIPANTES)
    df_editais = limpar_planilha_bi(BASE_EDITAIS)

    # 2. Verifica se a coluna 'licitacao' possui valores únicos e não-nulos
    testar_chave_candidata(df_licitacoes)

    # 3. Salva as bases limpas
    df_licitacoes.to_excel(CLEAN_DIR / "clean_base_licitacoes.xlsx", index=False)
    df_licitacoes_homologadas.to_excel(CLEAN_DIR / "clean_base_licitacoes_homologadas.xlsx", index=False)
    df_participantes.to_excel(CLEAN_DIR / "clean_base_participantes.xlsx", index=False)
    df_editais.to_excel(CLEAN_DIR / "clean_base_editais.xlsx", index=False)

    print("-" * 50)
    print("Bases processadas e limpas com sucesso!")
    print("-" * 50)
