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
│   │   ├── 2-2-papers-pdfs/       # 130 PDFs renomeados (118 bases + 12 manual)
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
│       ├── refs_por_estudo/           # 44 JSONs ativos + TXTs com refs por estudo
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

Busca manual nas 5 bases                   PDFs coletados (130)
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
                                               [6] Triagem final (44 aprov., 86 rej.)
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
| 2 | Deduplicacao (118 unicos das bases, 28 removidos incl. 9 TD/WP manuais) + 12 inclusoes manuais = 130 | Concluido |
| 3 | Triagem pre-LLM | Concluido |
| 4 | Coleta de PDFs (130 de 130, 100%) | Concluido |
| 5 | Analise LLM (Stages 1-3, 130 papers) | Concluido |
| 6 | Triagem final (44 aprovados, 86 rejeitados, 130 total) | Concluido |
| 7 | Consolidacao JSON (registros + LLM) | Concluido |
| 8 | Extracao de referencias (44 estudos ativos) | Concluido |
| 9 | Matching de citacoes entre estudos (142 citacoes cruzadas) | Concluido |
| 10 | Indice de citacao (142 citacoes cruzadas; 44 estudos: 22 pub, 22 nao-pub) | Concluido |
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
| `generate_approved_ris.py` | Filtra RIS para estudos aprovados | — |
| `generate_bibtex.py` | Converte RIS aprovado → BibTeX (references.bib) | — |
| `generate_ic_table.py` | Gera tabela IC LaTeX com \citeonline (tabela_ic.tex) | — |
| `generate_latex_tables.py` | Regenera tabelas derivadas do artigo (estudos-ano, instrumentos, autores, unidade-amostral, metodos) | — |
| `generate_figures.py` | Gera figuras para o artigo LaTeX (mapas, graficos) | `--list`, `--validate`, `--force`, `--verbose` |

Opcoes globais do `main.py`: `--config FILE`, `--verbose`, `--output-dir DIR`

## Geracao de Figuras

O projeto inclui scripts R para gerar figuras da secao de Politica Regional do artigo LaTeX, orquestrados via wrapper Python.

### Figuras Geradas

| Figura | Script R | Descricao |
|--------|----------|-----------|
| `distribuicao_pib_relativo_municipal.png` | `mapa_distribuicao_pib_municipal.R` | Mapas de distribuicao do PIB per capita relativo (2002, 2010, 2019, 2021) |
| `tipologia_II_simples_com_legenda.png` | `mapa_tipologia_simples.R` | Mapa de tipologia regional 2018 (9 categorias: renda × dinamismo) |
| `icf_superint_setor.png` | `grafico_resumo_icf.R` | Grafico de incentivos fiscais por superintendencia e setor |

**Figura externa (nao gerada):** `tipologia_I.JPG` (fonte: Decreto nº 6.047/2007)

### Comandos

```bash
cd scripts

# Listar figuras e status (existencia, tamanho, ultima modificacao)
python generate_figures.py --list

# Validar dependencias (R, dados RDS, shapefiles)
python generate_figures.py --validate

# Gerar figuras (incremental, apenas se desatualizadas)
python generate_figures.py

# Forcar regeneracao de todas as figuras
python generate_figures.py --force

# Logging DEBUG
python generate_figures.py --verbose
```

### Dependencias

- **R** (auto-deteccao ou configurado em `config.yaml`)
  - Instalacao: https://cran.r-project.org/bin/windows/base/
  - Pacotes: `ggplot2`, `sf`, `tidyverse`, `RColorBrewer`, `readxl`
- **Dados RDS** do projeto `tese` (configurado em `config.yaml`)
- **Shapefiles** IBGE (configurado em `config.yaml`)

### Configuracao

Edite `scripts/config.yaml`, secao `figures:`:

