import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve
)
from sklearn.preprocessing import label_binarize


def avaliar_modelos(modelos_treinados, X_test, y_test):
    """
        Realiza predições no conjunto de teste, extraindo as
        métricas de avaliação para cada modelo.
    """
    
    print("-" * 50)
    print("INICIANDO AVALIAÇÃO DE MODELOS...")
    print("-" * 50)

    classe_nomes = ['Baixo Risco', 'Médio Risco', 'Alto Risco']
    y_test_bin = label_binarize(y_test, classes=[0, 1, 2])
    n_classes = y_test_bin.shape[1]
    resultados = {}

    for nome, modelo in modelos_treinados.items():
        print(f"[{nome}] Gerando predições...")

        y_pred = modelo.predict(X_test)

        try:
            y_proba = modelo.predict_proba(X_test)
        except AttributeError:
            print(f"[AVISO] {nome} não suporta predict_proba. ROC-AUC será ignorado.")
            y_proba = None

        acuracia = accuracy_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred, average='macro')
        precisao = precision_score(y_test, y_pred, average='macro')
        recall = recall_score(y_test, y_pred, average='macro')

        resultados[nome] = {
            'Acurácia': acuracia,
            'F1-Score': f1,
            'Precisão': precisao,
            'Recall': recall
        }

        print(f"== RELATÓRIO DE CLASSIFICAÇÃO - {nome} ==")
        print(classification_report(y_test, y_pred, target_names=classe_nomes))

        # PLOT 1: Matriz de Confusão.
        cm = confusion_matrix(y_test, y_pred)
        plt.figure(figsize=(6, 5))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=classe_nomes, yticklabels=classe_nomes)
        plt.title(f"Matriz de Confusão - {nome}")
        plt.ylabel("Risco Real")
        plt.xlabel("Risco Previsto")
        plt.tight_layout()
        plt.show()

        # PLOT 2: Curva ROC-AUC.
        if y_proba is not None:
            roc_auc_macro = roc_auc_score(y_test, y_proba, multi_class='ovr', average='macro')
            resultados[nome]['ROC-AUC'] = roc_auc_macro

            plt.figure(figsize=(8, 6))
            cores = ['green', 'orange', 'red']

            for i in range(n_classes):
                fpr, tpr, _ = roc_curve(y_test_bin[:, i], y_proba[:, i])
                auc_score = roc_auc_score(y_test_bin[:, i], y_proba[:, i])
                plt.plot(fpr, tpr, color=cores[i], lw=2, label=f'ROC {classe_nomes[i]} (AUC = {auc_score:.3f})')

            plt.plot([0, 1], [0, 1], 'k--', lw=2, label='Aleatório (AUC = 0.500)')
            plt.xlim([0.0, 1.0])
            plt.ylim([0.0, 1.05])
            plt.xlabel("Taxa de Falsos Positivos (FPR)")
            plt.ylabel("Taxa de Verdadeiros Positivos (TPR - RECALL)")
            plt.title(f"Curva ROC - {nome}")
            plt.legend(loc='lower right')
            plt.tight_layout()
            plt.show()

    print("== RESUMO DO DESEMPENHO ==")
    df_resumo = pd.DataFrame(resultados).T
    colunas_ordenadas = ['Acurácia', 'Precisão', 'Recall', 'F1-Score', 'ROC-AUC']
    colunas_finais = [col for col in colunas_ordenadas if col in df_resumo.columns]
    df_resumo = df_resumo[colunas_finais]

    print(df_resumo.to_markdown())

    return df_resumo
