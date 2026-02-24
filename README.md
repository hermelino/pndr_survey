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
├── scripts/                # Pipeline completo
│   ├── main.py             # Ponto de entrada CLI
│   ├── config.yaml         # Configuração (não versionado)
│   ├── config.example.yaml # Template de configuração
│   ├── requirements.txt
│   ├── keywords/           # Estratégias de busca por base (.txt)
│   │   ├── econpapers.txt
│   │   ├── google_scholar.txt
│   │   ├── capes.txt
│   │   └── scopus.txt
│   ├── questionnaires/     # Questionários JSON para análise LLM
│   │   ├── stage_1_screening.json   # Triagem (9 perguntas)
│   │   ├── stage_2_methods.json     # Metodologia (9 perguntas)
│   │   └── stage_3_results.json     # Resultados (7 perguntas)
│   └── src/
│       ├── models.py       # BibRecord + PaperRecord (dataclasses)
│       ├── config.py       # Carregamento YAML + validação
│       ├── searchers/      # Busca em bases acadêmicas
│       │   ├── base.py             # BaseSearcher ABC
│       │   ├── econpapers.py       # Busca automática via HTTP
│       │   ├── google_scholar.py   # Semi-automático (import RIS/CSV)
│       │   ├── capes.py            # Semi-automático (import RIS/CSV)
│       │   └── scopus.py           # Semi-automático (import RIS/CSV)
│       ├── dedup/          # Deduplicação (DOI exato + fuzzy title)
│       │   └── deduplicator.py
│       ├── extractors/     # Extração de texto de PDFs
│       │   └── pdf_extractor.py    # pdfplumber + SHA-256
│       ├── analyzers/      # Análise via LLM
│       │   ├── base.py             # BaseAnalyzer ABC
│       │   └── gemini_analyzer.py  # API Gemini com retry + rate limit
│       ├── exporters/      # Exportação de resultados
│       │   ├── common.py           # Flatten records para tabular
│       │   ├── excel_exporter.py   # Excel com abas Resultados + Resumo
│       │   ├── csv_exporter.py     # CSV UTF-8-BOM (;)
│       │   ├── ris_exporter.py     # RIS para Zotero/Mendeley
│       │   └── json_exporter.py    # JSON completo
│       └── utils/
│           ├── logger.py           # Logging dual (console + arquivo)
│           └── downloader.py       # Download de PDFs com validação
├── latex/                  # Artigo LaTeX (esqueleto)
│   └── main.tex
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

## Status do Projeto

| # | Etapa | Status |
|---|-------|--------|
| 0A | BibRecord + modelo bibliográfico | Concluído |
| 0B | Searchers (EconPapers + manuais) | Concluído |
| 0C | Deduplicação (DOI + fuzzy title) | Concluído |
| 0D | Download de PDFs | Concluído |
| 1 | Configuração (YAML) e PaperRecord | Concluído |
| 2 | Extrator de texto de PDFs | Concluído |
| 3 | Analisador LLM (triagem — Stage 1) | Concluído |
| 4 | Analisador LLM (metodologia + resultados — Stages 2-3) | Concluído |
| 5 | Exportadores (Excel/CSV/RIS/JSON) | Concluído |
| 6 | Orquestrador CLI (main.py) | Concluído |
| 7 | Migração questionários + keywords | Concluído |
| 8 | Citation analysis | Futuro |
| 9 | Artigo LaTeX | Futuro |

## Instalação

### Pré-requisitos

- Python 3.12+
- Google Gemini API key

### Setup

```bash
# 1. Clonar o repositório
git clone <url> && cd pndr_survey

# 2. Criar e ativar ambiente virtual
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Linux/macOS

# 3. Instalar dependências
pip install -r scripts/requirements.txt

# 4. Configurar
cp scripts/config.example.yaml scripts/config.yaml
# Editar scripts/config.yaml se necessário (bases, modelo, caminhos)

# 5. Definir chave da API Gemini
set GEMINI_API_KEY=sua-chave-aqui          # Windows CMD
# $env:GEMINI_API_KEY="sua-chave-aqui"     # Windows PowerShell
# export GEMINI_API_KEY=sua-chave-aqui     # Linux/macOS
```

## Guia de Uso — Comandos por Etapa

Todos os comandos devem ser executados a partir do diretório `scripts/`:

```bash
cd scripts
```

### Ajuda geral

```bash
python main.py --help
python main.py search --help
python main.py analyze --help
python main.py export --help
```

---

### FASE 1 — Busca e Coleta

#### 1.1 Visualizar queries sem executar (dry-run)

```bash
python main.py search --dry-run
```

Mostra a query booleana de cada base configurada sem executar nenhuma busca. Útil para verificar as estratégias de busca antes de rodar.

#### 1.2 Buscar automaticamente no EconPapers

```bash
python main.py search --databases econpapers
```

Executa busca HTTP automatizada no EconPapers/RePEc, coleta metadados, deduplica e tenta baixar PDFs disponíveis.

