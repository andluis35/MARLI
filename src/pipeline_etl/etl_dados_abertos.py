import pandas as pd
from pathlib import Path
import re
import unicodedata


# Definição de caminhos absolutos no nível de orquestração.
BASE_DIR = Path(__file__).resolve().parent.parent.parent
CAMINHO_BASE_BRUTA = BASE_DIR / "data" / "raw"
CAMINHO_BASE_TRATADA = BASE_DIR / "data" / "processed"


def carregar_bases():
    """
        Transforma as bases de dados abertos .csv em DataFrames.
    """

    # Listagem dos arquivos sobre vencedores.
    arquivos_vencedores_municipios = [
        CAMINHO_BASE_BRUTA / "raw_base_vencedores_municipios_2024.csv",
        CAMINHO_BASE_BRUTA / "raw_base_vencedores_municipios_2025.csv",
        CAMINHO_BASE_BRUTA / "raw_base_vencedores_municipios_2026.csv"
    ]

    # Concatena os arquivos de Vencedores de Licitações dos Municípios do RJ em um único DataFrame.
    df_vencedores_m = pd.concat([pd.read_csv(f, sep=';') for f in arquivos_vencedores_municipios], ignore_index=True)

    # Transforma as bases .csv de Licitações em DataFrames
    df_licitacoes_m = pd.read_csv(CAMINHO_BASE_BRUTA / "raw_base_licitacoes_municipios.csv", sep=';')

    # Retira caracteres inválidos.
    df_licitacoes_m = df_licitacoes_m.replace(
        to_replace=r'[\x00-\x08\x0B\x0C\x0E-\x1F]',
        value='',
        regex=True
    )

    df_vencedores_m = df_vencedores_m.replace(
        to_replace=r'[\x00-\x08\x0B\x0C\x0E-\x1F]',
        value='',
        regex=True
    )

    return df_licitacoes_m, df_vencedores_m


def criar_chave_composta(df_licitacoes_m, df_vencedores_m):
    """
        Realiza a criação de uma chave composta dos campos 'Ente',
        'Modalidade', 'DataHomologacao' e 'ValorEstimado'.
    """

    df_licitacoes_m['chave_composta'] = (
        df_licitacoes_m['Ente'].astype(str) + "_" +
        df_licitacoes_m['Modalidade'].astype(str) + "_" +
        df_licitacoes_m['DataHomologacao'].astype(str) + "_" +
        df_licitacoes_m['ValorEstimado'].astype(str)
    )

    df_vencedores_m['chave_composta'] = (
        df_vencedores_m['Ente'].astype(str) + "_" +
        df_vencedores_m['Modalidade'].astype(str) + "_" +
        df_vencedores_m['DataHomologacao'].astype(str) + "_" +
        df_vencedores_m['ValorEstimado'].astype(str)
    )

    return df_licitacoes_m, df_vencedores_m


def limpar_nome_empresa(nome):
    """
        Realiza a normalização de nomes de empresas para reduzir duplicidades.
    """
    
    if pd.isna(nome):
        return "DESCONHECIDO"
    
    # 1. Padronização de CASE.
    nome = str(nome).upper()
    
    # 2. Remoção de acentos.
    nome = ''.join(
        c for c in unicodedata.normalize('NFKD', nome)
        if not unicodedata.combining(c)
    )
    
    # 3. Remoção de pontuações e caracteres especiais.
    nome = re.sub(r'[^\w\s]', ' ', nome)
    
    # 4. Remoção de sufixos e termos societários comuns
    sufixos_societarios = r'\b(LTDA|LIMITADA|SA|ME|EPP|EI|EIRELI|MEI|SS|EPP|M E|S A|UNIPESSOAL|SOCIEDADE|IND|COM|COMERCIO|SERVICOS|REPRESENTACOES)\b'
    nome = re.sub(sufixos_societarios, '', nome)
    
    # 5. Compressão de espaços.
    nome = re.sub(r'\s+', ' ', nome).strip()
    
    return nome


