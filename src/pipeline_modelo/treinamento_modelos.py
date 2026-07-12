from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
import time
from xgboost import XGBClassifier


def treinar_modelos(X_train_smote, y_train_smote):
    """
        Instancia, treina e armazena os quatro algoritmos de 
        classificação na base de treinamento já balanceada.
    """

    print("-" * 50)
    print("Iniciando o treinamento dos modelos da MARLI...")
    print("-" * 50)

    # Define os algoritmos e seus respectivos hiperparâmetros.
    modelos = {
        "Logistic Regression": LogisticRegression(
            max_iter=2000,
            random_state=42
        ),
        "Random Forest": RandomForestClassifier(
            n_estimators=500,
            max_depth=15,
            min_samples_leaf=5,
            class_weight="balanced_subsample",
            random_state=42,
            n_jobs=-1
        ),
        "Gradient Boosting": GradientBoostingClassifier(
            random_state=42
        ),
        "XGBoost": XGBClassifier(
            n_estimators=500,
            max_depth=5,
            learning_rate=0.03,
            subsample=0.8,
            colsample_bytree=0.8,
            gamma=1,
            min_child_weight=3,
            objective="multi:softprob",
            eval_metric="mlogloss",
            random_state=42,
            n_jobs=-1
        )
    }

    modelos_treinados = {}

    # Percorre todos os algoritmos realizando treinamento e medição do tempo de execução.
    for nome_modelo, algoritmo in modelos.items():
        print("-" * 50)
        print(f"Treinando {nome_modelo}...")
        print("-" * 50)

        inicio = time.perf_counter()

        algoritmo.fit(X_train_smote, y_train_smote)

        fim = time.perf_counter()
        tempo_execucao = fim - inicio

        print(f"[OK] {nome_modelo} treinado com sucesso em {tempo_execucao:.2f} segundos.")

        # Armazena o modelo já treinado para utilização na etapa de avaliação.
        modelos_treinados[nome_modelo] = algoritmo

    print("-" * 50)
    print("[SUCESSO] Etapa de treinamento concluída.")
    print("-" * 50)
    return modelos_treinados
