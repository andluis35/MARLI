import numpy as np
import pandas as pd
from pathlib import Path
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

    df_m['score_de_risco'] = (
        (df_m['qtd_participantes'] < QTD_MINIMA_PARTICIPANTES).astype(int) +
        (df_m['percentual_desconto'] < PERCENTUAL_DESCONTO_MINIMO).astype(int) +
        (df_m['historico_vitorias_empresa_vencedora'] >= LIMIAR_VITORIAS).astype(int) +
        (df_m['sem_publicidade'] == True).astype(int) +
        (df_m['modalidade_de_risco'] == True).astype(int)
    )

    print("[OK] Score de risco (0 a 5) calculado com sucesso.")

    return df_m


def criar_categoria_de_risco(df_m):
    """
        Categoriza as licitações em 'Baixo Risco', 'Médio Risco' ou 'Alto Risco'
        de acordo com a pontuação calculada em cada uma delas.
    """

    condicoes = [
        df_m['score_de_risco'] <= 1,
        df_m['score_de_risco'].isin([2, 3]),
        df_m['score_de_risco'] >= 4
    ]
    classes = ['Baixo Risco', 'Médio Risco', 'Alto Risco']

    df_m['risco'] = np.select(condicoes, classes, default='Indefinido')
    
    print("[OK] Rótulos de classe (Baixo, Médio, Alto) atribuídos com sucesso.")

    return df_m


def executar_score(df_master):
    """
        Calcula e acopla os scores e suas respectivas categorias às licitações.
    """
    
    print("\n" * 50)
    print("-" * 50)
    print("INICIANDO FASE 4: CÁLCULO DO SCORE DE RISCO")
    print("-" * 50)

    df_master = calcular_score_de_risco(df_m=df_master)
    df_master = criar_categoria_de_risco(df_m=df_master)

    # Exibe o grau de desbalanceamento da base.
    print("-" * 50)
    print("== DISTRIBUIÇÃO DAS CLASSES DE RISCO NA BASE ==")
    print(df_master['risco'].value_counts(normalize=True) * 100)
    print("\n== CONTAGEM ABSOLUTA ==")
    print(df_master['risco'].value_counts())
    print("-" * 50)
    sleep(2)

    return df_master