```yaml
figures:
  external_data_dir: "C:/OneDrive/github/tese/bulding_dataset_R/output/data"
  external_shapefiles_dir: "C:/OneDrive/DATABASES"
  r_executable: ""  # Vazio = auto-detect
```

Documentacao completa: [data/r_scripts/README.md](data/r_scripts/README.md)

## Reprodutibilidade

Este projeto é **completamente reproduzível**. Qualquer pessoa pode clonar o repositório e regenerar todos os outputs (tabelas, figuras, artigo PDF) a partir dos dados originais.

### 🚀 Quick Start

```bash
# 1. Clonar repositório
git clone https://github.com/<USER>/pndr_survey.git
cd pndr_survey

# 2. Configurar ambiente
python -m venv .venv && .venv\Scripts\activate
pip install -r scripts/requirements.txt

# 3. Configurar pipeline
cp scripts/config.example.yaml scripts/config.yaml
# Edite config.yaml com suas configurações (API key, paths de dados externos)

# 4. Pipeline completo
make all          # GNU Make (Git Bash/WSL)
# ou
build.bat all     # Windows nativo
```

### 📊 Níveis de Reprodutibilidade

| Nível | Descrição | Tempo | Requer |
|-------|-----------|-------|--------|
| **Nível 1: Completo** | Refazer toda análise do zero | ~3-5h | Python, R, PDFs, API key, dados externos |
| **Nível 2: Parcial** | Regenerar outputs a partir de dados processados | ~10min | Python, R, dados externos |
| **Nível 3: Compilação** | Apenas compilar LaTeX → PDF | ~1min | LaTeX |

**Documentação completa:** [REPRODUCING.md](REPRODUCING.md)

### 📁 Estrutura de Arquivos

**Versionados (no Git):**
- Inputs originais: RIS/Excel das 5 bases acadêmicas
- Scripts Python/R de processamento e geração
- Código LaTeX do artigo
- Documentação e configurações

**Não versionados (gerados pelo pipeline):**
- PDFs dos estudos (119 arquivos, ~119 MB) — [como obter](data/DATASETS.md)
- Dados intermediários (JSONs processados, checkpoints LLM)
- Outputs finais (tabelas LaTeX, figuras PNG, references.bib)

**Comandos disponíveis:**
```bash
make setup       # Instalar dependências
make import      # Importar registros das 5 bases
make screen      # Triagem pré-LLM
make analyze     # Análise LLM (requer GEMINI_API_KEY e PDFs)
make citations   # Matching de citações + índice
make tables      # Gerar tabelas LaTeX
make figures     # Gerar figuras (mapas, gráficos)
make latex       # Compilar PDF do artigo
make all         # Pipeline completo
make clean       # Limpar outputs gerados
```

Equivalente Windows: `build.bat <comando>`

### 🔗 Recursos

- **Guia de reprodutibilidade:** [REPRODUCING.md](REPRODUCING.md)
- **Dados externos:** [data/DATASETS.md](data/DATASETS.md)
- **Build scripts:** [Makefile](Makefile), [build.bat](build.bat)

---

## Documentacao

| Arquivo | Conteudo |
|---------|----------|
| [REPRODUCING.md](REPRODUCING.md) | **Guia completo de reprodutibilidade** (Nivel 1, 2, 3) |
| [data/DATASETS.md](data/DATASETS.md) | Como obter dados externos (PDFs, RDS, shapefiles) |
| [docs/pipeline_extraction.md](docs/pipeline_extraction.md) | Metodologia, queries, dados coletados, analise LLM, citacoes |
| [CLAUDE.md](CLAUDE.md) | Regras de codigo e convencoes do projeto |
| [docs/update_reports/](docs/update_reports/) | Relatorios de atualizacoes do pipeline (propagate-update) |
| [docs/processar-dados-guide.md](docs/processar-dados-guide.md) | **Guia da skill processar-dados** (conversao R → Python) |
| [docs/archive/PLAN.md](docs/archive/PLAN.md) | Plano de construcao original (historico) |
