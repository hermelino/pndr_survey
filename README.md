# pndr_survey

Revisão sistemática da literatura empírica sobre os instrumentos da Política Nacional de Desenvolvimento Regional (PNDR), cobrindo estudos publicados entre 2000 e 2025.

## Objetivo

Identificar, classificar e sintetizar as evidências empíricas sobre o impacto dos três grupos de instrumentos da PNDR:

- **Fundos Constitucionais** (FNE, FNO, FCO)
- **Fundos de Desenvolvimento** (FDNE, FDA, FDCO)
- **Incentivos Fiscais** (SUDENE, SUDAM)

O projeto combina busca em bases acadêmicas (automática e semi-automática) com análise via LLM (Gemini) para extrair informações estruturadas de cada artigo.

## Estrutura do Projeto

```
pndr_survey/
├── latex/                  # Artigo LaTeX
│   └── main.tex
├── scripts/                # Pipeline completo
│   ├── main.py             # Ponto de entrada CLI
│   ├── config.yaml         # Configuração (não versionado)
│   ├── config.example.yaml # Template de configuração
│   ├── requirements.txt
│   ├── keywords/           # Estratégias de busca por base
│   ├── questionnaires/     # Questionários JSON para análise LLM
│   └── src/
│       ├── models.py       # BibRecord + PaperRecord
│       ├── config.py       # Carregamento de configuração
│       ├── searchers/      # Busca em bases acadêmicas
│       ├── dedup/          # Deduplicação (DOI + fuzzy title)
│       ├── extractors/     # Extração de texto de PDFs
│       ├── analyzers/      # Análise via LLM
│       ├── exporters/      # Excel, CSV, RIS, JSON
│       └── utils/          # Logging
├── data/                   # Dados (não versionados)
│   ├── papers/             # PDFs dos artigos
│   └── processed/          # Resultados da análise
├── figures/                # Figuras para o artigo
└── docs/
    └── PLAN.md             # Plano de construção detalhado
```

## Pipeline

```
FASE 1 — BUSCA E COLETA
========================

Bases acadêmicas (EconPapers, Google Scholar, CAPES, Scopus)
    │
    ▼
[0] Busca automática (EconPapers) + semi-automática (demais bases)
    │
    ▼
[1] Importação e normalização → BibRecord
    │
    ▼
[2] Deduplicação (DOI exato + fuzzy title)
    │
    ▼
[3] Download de PDFs disponíveis


FASE 2 — ANÁLISE E SÍNTESE
===========================

PDFs coletados
    │
    ▼
[4] Extração de texto (pdfplumber)
    │
    ▼
[5] Análise via LLM (Gemini)
    │   Stage 1: Triagem — é estudo empírico sobre PNDR?
    │   Stage 2: Metodologia — métodos, variáveis, período, região
    │   Stage 3: Resultados — instrumentos avaliados, efeitos, significância
    │
    ▼
[6] Exportação (Excel/CSV/RIS/JSON)
    │
    ▼
[7] Síntese para o artigo LaTeX
```

## Etapas do Projeto

| # | Etapa | Status |
|---|-------|--------|
| -- | Esqueleto do projeto e documentação | Concluído |
| 0A | BibRecord + modelo bibliográfico | Pendente |
| 0B | Searchers (EconPapers + manuais) | Pendente |
| 0C | Deduplicação (DOI + fuzzy title) | Pendente |
| 0D | Download de PDFs | Pendente |
| 1 | Configuração e PaperRecord | Pendente |
| 2 | Extrator de texto de PDFs | Pendente |
| 3 | Analisador LLM (triagem) | Pendente |
| 4 | Analisador LLM (metodologia + resultados) | Pendente |
| 5 | Exportadores (Excel/CSV/RIS/JSON) | Pendente |
| 6 | Orquestrador (main.py) | Pendente |
| 7 | Migração questionários + keywords + dados | Pendente |
| 8 | Citation analysis | Futuro |
| 9 | Artigo LaTeX | Futuro |

## Requisitos

- Python 3.12+
- Google Gemini API key (variável de ambiente `GEMINI_API_KEY`)
- Dependências: ver `scripts/requirements.txt`

## Origem

Reimplementação limpa do sistema `survey_extraction_system` do projeto de tese (CAEN/UFC), usando como referência de arquitetura o projeto `slr-disasters-birth-outcomes`.
