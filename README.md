# pndr_survey

Revisao sistematica da literatura empirica sobre os instrumentos da Politica Nacional de Desenvolvimento Regional (PNDR), cobrindo estudos publicados entre 2000 e 2025.

## Objetivo

Identificar, classificar e sintetizar as evidencias empiricas sobre o impacto de tres grupos de instrumentos da PNDR:

- **Fundos Constitucionais** (FNE, FNO, FCO)
- **Fundos de Desenvolvimento** (FDNE, FDA, FDCO)
- **Incentivos Fiscais** (SUDENE, SUDAM)

## Estrutura do Projeto

```
pndr_survey/
├── scripts/                  # Pipeline Python
│   ├── main.py               # CLI (search, screen, analyze, export, full)
│   ├── config.yaml           # Configuracao (nao versionado)
│   ├── config.example.yaml   # Template
│   ├── requirements.txt
│   ├── keywords/             # Queries de busca por base (.txt)
│   ├── questionnaires/       # Questionarios LLM (JSON, 3 stages)
│   └── src/
│       ├── models.py         # BibRecord + PaperRecord
│       ├── config.py         # Carregamento YAML
│       ├── importer.py       # Importacao de RIS/CSV/Excel
│       ├── dedup/            # Deduplicacao (DOI + fuzzy title)
│       ├── extractors/       # Extracao de texto de PDFs
│       ├── analyzers/        # Analise via Gemini (3 stages)
│       ├── screening/        # Triagem pre-LLM (PRISMA)
│       ├── exporters/        # Excel, CSV, RIS, JSON
│       └── utils/            # Logging
├── data/                     # Dados (nao versionados)
│   ├── all_records.ris       # Todos os 125 registros unicos (Zotero/Mendeley)
│   ├── all_records.xlsx      # Todos os 132 registros com URLs de download
│   ├── econpapers/           # 24 registros RIS (originais)
│   ├── capes/                # 30 registros RIS (originais)
│   ├── scopus/               # 16 registros RIS (originais)
│   ├── anpec/                # 62 registros Excel (originais)
│   ├── papers/               # PDFs dos artigos
│   └── processed/            # Saidas do pipeline (JSON, CSV)
├── latex/                    # Artigo LaTeX (esqueleto)
├── figures/                  # Figuras para o artigo
└── docs/
    └── pipeline_extraction.md  # Metodologia e log de extracao
```

## Pipeline

```
FASE 1 — COLETA                           FASE 2 — ANALISE
========================                   ========================

Busca manual nas 4 bases                   PDFs coletados
        |                                          |
        v                                          v
[1] Importacao (RIS/CSV/Excel)             [4] Extracao de texto (pdfplumber)
        |                                          |
        v                                          v
[2] Deduplicacao (DOI + fuzzy)             [5] Analise LLM (Gemini)
        |                                      Stage 1: Triagem
        v                                      Stage 2: Metodologia
[3] Triagem pre-LLM (PRISMA)                  Stage 3: Resultados
                                                       |
                                                       v
                                               [6] Exportacao (Excel/CSV/RIS/JSON)
```

## Status Atual

| Etapa | Descricao | Status |
|-------|-----------|--------|
| 1 | Busca manual + importacao (4 bases, 132 registros) | Concluido |
| 2 | Deduplicacao (125 unicos, 7 removidos) | Concluido |
| 3 | Triagem pre-LLM | Concluido |
| 4 | Coleta de PDFs (81 de 125) | Parcial — CAPES/Scopus pendentes |
| 5 | Analise LLM (Stages 1-3) | Pendente |
| 6 | Exportacao de resultados | Pendente |

Detalhes da extracao: [docs/pipeline_extraction.md](docs/pipeline_extraction.md)

## Quick Start

```bash
# Setup
python -m venv .venv && .venv\Scripts\activate
pip install -r scripts/requirements.txt
cp scripts/config.example.yaml scripts/config.yaml

# Ver queries de busca
cd scripts && python main.py search --dry-run

# Importar registros das 4 bases
python main.py --verbose search \
  --import-econpapers "../data/econpapers/econpapers_combined.ris" \
  --import-capes "../data/capes/Periodicos-CAPES-RIS.ris" \
  --import-scopus "../data/scopus/scopus_export_Feb 25-2026_bd09397c-fbc7-4454-8d88-0d42afc92ae6.ris" \
  --import-anpec "../data/anpec/resultados_anpec_pesquisa_250226_1030.xlsx"

# Triagem
python main.py screen --input-json ../data/processed/bib_records.json

# Analise LLM (requer GEMINI_API_KEY)
set GEMINI_API_KEY=sua-chave-aqui
python main.py analyze --stage 1 --max-papers 5    # teste
python main.py analyze                              # completo

# Exportar resultados
python main.py export --input-json ../data/processed/results.json
```

## Referencia de Comandos

| Comando | Descricao | Flags principais |
|---------|-----------|------------------|
| `search` | Importar registros de arquivos exportados | `--import-{base} FILE`, `--skip-dedup`, `--dry-run` |
| `screen` | Triagem pre-LLM (tipo, idioma, PDF) | `--input-json FILE`, `--title-filter`, `--report` |
| `analyze` | Analise LLM dos PDFs | `--stage {1,2,3,all}`, `--max-papers N`, `--input-dir DIR` |
| `export` | Exportar resultados | `--formats {excel,csv,ris,json}`, `--input-json FILE` |
| `full` | Pipeline completo | (combina todos acima) |

Opcoes globais: `--config FILE`, `--verbose`, `--output-dir DIR`

## Documentacao

| Arquivo | Conteudo |
|---------|----------|
| [docs/pipeline_extraction.md](docs/pipeline_extraction.md) | Metodologia, queries, dados coletados, trabalho pendente |
| [CLAUDE.md](CLAUDE.md) | Regras de codigo e convencoes do projeto |
| [docs/archive/PLAN.md](docs/archive/PLAN.md) | Plano de construcao original (historico) |