#### 1.3 Buscar em bases semi-automáticas (Google Scholar, CAPES, Scopus)

Para bases sem API, o pipeline gera instruções de busca manual. O fluxo é:

1. Rodar `--dry-run` para obter a query formatada
2. Executar a busca manualmente na base (via navegador, Publish or Perish, etc.)
3. Exportar os resultados como arquivo RIS ou CSV
4. Importar os resultados no pipeline:

```bash
# Importar resultados do Google Scholar (Publish or Perish ou Zotero)
python main.py search --import-scholar caminho/para/scholar_results.ris

# Importar resultados do Portal CAPES
python main.py search --import-capes caminho/para/capes_results.ris

# Importar resultados do Scopus
python main.py search --import-scopus caminho/para/scopus_results.csv

# Importar de múltiplas bases de uma vez
python main.py search \
  --import-scholar scholar.ris \
  --import-capes capes.ris \
  --import-scopus scopus.csv
```

#### 1.4 Opções de controle da busca

```bash
# Pular deduplicação (manter todos os registros)
python main.py search --import-scholar results.ris --skip-dedup

# Pular download de PDFs (apenas coletar metadados)
python main.py search --databases econpapers --skip-download

# Combinar busca automática com importação manual
python main.py search --databases econpapers --import-scholar scholar.ris
```

---

### FASE 2 — Análise via LLM

> **Pré-requisito:** PDFs devem estar em `data/papers/` e a variável `GEMINI_API_KEY` deve estar definida.

#### 2.1 Executar pipeline completo de análise (Stages 1→2→3)

```bash
python main.py analyze
```

Extrai texto dos PDFs, executa triagem (Stage 1), filtra estudos empíricos, e aplica questionários de metodologia (Stage 2) e resultados (Stage 3).

#### 2.2 Executar apenas uma etapa específica

```bash
# Apenas triagem (Stage 1)
python main.py analyze --stage 1

# Apenas metodologia (Stage 2) — requer Stage 1 já executado
python main.py analyze --stage 2

# Apenas resultados (Stage 3) — requer Stages 1-2 já executados
python main.py analyze --stage 3
```

#### 2.3 Limitar número de papers (útil para testes)

```bash
python main.py analyze --max-papers 5
python main.py analyze --stage 1 --max-papers 3
```

#### 2.4 Usar diretório alternativo de PDFs

```bash
python main.py analyze --input-dir caminho/para/pdfs/
```

---

### FASE 3 — Exportação de Resultados

#### 3.1 Exportar nos formatos padrão (definidos em config.yaml)

```bash
python main.py export --input-json ../data/processed/YYYYMMDD_HHMMSS/results.json
```

#### 3.2 Escolher formatos específicos

```bash
# Apenas Excel e CSV
python main.py export --input-json results.json --formats excel csv

# Apenas RIS (para importar em Zotero/Mendeley)
python main.py export --input-json results.json --formats ris

# Todos os formatos
python main.py export --input-json results.json --formats excel csv ris json
```

#### 3.3 Definir diretório de saída

```bash
python main.py export --input-json results.json --output-dir ../data/processed/final
```

---

### Pipeline Completo (Full)

Executa todas as fases em sequência (busca → análise → exportação):

```bash
python main.py full
```

Equivale a rodar `search` + `analyze` + `export` sequencialmente. Ao final, imprime um resumo PRISMA-like com estatísticas do pipeline.

---

### Opções Globais

```bash
# Usar arquivo de configuração alternativo
python main.py --config meu_config.yaml search --dry-run

# Ativar logging detalhado (DEBUG)
python main.py --verbose analyze --stage 1 --max-papers 2

# Definir diretório de saída geral
python main.py --output-dir ../data/output search --databases econpapers
```

## Saída

Os resultados são salvos em `data/processed/YYYYMMDD_HHMMSS/` contendo:

| Arquivo | Descrição |
|---------|-----------|
| `results.xlsx` | Excel com aba "Resultados" (1 linha/paper) e aba "Resumo" (estatísticas) |
| `results.csv` | CSV com separador `;` e encoding UTF-8-BOM (compatível com Excel PT-BR) |
| `results.ris` | RIS para importação em gerenciadores bibliográficos (Zotero, Mendeley) |
| `results.json` | JSON completo (pode ser recarregado com `--input-json`) |

## Configuração

O arquivo `config.yaml` controla todo o comportamento do pipeline:

| Seção | Parâmetros principais |
|-------|----------------------|
| `search` | bases a buscar, diretório de keywords, range de datas, max resultados |
| `dedup` | threshold fuzzy (0-100), normalização de títulos |
| `llm` | provider, modelo, API key, temperatura, rate limit |
| `paths` | diretório de PDFs, diretório de questionários |
| `output` | diretório de saída, formatos, timestamping |
| `logging` | nível console (INFO/DEBUG), nível arquivo (DEBUG) |

## Origem

Reimplementação limpa do sistema `survey_extraction_system` do projeto de tese (CAEN/UFC), usando como referência de arquitetura o projeto `slr-disasters-birth-outcomes`.
