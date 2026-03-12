# pndr_survey

Revisão sistemática da literatura empírica sobre os instrumentos da Política Nacional de Desenvolvimento Regional (PNDR), cobrindo estudos publicados entre 2000 e 2025.

**Artigo (versão mais recente):** [latex/0-main.pdf](https://github.com/hermelino/pndr_survey/blob/main/latex/0-main.pdf) — atualizado em 10/03/2026

## Objetivo

Identificar, classificar e sintetizar as evidências empíricas sobre o impacto de três grupos de instrumentos da PNDR:

- **Fundos Constitucionais** (FNE, FNO, FCO)
- **Fundos de Desenvolvimento** (FDNE, FDA, FDCO)
- **Incentivos Fiscais** (SUDENE, SUDAM)

## Estrutura do Projeto

```
pndr_survey/
├── scripts/                       # Pipeline Python
│   ├── main.py                    # CLI (search, screen, analyze, export, full)
│   ├── run_llm_all_papers.py      # Execução da análise LLM em lote
│   ├── test_llm_single.py         # Teste de análise LLM em PDF individual
│   ├── merge_papers_to_json.py    # Mescla registros + classificação LLM → JSON
│   ├── match_refs_to_studies.py   # Matching de citações entre estudos da triagem
│   ├── citation_index.py         # Índice de citação (IC) para revisão sistemática
│   ├── config.yaml                # Configuração (não versionado)
│   ├── config.example.yaml        # Template
│   ├── requirements.txt
│   ├── keywords/                  # Queries de busca por base (.txt)
│   ├── questionnaires/            # Questionários LLM (JSON, 3 stages)
│   └── src/
│       ├── models.py              # BibRecord + PaperRecord
│       ├── config.py              # Carregamento YAML
│       ├── importer.py            # Importação de RIS/CSV/Excel
│       ├── dedup/                 # Deduplicação (DOI + fuzzy title)
│       ├── extractors/            # Extração de texto de PDFs
│       ├── analyzers/             # Análise via Gemini (3 stages)
│       ├── screening/             # Triagem pré-LLM (PRISMA)
│       ├── exporters/             # Excel, CSV, RIS, JSON
│       └── utils/                 # Logging
├── data/
│   ├── 1-records/                 # Registros bibliográficos
│   │   ├── all_records.ris        # 128 registros únicos (Zotero/Mendeley)
│   │   ├── all_records.xlsx       # Resumo de registros por base
│   │   ├── 1-1-records-scopus/    # 16 registros RIS + Excel
│   │   ├── 1-2-records-scielo/    # 5 registros RIS + Excel
│   │   ├── 1-3-records-capes/     # 30 registros RIS + Excel
│   │   ├── 1-4-records-econpapers/# 24 registros RIS + Excel
│   │   ├── 1-5-records-anpec/     # 62 registros Excel
│   │   └── processed/             # Saídas do pipeline (JSON, CSV)
│   │       ├── bib_records.json   # 137 registros normalizados (BibRecord)
│   │       ├── bib_screened.json  # Registros após triagem pré-LLM
│   │       └── duplicates_removed.csv
│   ├── 2-papers/                  # Artigos e classificação
│   │   ├── 2-2-papers.json        # JSON enriquecido (registros + LLM + triagem)
│   │   ├── 2-2-papers-pdfs/       # 130 PDFs renomeados (118 bases + 12 manual)
│   │   ├── 2-1-papers_scripts/    # Scripts de renomeação e verificação
│   │   ├── all_papers.xlsx        # Controle: registros + status de download
│   │   ├── all_papers_llm_classif.xlsx        # Classificação LLM bruta
│   │   ├── all_papers_llm_classif_final.xlsx  # Classificação LLM revisada (somente leitura)
│   │   ├── resumo_classificacao.xlsx          # Resumo estatístico (gerado por _rebuild_resumo.py)
│   │   ├── _llm_checkpoint.json   # Checkpoint da análise LLM (stages 1-3)
│   │   └── build_verified_xlsx.py # Gera xlsx verificado a partir do checkpoint
│   └── 3-ref-bib/                   # Referências bibliográficas dos estudos
│       ├── extrair_referencias.py     # Extração de refs dos PDFs via Gemini
│       ├── estruturar_referencias.py  # Estruturação de refs em JSON
│       ├── referencias_consolidadas.txt
│       ├── referencias_estruturadas.json
│       ├── refs_por_estudo/           # 44 JSONs ativos + TXTs com refs por estudo
│       ├── citation_index_results.json # Índice de citação por estudo (JSON)
│       └── citation_index_report.txt   # Relatório do índice de citação
├── latex/                         # Artigo LaTeX (esqueleto)
├── figures/                       # Figuras para o artigo
└── docs/
    ├── pipeline_extraction.md     # Metodologia e log de extração
    └── archive/PLAN.md            # Plano de construção original (histórico)
```

## Pipeline

```
FASE 1 — COLETA                           FASE 2 — ANÁLISE
========================                   ========================

Busca manual nas 5 bases                   PDFs coletados (130)
        |                                          |
        v                                          v
[1] Importação (RIS/CSV/Excel)             [4] Extração de texto (pdfplumber)
        |                                          |
        v                                          v
[2] Deduplicação (DOI + fuzzy)             [5] Análise LLM (Gemini)
        |                                      Stage 1: Triagem
        v                                      Stage 2: Metodologia
[3] Triagem pré-LLM (PRISMA)                  Stage 3: Resultados
                                                       |
                                                       v
                                               [6] Triagem final (44 aprov., 86 rej.)
                                                       |
                                                       v
                                               [7] Consolidação JSON enriquecido
                                                       |
                                                       v
                                               [8] Extração e matching de citações
                                                      |
                                                      v
                                               [9] Índice de citação (IC)
```

## Status Atual

| Etapa | Descrição | Status |
|-------|-----------|--------|
| 1 | Busca manual + importação (5 bases) | Concluído |
| 2 | Deduplicação (118 únicos das bases, 28 removidos incl. 9 TD/WP manuais) + 12 inclusões manuais = 130 | Concluído |
| 3 | Triagem pré-LLM | Concluído |
| 4 | Coleta de PDFs (130 de 130, 100%) | Concluído |
| 5 | Análise LLM (Stages 1-3, 130 papers) | Concluído |
| 6 | Triagem final (44 aprovados, 86 rejeitados, 130 total) | Concluído |
| 7 | Consolidação JSON (registros + LLM) | Concluído |
| 8 | Extração de referências (44 estudos ativos) | Concluído |
| 9 | Matching de citações entre estudos (142 citações cruzadas) | Concluído |
| 10 | Índice de citação (142 citações cruzadas; 44 estudos: 22 pub, 22 não-pub) | Concluído |
| 11 | Artigo LaTeX | Em andamento |

Detalhes da extração: [docs/pipeline_extraction.md](docs/pipeline_extraction.md)

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

# Análise LLM (requer GEMINI_API_KEY)
set GEMINI_API_KEY=sua-chave-aqui
python run_llm_all_papers.py

# Consolidar registros + LLM em JSON enriquecido
python merge_papers_to_json.py

# Matching de citações entre estudos
python match_refs_to_studies.py

# Índice de citação
python citation_index.py
```

## Referência de Comandos

| Comando / Script | Descrição | Flags principais |
|------------------|-----------|------------------|
| `main.py search` | Importar registros de arquivos exportados | `--import-{base} FILE`, `--skip-dedup`, `--dry-run` |
| `main.py screen` | Triagem pré-LLM (tipo, idioma, PDF) | `--input-json FILE`, `--title-filter`, `--report` |
| `main.py analyze` | Análise LLM dos PDFs | `--stage {1,2,3,all}`, `--max-papers N` |
| `main.py export` | Exportar resultados | `--formats {excel,csv,ris,json}`, `--input-json FILE` |
| `run_llm_all_papers.py` | Análise LLM em lote (todos os PDFs) | — |
| `merge_papers_to_json.py` | Mescla registros + LLM → JSON enriquecido | — |
| `match_refs_to_studies.py` | Matching de citações entre estudos da triagem | — |
| `citation_index.py` | Índice de citação (IC) para artigos não-publicados | — |
| `generate_approved_ris.py` | Filtra RIS para estudos aprovados | — |
| `generate_bibtex.py` | Converte RIS aprovado → BibTeX (references.bib) | — |
| `generate_ic_table.py` | Gera tabela IC LaTeX com \citeonline (tabela_ic.tex) | — |
| `generate_latex_tables.py` | Regenera tabelas derivadas do artigo (estudos-ano, instrumentos, autores, unidade-amostral, métodos) | — |
| `generate_figures.py` | Gera figuras para o artigo LaTeX (mapas, gráficos) | `--list`, `--validate`, `--force`, `--verbose` |

Opções globais do `main.py`: `--config FILE`, `--verbose`, `--output-dir DIR`

## Geração de Figuras

O projeto inclui scripts R para gerar figuras da seção de Política Regional do artigo LaTeX, orquestrados via wrapper Python.

### Figuras Geradas

| Figura | Script R | Descrição |
|--------|----------|-----------|
| `distribuicao_pib_relativo_municipal.png` | `mapa_distribuicao_pib_municipal.R` | Mapas de distribuição do PIB per capita relativo (2002, 2010, 2019, 2021) |
| `tipologia_II_simples_com_legenda.png` | `mapa_tipologia_simples.R` | Mapa de tipologia regional 2018 (9 categorias: renda × dinamismo) |
| `icf_superint_setor.png` | `grafico_resumo_icf.R` | Gráfico de incentivos fiscais por superintendência e setor |

**Figura externa (não gerada):** `tipologia_I.JPG` (fonte: Decreto nº 6.047/2007)

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

### Dependências

- **R** (auto-detecção ou configurado em `config.yaml`)
  - Instalação: https://cran.r-project.org/bin/windows/base/
  - Pacotes: `ggplot2`, `sf`, `tidyverse`, `RColorBrewer`, `readxl`
- **Dados RDS** do projeto `tese` (configurado em `config.yaml`)
- **Shapefiles** IBGE (configurado em `config.yaml`)

### Configuração

Edite `scripts/config.yaml`, seção `figures:`:

```yaml
figures:
  external_data_dir: "C:/OneDrive/github/tese/bulding_dataset_R/output/data"
  external_shapefiles_dir: "C:/OneDrive/DATABASES"
  r_executable: ""  # Vazio = auto-detect
```

Documentação completa: [data/r_scripts/README.md](data/r_scripts/README.md)

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

## Documentação

| Arquivo | Conteúdo |
|---------|----------|
| [REPRODUCING.md](REPRODUCING.md) | **Guia completo de reprodutibilidade** (Nível 1, 2, 3) |
| [data/DATASETS.md](data/DATASETS.md) | Como obter dados externos (PDFs, RDS, shapefiles) |
| [docs/pipeline_extraction.md](docs/pipeline_extraction.md) | Metodologia, queries, dados coletados, análise LLM, citações |
| [CLAUDE.md](CLAUDE.md) | Regras de código e convenções do projeto |
| [docs/update_reports/](docs/update_reports/) | Relatórios de atualizações do pipeline (propagate-update) |
| [docs/processar-dados-guide.md](docs/processar-dados-guide.md) | **Guia da skill processar-dados** (conversão R → Python) |
| [docs/archive/PLAN.md](docs/archive/PLAN.md) | Plano de construção original (histórico) |
