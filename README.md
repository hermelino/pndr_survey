# pndr_survey

Revisão sistemática da literatura empírica sobre os instrumentos da Política Nacional de Desenvolvimento Regional (PNDR), cobrindo estudos publicados entre 2005 e 2025.

## Objetivo

Identificar, classificar e sintetizar as evidências empíricas sobre o impacto dos três grupos de instrumentos da PNDR:

- **Fundos Constitucionais** (FNE, FNO, FCO)
- **Fundos de Desenvolvimento** (FDNE, FDA, FDCO)
- **Incentivos Fiscais** (SUDENE, SUDAM)

O projeto combina busca manual em bases acadêmicas com análise automatizada via LLM (Gemini) para extrair informações estruturadas de cada artigo.

## Estrutura do Projeto

```
pndr_survey/
├── latex/                  # Artigo LaTeX
│   └── main.tex
├── scripts/                # Pipeline de extração e análise
│   ├── config.yaml         # Configuração central
│   ├── src/
│   │   ├── models.py       # Modelo de dados (PaperRecord)
│   │   ├── config.py       # Carregamento de configuração
│   │   ├── analyzers/
│   │   │   └── llm_analyzer.py
│   │   ├── extractors/
│   │   │   └── pdf_extractor.py
│   │   ├── exporters/
│   │   │   ├── excel_exporter.py
│   │   │   └── csv_exporter.py
│   │   └── utils/
│   │       ├── logger.py
│   │       └── file_utils.py
│   ├── questionnaires/     # Questionários JSON para análise LLM
│   └── main.py             # Ponto de entrada
├── data/                   # Dados (não versionados)
│   ├── papers/             # PDFs dos artigos
│   └── processed/          # Resultados da análise
├── figures/                # Figuras para o artigo
└── docs/                   # Documentação adicional
    └── PLAN.md             # Plano de construção
```

## Pipeline

```
PDFs dos artigos
    │
    ▼
[1] Extração de texto (pdfplumber)
    │
    ▼
[2] Análise via LLM (Gemini)
    │   Etapa 1: Triagem — é estudo empírico sobre PNDR?
    │   Etapa 2: Metodologia — métodos, variáveis, período, região
    │   Etapa 3: Resultados — instrumentos avaliados, efeitos, significância
    │
    ▼
[3] Exportação (Excel/CSV estruturado)
    │
    ▼
[4] Síntese para o artigo LaTeX
```

## Etapas do Projeto

| # | Etapa | Status |
|---|-------|--------|
| 1 | Esqueleto do projeto e documentação | Concluído |
| 2 | Configuração e modelo de dados | Pendente |
| 3 | Extrator de texto de PDFs | Pendente |
| 4 | Analisador LLM (triagem) | Pendente |
| 5 | Analisador LLM (metodologia + resultados) | Pendente |
| 6 | Exportadores (Excel/CSV) | Pendente |
| 7 | Orquestrador (main.py) | Pendente |
| 8 | Migração dos questionários e dados | Pendente |
| 9 | Redação do artigo LaTeX | Pendente |

## Requisitos

- Python 3.12+
- Google Gemini API key (variável de ambiente `GEMINI_API_KEY`)
- Dependências: ver `scripts/requirements.txt`

## Origem

Reimplementação limpa do sistema `survey_extraction_system` do projeto de tese (CAEN/UFC), usando como referência de organização o projeto `slr-disasters-birth-outcomes`.