def testar_chave_candidata(df, chave_candidata='ProcessoLicitatorio'):
    """
        Verifica se a coluna 'ProcessoLicitatorio' possui valores únicos não-nulos, caracterizando-a como chave primária.
    """
    
    if chave_candidata in df.columns:
        eh_unique = df[chave_candidata].is_unique
        
        if eh_unique:
            print(f"[DIAGNÓSTICO] A coluna '{chave_candidata}' é uma chave única perfeita!")
        else:
            duplicadas = df.duplicated(subset=[chave_candidata]).sum()
            print(f"[DIAGNÓSTICO] A coluna '{chave_candidata}' NÃO É uma chave única perfeita!")
            print(f"[ALERTA] Foram encontradas {duplicadas} linhas com IDs de licitação repetidos.")


def executar_etl():
    """
        Realiza o ETL completo das bases brutas, garantindo a relação 1:1 (1 linha = 1 licitação).
    """

    print("\n" * 50)
    print("-" * 50)
    print("INICIANDO FASE 1: PIPELINE DE ETL (LIMPEZA)")
    print("-" * 50)
    
    # 1. Carrega as bases.
    df_licitacoes_municipios, df_vencedores_municipios = carregar_bases()
    print("[OK] Bases carregadas com sucesso!")

    # 2. Cria a chave composta com os atributos Ente/Unidade, Modalidade, DataHomologacao e ValorEstimado.
    df_licitacoes_municipios, df_vencedores_municipios = criar_chave_composta(
        df_licitacoes_m=df_licitacoes_municipios,
        df_vencedores_m=df_vencedores_municipios
    )
    print("[OK] Chave composta criada com sucesso!")
    
    # 3. Remove vencedores nulos.
    df_vencedores_municipios = df_vencedores_municipios.dropna(subset=['Participante']).copy()
    print("[OK] Campos nulos de vencedores removidos com sucesso!")

    # 4. Padroniza o nomne das empresas participantes.
    df_vencedores_municipios['ParticipantePadronizado'] = df_vencedores_municipios['Participante'].apply(limpar_nome_empresa)
    print("[OK] Nomes das empresas participantes padronizados com sucesso!")

    # 5. Calcula o histórico global.
    # 5.1 Remove as repetições de itens dentro da mesma licitação para a mesma empresa.
    df_vencedores_unicos_por_certame = df_vencedores_municipios.drop_duplicates(subset=['chave_composta', 'ParticipantePadronizado'])

    # 5.2 Calcula o histórico contando apenas licitações distintas. 
    historico_vencedores = df_vencedores_unicos_por_certame.groupby('ParticipantePadronizado').size().reset_index(name='HistoricoVitoriasEmpresaVencedora')

    # 6. Acopla o histórico das empresas na tabela de vencedores.
    df_vencedores_municipios = df_vencedores_municipios.merge(historico_vencedores, on='ParticipantePadronizado', how='left')

    # 7. Agrupa a base de vencedores para criar a relação 1 linha = 1 licitação.
    df_vencedores_agrupado = df_vencedores_municipios.groupby('chave_composta').agg({
        'ValorHomologacao': 'max',
        'QuantidadeParticipante': 'max',
        'HistoricoVitoriasEmpresaVencedora': 'max'
    }).reset_index()

    # 8. Acopla as licitações com os vencedores agrupados.
    df_marli = pd.merge(
        df_licitacoes_municipios,
        df_vencedores_agrupado,
        on='chave_composta',
        how='left'
    )
    print("[OK] Histórico das empresas vencedoras calculado e acoplado com sucesso!")

    # 9. Remove colunas desnecessárias.
    df_marli = df_marli.drop(columns=[
        'Unidade', 'Tipo', 'DataPublicacaoOficial',
        'DataHomologacao', 'DataPublicacaoEdital', 'Parecer',
        'AdiadoSineDie', 'OrcamentoSigiloso', 'chave_composta', 'PercentualRecursosUniao'
    ])
    print("[OK] Colunas sobressalentes removidas com sucesso!")

    # 10. Remove linhas com ao menos um valor nulo.
    df_marli = df_marli.dropna()
    print("[OK] Linhas com valores nulos removidas com sucesso!")

    # 11. Verifica se a coluna 'ProcessoLicitatorio' possui valores únicos e não nulos.
    testar_chave_candidata(df_marli)

    print(f"[OK] ETL Concluído. Total de licitações na base final: {len(df_marli)}")

    return df_marli
    