import hashlib
import pandas as pd
from pathlib import Path
import re
from time import sleep
import unicodedata


def padronizar_cabecalhos(df):
    """
        Padroniza os nomes das colunas para facilitar a manipulação.
        EX.: 'Valor Homologação' vira 'valor_homologacao'.
    """

    novas_colunas = []
    for col in df.columns:
        col_str = str(col)

        # Remove acentos (EX.: 'Licitação' vira 'Licitacao')
        col_str = unicodedata.normalize('NFKD', col_str).encode('ASCII', 'ignore').decode('utf-8')

        # Deixa tudo minúsculo, remove espaços extras nas pontas e substitui espaos internos por '_' (underscore)
        col_str = re.sub(r'\s+', '_', col_str.strip().lower())
        novas_colunas.append(col_str)

    df.columns = novas_colunas
    return df


def limpar_planilha_bi(caminho_arquivo):
    """
        Lê o arquivo Excel exportado do BI e remove sujeiras estruturais.
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
    """
        Verifica se a coluna 'licitacao' possui valores únicos não-nulos, caracterizando-a como chave primária.
    """
    
    if chave_candidata in df.columns:
        eh_unique = df[chave_candidata].is_unique
        
        if eh_unique:
            print(f"[DIAGNÓSTICO] A coluna '{chave_candidata}' é uma chave única perfeita!")
        else:
            duplicadas = df.duplicated(subset=[chave_candidata]).sum()
            print(f"[DIAGNÓSTICO] A coluna '{chave_candidata}' NÃO É uma chave única perfeita!")
            print(f"[ALERTA] Foram encontradas {duplicadas} linhas com IDs de licitação repetidos.")


def anonimizar_dado(valor):
    """
        Aplica o hash SHA-256 unidirecional no documento do fornecedor.
    """

    if pd.isna(valor):
        return valor
    
    # Remove qualuqer pontuação para garantir que o hash seja idêntico para o mesmo número
    valor_limpo = re.sub(r'\D', '', str(valor))

    # Retorna a string criptografada
    return hashlib.sha256(valor_limpo.encode('utf-8')).hexdigest()


def executar_etl(caminhos_raw):
    """
        Realiza o ETL completo das bases brutas.
    """

    # Configuração de diretórios absolutos
    BASE_EDITAIS = caminhos_raw / "raw_base_editais.xlsx"
    BASE_HOMOLOGACOES = caminhos_raw / "raw_base_homologacoes.xlsx"
    BASE_LICITACOES = caminhos_raw / "raw_base_licitacoes.xlsx"
    BASE_PARTICIPANTES = caminhos_raw / "raw_base_participantes.xlsx"
    
    print("\n" * 50)
    print("-" * 50)
    print("INICIANDO FASE 1: PIPELINE DE ETL (LIMPEZA)")
    print("-" * 50)

    # 1. Carrega e limpa as bases
    df_editais = limpar_planilha_bi(BASE_EDITAIS)
    df_homologacoes = limpar_planilha_bi(BASE_HOMOLOGACOES)
    df_licitacoes = limpar_planilha_bi(BASE_LICITACOES)
    df_participantes = limpar_planilha_bi(BASE_PARTICIPANTES)
    print("\n[OK] Bases carregadas e limpas com sucesso!")

    # 2. Verifica se a coluna 'licitacao' possui valores únicos e não-nulos
    testar_chave_candidata(df_licitacoes)

    # 3. Criptografa o identificador dos fornecedores/participantes das licitações
    df_participantes['hash_fornecedor'] = df_participantes['cpfcnpj'].apply(anonimizar_dado)
    df_participantes = df_participantes.drop(columns=['cpfcnpj'])
    print("[OK] Identificadores anonimizados com SHA-256 com sucesso!")

    # 4. Filtra somente as colunas que serão utilizadas de cada base
    df_editais = df_editais[['numeroedital', 'url_ultima_publicacao']]
    df_homologacoes = df_homologacoes[['licitacao', 'valor_homologacao']]
    df_licitacoes = df_licitacoes[['ano', 'mes', 'unidade_gestora', 'licitacao', 'numero_edital', 'modalidade', 'objeto', 'valor_estimado']]
    df_participantes = df_participantes.rename(columns={"'fatocotacaoitemparticipantelicitacao'[situacao]": "situacao"})
    df_participantes = df_participantes[['licitacao', 'hash_fornecedor', 'situacao']]
    print("[OK] Colunas filtradas com sucesso!")

    # 5. Resumo do processamento
    print("-" * 50)
    print("== RESUMO DAS BASES ==")
    print(f"Editais: {df_editais.shape}")
    print(f"Homologações: {df_homologacoes.shape}")
    print(f"Licitações: {df_licitacoes.shape}")
    print(f"Participantes: {df_participantes.shape}")
    print("-" * 50)
    sleep(2)

    return df_editais, df_homologacoes, df_licitacoes, df_participantes
