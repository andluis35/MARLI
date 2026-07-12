import numpy as np
from time import sleep


# Definição de constantes que representam os limiares das regras heurísticas.
QTD_MINIMA_PARTICIPANTES = 3
PERCENTUAL_DESCONTO_MINIMO = 5.0
LIMIAR_VITORIAS = 10


def calcular_score_de_risco(df_m):
    """
        Efetua o cálculo do score de risco baseado nas colunas do 'df_m'.
        Cada True vira 1 ponto; Cada False vira 0 pontos.
    """

    df_m['ScoreDeRisco'] = (
        (df_m['QuantidadeParticipante'] < QTD_MINIMA_PARTICIPANTES).astype(int) +
        (df_m['PercentualDesconto'] < PERCENTUAL_DESCONTO_MINIMO).astype(int) +
        (df_m['HistoricoVitoriasEmpresaVencedora'] >= LIMIAR_VITORIAS).astype(int) +
        (df_m['SemPublicidadePNCP'] == True).astype(int) +
        (df_m['ModalidadeDeRisco'] == True).astype(int)
    )

    print("[OK] Score de risco (0 a 5) calculado com sucesso!")

    return df_m


def criar_categoria_de_risco(df_m):
    """
        Categoriza as licitações em 'Baixo Risco', 'Médio Risco' ou 'Alto Risco'
        de acordo com a pontuação calculada em cada uma delas.
    """

    condicoes = [
        df_m['ScoreDeRisco'] <= 2,
        df_m['ScoreDeRisco'] == 3,
        df_m['ScoreDeRisco'] >= 4
    ]
    classes = ['Baixo Risco', 'Médio Risco', 'Alto Risco']

    df_m['Risco'] = np.select(condicoes, classes, default='Indefinido')
    
    print("[OK] Rótulos de classe (Baixo, Médio, Alto) atribuídos com sucesso!")

    return df_m


def executar_score(df_marli):
    """
        Calcula e acopla os scores e suas respectivas categorias às licitações.
    """
    
    print("\n" * 50)
    print("-" * 50)
    print("INICIANDO FASE 3: CÁLCULO DO SCORE DE RISCO")
    print("-" * 50)

    df_marli = calcular_score_de_risco(df_m=df_marli)
    df_marli = criar_categoria_de_risco(df_m=df_marli)

    # Exibe o grau de desbalanceamento da base.
    print("-" * 50)
    print("== DISTRIBUIÇÃO DAS CLASSES DE RISCO NA BASE ==")
    print(df_marli['Risco'].value_counts(normalize=True) * 100)
    print("\n== CONTAGEM ABSOLUTA ==")
    print(df_marli['Risco'].value_counts())
    print("-" * 50)
    sleep(2)

    return df_marli
