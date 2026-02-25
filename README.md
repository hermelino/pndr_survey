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
│   │   ├── capes.txt
│   │   ├── scopus.txt
│   │   └── anpec.txt
│   ├── questionnaires/     # Questionários JSON para análise LLM
│   │   ├── stage_1_screening.json   # Triagem (9 perguntas)
│   │   ├── stage_2_methods.json     # Metodologia (9 perguntas)
│   │   └── stage_3_results.json     # Resultados (7 perguntas)
│   └── src/
│       ├── models.py       # BibRecord + PaperRecord (dataclasses)
│       ├── config.py       # Carregamento YAML + validação
│       ├── searchers/      # Busca em bases acadêmicas
│       │   ├── base.py             # BaseSearcher ABC
│       │   ├── econpapers.py       # Semi-automático (import RIS/CSV)
│       │   ├── capes.py            # Semi-automático (import RIS/CSV)
│       │   ├── scopus.py           # Semi-automático (import RIS/CSV)
│       │   └── anpec.py            # Semi-automático (import Excel/RIS/CSV)
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

Bases acadêmicas (EconPapers, CAPES, Scopus, ANPEC)
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

## Log de Extração (25/02/2026)

### Dados coletados

| Base | Arquivo em `data/` | Registros | PDFs | Método de busca |
|------|--------------------|-----------|------|-----------------|
| EconPapers/RePEc | `econpapers_ris/econpapers_combined.ris` | 24 | 19 (manual) | Busca manual em econpapers.repec.org, exportação RIS individual, unificação em arquivo combinado. PDFs baixados manualmente em `papers/econpapers/` |
| Portal CAPES | `capes_ris/Periodicos-CAPES-RIS.ris` | 30 | 0 (pendente) | Busca avançada no Portal de Periódicos CAPES via CAFe, exportação RIS |
| Scopus | `scopus_ris/scopus_export_Feb 25-2026_*.ris` | 16 | 0 (pendente) | Advanced query no Scopus com sintaxe `TITLE-ABS-KEY(...)`, exportação RIS |
| ANPEC | `anpec_extraction/resultados_anpec_pesquisa_250226_1030.xlsx` | 62 | 62 (auto) | Busca via Google com `site:anpec.org.br`, extração com extensão Claude para navegador, download automático |
| **Total bruto** | | **132** | **81** | |

### Deduplicação

- Duplicatas por DOI exato: 2
- Duplicatas por título fuzzy (threshold 80%): 5
- **Total de registros únicos: 125**

### Queries utilizadas

**EconPapers / CAPES** (query booleana genérica):
```
("fundo constitucional" OR "fundos constitucionais" OR "fundo de desenvolvimento"
OR "fundos de desenvolvimento" OR "incentivo fiscal" OR "incentivos fiscais")
AND ("FNE" OR "FNO" OR "FCO" OR "FDNE" OR "FDCO" OR "SUDENE" OR "SUDECO"
OR "SUDAM" OR "PNDR")
```

**Scopus** (sintaxe Advanced query):
```
TITLE-ABS-KEY("fundo constitucional" OR "fundo de desenvolvimento"
OR "incentivo fiscal" OR "incentivos fiscais" OR "regional fund"
OR "constitutional fund" OR "development fund" OR "tax incentive")
AND TITLE-ABS-KEY("FNE" OR "FNO" OR "FCO" OR "FDNE" OR "FDCO"
OR "SUDENE" OR "SUDECO" OR "SUDAM" OR "PNDR")
```

**ANPEC** (Google Search com filtro de domínio):
```
site:anpec.org.br ("fundo constitucional" OR "fundos constitucionais"
OR "fundo de desenvolvimento" OR "incentivo fiscal" OR "incentivos fiscais")
("FNE" OR "FNO" OR "FCO" OR "FDNE" OR "SUDENE" OR "SUDAM" OR "PNDR")
```

### Decisões metodológicas

