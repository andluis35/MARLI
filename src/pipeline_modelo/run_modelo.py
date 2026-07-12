from avaliacao_modelos import avaliar_modelos, plotar_importancia_variaveis
from pathlib import Path
from pre_processamento import executar_pipeline
from treinamento_modelos import treinar_modelos


# Definição de caminhos absolutos no nível de orquestração.
BASE_DIR = Path(__file__).resolve().parent.parent.parent
CAMINHO_BASE_TRATADA = BASE_DIR / "data" / "processed" / "base_marli_tratada.xlsx"


def main():
    """
        Realiza o pré-processamento completo dos dados.
    """

    # 1. Separa os dados em conjuntos de TREINO e TESTE, realizando:
    # - Isolamento de variáveis preditivas e de rotulagem;
    # - Codificação via Label Encoding;
    # - Tratamento de valores nulos;
    # - Normalização via Standard Scaling;
    # - Vetorização do 'objeto' via TF-IDF;
    # - SMOTE.
    X_train_smote, X_test, y_train_smote, y_test = executar_pipeline(CAMINHO_BASE_TRATADA)

    # 2. Treina os modelos de acordo com os seguintes algoritmos de classificação:
    # - Logistic Regression;
    # - Random Forest;
    # - Gradient Boosting;
    # - XGBoost.
    modelos_prontos = treinar_modelos(X_train_smote, y_train_smote)

    # 3. Avalia os modelos e gera os gráficos.
    resumo_metricas = avaliar_modelos(modelos_prontos, X_test, y_test)

    # 4. Extrai a Feature Importance do melhor modelo.
    feature_importance = plotar_importancia_variaveis(modelos_prontos, X_train_smote, nome_melhor_modelo='Random Forest', top_n=15)

    print("[SUCESSO] Pipeline finalizado!")


if __name__ == "__main__":
    main()
