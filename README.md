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
├── scripts/                       # Pipeline Python
│   ├── main.py                    # CLI (search, screen, analyze, export, full)
│   ├── run_llm_all_papers.py      # Execucao da analise LLM em lote
│   ├── test_llm_single.py         # Teste de analise LLM em PDF individual
│   ├── merge_papers_to_json.py    # Mescla registros + classificacao LLM → JSON
│   ├── match_refs_to_studies.py   # Matching de citacoes entre estudos da triagem
│   ├── citation_index.py         # Indice de citacao (IC) para revisao sistematica
│   ├── config.yaml                # Configuracao (nao versionado)
│   ├── config.example.yaml        # Template
│   ├── requirements.txt
│   ├── keywords/                  # Queries de busca por base (.txt)
│   ├── questionnaires/            # Questionarios LLM (JSON, 3 stages)
│   └── src/
│       ├── models.py              # BibRecord + PaperRecord
│       ├── config.py              # Carregamento YAML
│       ├── importer.py            # Importacao de RIS/CSV/Excel
│       ├── dedup/                 # Deduplicacao (DOI + fuzzy title)
│       ├── extractors/            # Extracao de texto de PDFs
│       ├── analyzers/             # Analise via Gemini (3 stages)
│       ├── screening/             # Triagem pre-LLM (PRISMA)
│       ├── exporters/             # Excel, CSV, RIS, JSON
│       └── utils/                 # Logging
├── data/
│   ├── 1-records/                 # Registros bibliograficos
│   │   ├── all_records.ris        # 128 registros unicos (Zotero/Mendeley)
│   │   ├── all_records.xlsx       # Resumo de registros por base
│   │   ├── 1-1-records-scopus/    # 16 registros RIS + Excel
│   │   ├── 1-2-records-scielo/    # 5 registros RIS + Excel
│   │   ├── 1-3-records-capes/     # 30 registros RIS + Excel
│   │   ├── 1-4-records-econpapers/# 24 registros RIS + Excel
│   │   ├── 1-5-records-anpec/     # 62 registros Excel
│   │   └── processed/             # Saidas do pipeline (JSON, CSV)
│   │       ├── bib_records.json   # 137 registros normalizados (BibRecord)
│   │       ├── bib_screened.json  # Registros apos triagem pre-LLM
│   │       └── duplicates_removed.csv
│   ├── 2-papers/                  # Artigos e classificacao
│   │   ├── 2-2-papers.json        # JSON enriquecido (registros + LLM + triagem)
│   │   ├── 2-2-papers-pdfs/       # 118 PDFs renomeados
│   │   ├── 2-1-papers_scripts/    # Scripts de renomeacao e verificacao
│   │   ├── all_papers.xlsx        # Controle: registros + status de download
│   │   ├── all_papers_llm_classif.xlsx        # Classificacao LLM bruta
│   │   ├── all_papers_llm_classif_final.xlsx  # Classificacao LLM revisada
│   │   ├── _llm_checkpoint.json   # Checkpoint da analise LLM (stages 1-3)
│   │   └── build_verified_xlsx.py # Gera xlsx verificado a partir do checkpoint
│   └── 3-ref-bib/                   # Referencias bibliograficas dos estudos
│       ├── extrair_referencias.py     # Extracao de refs dos PDFs via Gemini
│       ├── estruturar_referencias.py  # Estruturacao de refs em JSON
│       ├── referencias_consolidadas.txt
│       ├── referencias_estruturadas.json
│       ├── refs_por_estudo/           # 54 JSONs + TXTs com refs por estudo
│       ├── citation_index_results.json # Indice de citacao por estudo (JSON)
│       └── citation_index_report.txt   # Relatorio do indice de citacao
├── latex/                         # Artigo LaTeX (esqueleto)
├── figures/                       # Figuras para o artigo
└── docs/
    ├── pipeline_extraction.md     # Metodologia e log de extracao
    └── archive/PLAN.md            # Plano de construcao original (historico)
```

## Pipeline

```
FASE 1 — COLETA                           FASE 2 — ANALISE
========================                   ========================

