from calculo_heuristicas import executar_heuristicas
from cruzamento_bases import executar_cruzamento
from etl_dados import executar_etl
from pathlib import Path
from time import sleep


# Definição de caminhos absolutos no nível de orquestração
BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
OUTPUT_DIR = BASE_DIR / "data" / "base_tratada.xlsx"


if __name__ == "__main__":
    print("\n" * 50)
    print("=" * 50)
    print("Iniciando o Pipeline da MARLI...")
    print("=" * 50)
    sleep(1)

    # FASE 1: Extração e Limpeza
    df_editais, df_homologacoes, df_licitacoes, df_participantes = executar_etl(RAW_DIR)

    # FASE 2: Cruzamento dos Dados
    df_master = executar_cruzamento(df_editais, df_homologacoes, df_licitacoes, df_participantes)

    # FASE 3: Cálculo das Heurísticas
    df_master = executar_heuristicas(df_master, df_participantes)
    