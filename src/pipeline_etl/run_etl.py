from calculo_heuristicas import executar_heuristicas
from calculo_score import executar_score
from etl_dados_abertos import executar_etl
from pathlib import Path
from time import sleep


# Definição de caminhos absolutos no nível de orquestração.
BASE_DIR = Path(__file__).resolve().parent.parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
OUTPUT_DIR = BASE_DIR / "data" / "processed"


def main():
    """
        Gera a base completa e tratada a partir dos dados brutos do TCE-RJ.
    """
    
    print("\n" * 50)
    print("=" * 50)
    print("Iniciando o Pipeline da MARLI...")
    print("=" * 50)
    sleep(1)

    # FASE 1: Extração e Limpeza.
    df_marli = executar_etl()

    # FASE 2: Cálculo das Heurísticas.
    df_marli = executar_heuristicas(df_marli)

    # FASE 4: Score e Rotulagem.
    df_marli = executar_score(df_marli)

    # SAÍDA: Base devidamente limpa, tratada e rotulada.
    df_marli.to_excel(OUTPUT_DIR / "base_marli_tratada.xlsx", index=False)

    print("-" * 50)
    print(f"[SUCESSO] Pipeline finalizado! Base exportada para: {OUTPUT_DIR}")
    print("-" * 50)


if __name__ == "__main__":
    main()