Busca manual nas 5 bases                   PDFs coletados (118)
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
                                               [6] Triagem final (53 aprovados)
                                                       |
                                                       v
                                               [7] Consolidacao JSON enriquecido
                                                       |
                                                       v
                                               [8] Extracao e matching de citacoes
                                                      |
                                                      v
                                               [9] Indice de citacao (IC)
```

## Status Atual

| Etapa | Descricao | Status |
|-------|-----------|--------|
| 1 | Busca manual + importacao (5 bases) | Concluido |
| 2 | Deduplicacao (118 unicos, 27 removidos incl. 8 TD/WP manuais) | Concluido |
| 3 | Triagem pre-LLM | Concluido |
| 4 | Coleta de PDFs (118 de 118, 100%) | Concluido |
| 5 | Analise LLM (Stages 1-3, 118 papers) | Concluido |
| 6 | Triagem final (46 aprovados, 72 rejeitados) | Concluido |
| 7 | Consolidacao JSON (registros + LLM) | Concluido |
| 8 | Extracao de referencias (48 estudos ativos) | Concluido |
| 9 | Matching de citacoes entre estudos (74 citacoes cruzadas) | Concluido |
| 10 | Indice de citacao (9 nao-publicados com IC > 0) | Concluido |
| 11 | Artigo LaTeX | Em andamento |

Detalhes da extracao: [docs/pipeline_extraction.md](docs/pipeline_extraction.md)

## Quick Start

```bash
# Setup
python -m venv .venv && .venv\Scripts\activate
pip install -r scripts/requirements.txt
cp scripts/config.example.yaml scripts/config.yaml

# Ver queries de busca
cd scripts && python main.py search --dry-run

# Importar registros das 5 bases
python main.py --verbose search \
  --import-scopus "../data/1-records/1-1-records-scopus/scopus_20260225.ris" \
  --import-scielo "../data/1-records/1-2-records-scielo/scielo_20260226.ris" \
  --import-capes "../data/1-records/1-3-records-capes/capes_20260224.ris" \
  --import-econpapers "../data/1-records/1-4-records-econpapers/econpapers_20260224.ris" \
  --import-anpec "../data/1-records/1-5-records-anpec/anpec_20260225.xlsx"

# Triagem
python main.py screen --input-json ../data/1-records/processed/bib_records.json

# Analise LLM (requer GEMINI_API_KEY)
set GEMINI_API_KEY=sua-chave-aqui
python run_llm_all_papers.py

# Consolidar registros + LLM em JSON enriquecido
python merge_papers_to_json.py

# Matching de citacoes entre estudos
python match_refs_to_studies.py

# Indice de citacao
python citation_index.py
```

## Referencia de Comandos

| Comando / Script | Descricao | Flags principais |
|------------------|-----------|------------------|
| `main.py search` | Importar registros de arquivos exportados | `--import-{base} FILE`, `--skip-dedup`, `--dry-run` |
| `main.py screen` | Triagem pre-LLM (tipo, idioma, PDF) | `--input-json FILE`, `--title-filter`, `--report` |
| `main.py analyze` | Analise LLM dos PDFs | `--stage {1,2,3,all}`, `--max-papers N` |
| `main.py export` | Exportar resultados | `--formats {excel,csv,ris,json}`, `--input-json FILE` |
| `run_llm_all_papers.py` | Analise LLM em lote (todos os PDFs) | — |
| `merge_papers_to_json.py` | Mescla registros + LLM → JSON enriquecido | — |
| `match_refs_to_studies.py` | Matching de citacoes entre estudos da triagem | — |
| `citation_index.py` | Indice de citacao (IC) para artigos nao-publicados | — |

Opcoes globais do `main.py`: `--config FILE`, `--verbose`, `--output-dir DIR`

## Documentacao

| Arquivo | Conteudo |
|---------|----------|
| [docs/pipeline_extraction.md](docs/pipeline_extraction.md) | Metodologia, queries, dados coletados, analise LLM, citacoes |
| [CLAUDE.md](CLAUDE.md) | Regras de codigo e convencoes do projeto |
| [docs/archive/PLAN.md](docs/archive/PLAN.md) | Plano de construcao original (historico) |
