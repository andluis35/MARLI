# MARLI
### Modelo de Análise de Risco em Licitações via Machine Learning

**MARLI** (Modelo de Análise de Risco em Licitações) é uma ferramenta desenvolvida como Trabalho de Conclusão de Curso em Ciência da Computação na Universidade do Estado do Rio de Janeiro (UERJ).

* O projeto utiliza técnicas de **Aprendizado de Máquina**, **Processamento de Linguagem Natural (NLP)** e **Análise Exploratória de Dados** para classificar processos licitatórios municipais em três níveis de risco (**Baixo**, **Médio** e **Alto**), fornecendo uma ferramenta de apoio à priorização de auditorias realizadas pelos Tribunais de Contas.

* A base utilizada é composta por dados públicos disponibilizados pelo **Tribunal de Contas do Estado do Rio de Janeiro (TCE-RJ)** por meio de seus painéis de Business Intelligence (BI), abrangendo licitações de **91 municípios fluminenses**.

---

# Objetivo

O projeto busca responder à seguinte questão:

> É possível utilizar técnicas de Machine Learning para identificar padrões em licitações públicas e apoiar a priorização de auditorias realizadas pelos órgãos de Controle Externo?

Para isso foi desenvolvida uma pipeline completa envolvendo:

- coleta dos dados;
- integração entre diferentes bases;
- tratamento e limpeza;
- engenharia de atributos;
- geração da variável alvo;
- treinamento de modelos supervisionados;
- avaliação estatística.

---

# Tecnologias Utilizadas

## Linguagem

- Python

## Bibliotecas

- Pandas
- NumPy
- Scikit-Learn
- XGBoost
- NLTK
- Imbalanced-Learn (SMOTE)
- Matplotlib
- Seaborn

## Ambiente

- Jupyter Notebook
- Visual Studio Code

---

# Estrutura do Projeto

```text
MARLI/
│
├── data/
│   ├── raw/                 # Bases extraídas do Portal BI
│   └── processed/           # Dataset final utilizado pelo modelo
│
├── notebooks/
│   └── 01_analise_exploratoria.ipynb
│
├── docs/
│   └── plots/               # Figuras geradas na execução
│
├── requirements.txt
├── README.md
└── .gitignore
```

---

# Pipeline do Projeto

A arquitetura da solução é composta pelas seguintes etapas:

1. Extração das bases públicas do Portal BI do TCE-RJ;
2. Integração entre licitações e vencedores;
3. Limpeza e tratamento dos dados;
4. Construção das heurísticas de risco;
5. Geração do Score MARLI;
6. Vetorização textual utilizando TF-IDF;
7. Divisão Treino/Teste;
8. Normalização das variáveis numéricas;
9. Balanceamento das classes utilizando SMOTE;
10. Treinamento dos modelos;
11. Avaliação por métricas estatísticas.

---

# Modelos Avaliados

Foram comparados quatro algoritmos supervisionados:

- Logistic Regression
- Random Forest
- Gradient Boosting
- XGBoost

A comparação foi realizada utilizando:

- Accuracy
- Precision
- Recall
- F1-Score
- ROC-AUC
- Matrizes de Confusão

O modelo com melhor desempenho foi o **Random Forest**, apresentando aproximadamente:

| Métrica | Valor |
|----------|--------|
| Accuracy | 0.73 |
| Precision (Macro) | 0.55 |
| Recall (Macro) | 0.50 |
| F1-Score (Macro) | 0.52 |
| ROC-AUC | 0.72 |

---

# Variáveis Utilizadas

Entre as principais variáveis empregadas pelo modelo destacam-se:

- Valor estimado da contratação;
- Modalidade da licitação;
- Município (Ente);
- Quantidade de participantes;
- Percentual de desconto obtido;
- Histórico de vitórias do fornecedor;
- Representação textual do objeto da licitação por TF-IDF.

---

# Funcionalidades

O projeto contempla:

- integração automática entre bases;
- geração do score heurístico de risco;
- engenharia de atributos;
- classificação em três níveis de risco;
- comparação entre algoritmos;
- geração automática de métricas;
- geração de matrizes de confusão;
- geração de curvas ROC;
- análise de importância das variáveis (Feature Importance).

---

# Como Executar

## 1. Clonar o repositório

```bash
git clone https://github.com/andluis35/MARLI

cd MARLI
```

## 2. Criar ambiente virtual

```bash
python -m venv venv
```

Windows

```bash
venv\Scripts\activate
```

Linux

```bash
source venv/bin/activate
```

## 3. Instalar dependências

```bash
pip install -r requirements.txt
```

## 4. Executar o orquestrador do ETL de dados

```bash
python src/pipeline_etl/run_etl.py
```

## 5. Executar o orquestrador dos modelos de ML

```bash
python src/pipeline_modelo/run_modelo.py
```

---

# Trabalhos Futuros

- Integração com a API pública do TCE-RJ;
- Inclusão das licitações estaduais para ampliar a base de treinamento;
- Desenvolvimento de dashboard em Streamlit e implantação em servidor institucional;
- Aperfeiçoamento do sistema de pontuação de heurísticas.

---

# Autor

**Anderson Luis**

Graduando em Ciência da Computação

Universidade do Estado do Rio de Janeiro (UERJ)

---

# Licença

Este projeto foi desenvolvido exclusivamente para fins acadêmicos como Trabalho de Conclusão de Curso.