- **Google Scholar excluído**: retorna 12.000+ resultados com proporção elevada de irrelevantes; periódicos relevantes já cobertos pelo CAPES e RePEc. Decisão alinhada com a justificativa da tese (seção 1.3).
- **Web of Science excluído**: cobertura já atendida pelo CAPES e RePEc.
- **PDFs do EconPapers**: 19 de 24 baixados manualmente a partir das landing pages RePEc (5 não disponíveis ou duplicatas). Salvos em `data/papers/econpapers/`. Lista de URLs em `data/econpapers_ris/econpapers_urls.txt`.
- **PDFs de CAPES e Scopus**: não possuem URL direta para PDF nos metadados exportados. Download manual pendente via acesso institucional ou resolução de DOI.

### Comando de importação unificada

```bash
cd scripts
python main.py --verbose search \
  --import-econpapers "../data/econpapers_ris/econpapers_combined.ris" \
  --import-capes "../data/capes_ris/Periodicos-CAPES-RIS.ris" \
  --import-scopus "../data/scopus_ris/scopus_export_Feb 25-2026_bd09397c-fbc7-4454-8d88-0d42afc92ae6.ris" \
  --import-anpec "../data/anpec_extraction/resultados_anpec_pesquisa_250226_1030.xlsx"
```

### Próximos passos

1. ~~Baixar PDFs do EconPapers~~ — 19/24 concluído (`data/papers/econpapers/`)
2. Baixar manualmente os PDFs de CAPES (30) e Scopus (16) e colocar em `data/papers/`
3. Executar análise LLM: `python main.py analyze`
4. Exportar resultados: `python main.py export`

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

#### 1.2 Importar do EconPapers / IDEAS (RePEc)

O EconPapers usa renderização JavaScript, então a busca é semi-manual:

1. Acesse [EconPapers](https://econpapers.repec.org/scripts/search.pf) ou [IDEAS](https://ideas.repec.org/cgi-bin/htsearch2)
2. Cole a query (gerada com `--dry-run`) no campo de busca
3. Baixe o arquivo RIS de cada resultado (não há opção de exportar todos de uma vez)
4. Salve os arquivos em `data/econpapers_ris/`

**Unificar os arquivos RIS individuais:**

```bash
python -c "
from pathlib import Path
import rispy

ris_dir = Path('data/econpapers_ris')
files = sorted(ris_dir.glob('*.ris'))
combined = '\n\n'.join(f.read_text(encoding='utf-8').strip() for f in files)
Path('data/econpapers_combined.ris').write_text(combined, encoding='utf-8')

with open('data/econpapers_combined.ris', encoding='utf-8') as fh:
    print(f'{len(rispy.load(fh))} registros combinados de {len(files)} arquivos')
"
```

**Importar no pipeline:**

```bash
cd scripts
python main.py search --import-econpapers ../data/econpapers_ris/econpapers_combined.ris
```

#### 1.3 Buscar em bases semi-automáticas (CAPES, Scopus, ANPEC)

Para bases sem API, o pipeline gera instruções de busca manual. O fluxo é:

1. Rodar `--dry-run` para obter a query formatada
2. Executar a busca manualmente na base (via navegador, etc.)
3. Exportar os resultados como arquivo RIS, CSV ou Excel
4. Importar os resultados no pipeline:

```bash
# Importar resultados do Portal CAPES
python main.py search --import-capes caminho/para/capes_results.ris

# Importar resultados do Scopus
python main.py search --import-scopus caminho/para/scopus_results.csv

# Importar resultados da ANPEC (Excel, RIS ou CSV)
python main.py search --import-anpec caminho/para/anpec_results.xlsx

# Importar de múltiplas bases de uma vez
python main.py search \
  --import-capes capes.ris \
  --import-scopus scopus.csv \
  --import-anpec anpec.xlsx
```

#### 1.4 Opções de controle da busca

```bash
# Pular deduplicação (manter todos os registros)
python main.py search --import-capes results.ris --skip-dedup

# Pular download de PDFs (apenas coletar metadados)
python main.py search --databases econpapers --skip-download

# Combinar busca automática com importação manual
python main.py search --databases econpapers --import-capes capes.ris
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
