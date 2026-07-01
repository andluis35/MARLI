from pathlib import Path
from pre_processamento import executar_pipeline
from treinamento_modelos import treinar_modelos


# Definição de caminhos absolutos no nível de orquestração.
BASE_DIR = Path(__file__).resolve().parent.parent.parent
CAMINHO_BASE_TRATADA = BASE_DIR / "data" / "processed" / "base_tratada.xlsx"


def main():
    """
        Realiza o pré-processamento completo dos dados.
    """

    # 1. Separa os dados em conjuntos de TREINO e TESTE, realizando:
    # - Isolamento de variáveis preditivas e de rotulagem;
    # - Codificação via Label Encoding;
    # - Tratamento de valores nulos;
    # - Normalização via Standart Scaling;
    # - Vetorização do 'objeto' via TF-IDF;
    # - SMOTE.
    X_train_smote, X_test, y_train_smote, y_test = executar_pipeline(CAMINHO_BASE_TRATADA)

    # 2. Treina os modelos de acordo com os seguintes algoritmos de classificação:
    # - Logistic Regression
    # - Random Forest
    # - Gradient Boosting
    # - XGBoost
    modelos_prontos = treinar_modelos(X_train_smote, y_train_smote)

if __name__ == "__main__":
    main()
