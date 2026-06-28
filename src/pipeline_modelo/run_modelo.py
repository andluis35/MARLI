from pathlib import Path
from pre_processamento import executar_pipeline


# Definição de caminhos absolutos no nível de orquestração.
BASE_DIR = Path(__file__).resolve().parent.parent.parent
CAMINHO_BASE_TRATADA = BASE_DIR / "data" / "processed" / "base_tratada.xlsx"


def main():
    """
        Realiza o pré-processamento completo dos dados.
    """

    print("\n" * 50)
    print("-" * 50)
    print("Iniciando pipeline de modelagem da MARLI...")
    print("-" * 50)

    # 1. Separa os dados em conjuntos de TREINO e TESTE, realizando:
    # - Isolamento de variáveis preditivas e de rotulagem;
    # - Tratamento de valores nulos;
    # - Normalização;
    # - SMOTE no conjunto de TREINO.
    X_train, X_test, y_train, y_test = executar_pipeline(CAMINHO_BASE_TRATADA)

    print("-" * 50)
    print("[SUCESSO] Dados prontos!")
    print("-" * 50)


if __name__ == "__main__":
    main()
