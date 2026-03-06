# Guia de Reprodutibilidade — pndr_survey

Este documento descreve como reproduzir **completamente** a revisão sistemática da literatura sobre instrumentos da PNDR, desde a importação dos registros bibliográficos até a compilação do artigo final em PDF.

## 📋 Índice

- [Visão Geral](#visão-geral)
- [Pré-requisitos](#pré-requisitos)
- [Quick Start](#quick-start)
- [Pipeline Completo](#pipeline-completo)
- [Etapas Individuais](#etapas-individuais)
- [Dados Externos](#dados-externos)
- [Solução de Problemas](#solução-de-problemas)
- [Estrutura de Arquivos](#estrutura-de-arquivos)

---

## 🎯 Visão Geral

Este projeto implementa uma revisão sistemática reproduzível em **3 níveis**:

### **Nível 1: Reprodução Completa** (este guia)
Refazer toda a análise do zero:
- ✅ Importar registros bibliográficos das 5 bases (RIS/Excel versionados)
- ✅ Deduplicação + triagem pré-LLM
- ⚠️ Análise LLM dos PDFs (requer API key + PDFs externos)
- ✅ Matching de citações + índice de citação
- ✅ Geração de tabelas LaTeX
- ✅ Geração de figuras (mapas, gráficos)
- ✅ Compilação do artigo em PDF

### **Nível 2: Reprodução Parcial** (sem re-análise LLM)
Regenerar outputs a partir de dados intermediários:
- Pular análise LLM (usar JSONs processados versionados)
- Regenerar tabelas, figuras e PDF

### **Nível 3: Apenas Compilação** (sem regenerar dados)
Compilar diretamente o artigo LaTeX:
- Todas as tabelas e figuras já versionadas
- `pdflatex latex/0-main.tex`

**Este guia cobre o Nível 1** (reprodução completa).

---

## 🔧 Pré-requisitos

### Software Necessário

| Software | Versão Mínima | Instalação | Verificar |
|----------|---------------|------------|-----------|
| **Python** | 3.12+ | [python.org](https://www.python.org/downloads/) | `python --version` |
| **Git** | 2.30+ | [git-scm.com](https://git-scm.com/) | `git --version` |
| **R** | 4.2+ | [cran.r-project.org](https://cran.r-project.org/) | `Rscript --version` |
| **LaTeX** | TeX Live 2023+ ou MiKTeX | [latex-project.org](https://www.latex-project.org/get/) | `pdflatex --version` |

### Dependências Python

Instaladas automaticamente via `requirements.txt`:
- `rapidfuzz>=3.0` — Deduplicação fuzzy
- `rispy>=0.8` — Parsing RIS
- `pdfplumber>=0.11` — Extração de texto de PDFs
- `google-generativeai>=0.8` — API Gemini
- `pandas>=2.0`, `openpyxl>=3.1` — Importação/exportação
- `pyyaml>=6.0` — Configuração

### Pacotes R

Necessários para gerar figuras (mapas e gráficos):
```r
install.packages(c("ggplot2", "sf", "tidyverse", "RColorBrewer", "readxl"))
```

### Dados Externos

⚠️ **Não versionados no repositório** (grandes demais ou de terceiros):

1. **PDFs dos estudos** (119 arquivos, ~119 MB)
   - Devem estar em `data/2-papers/2-2-papers-pdfs/`
   - Nomeados no formato: `<index>-<authors>-<year>-<title>.pdf`
   - **Obtenção**: Veja seção [Dados Externos](#dados-externos)

2. **Dados RDS da tese** (para gerar figuras)
   - Diretório: `C:/OneDrive/github/tese/bulding_dataset_R/output/data`
   - Contém: `pib_percapita_relativo_2002_2021.rds`, `tipologia_2018.rds`, etc.
   - **Obtenção**: Clone `github.com/<USER>/tese` ou baixe do Zenodo (link futuro)

3. **Shapefiles IBGE** (para mapas)
   - Diretório: `C:/OneDrive/DATABASES`
   - Contém: `BR_Municipios_2020`, `BR_UF_2020`, `Semiarido`, `AmazoniaLegal`
   - **Obtenção**: [geoftp.ibge.gov.br](https://geoftp.ibge.gov.br/organizacao_do_territorio/malhas_territoriais/)

### Credenciais

- **GEMINI_API_KEY**: Chave de API do Google Gemini (para análise LLM)
  - Obter em: [ai.google.dev](https://ai.google.dev/)
  - Configurar via variável de ambiente: `set GEMINI_API_KEY=sua-chave-aqui` (Windows) ou `export GEMINI_API_KEY=...` (Linux/Mac)
  - ⚠️ **Custo**: ~$5-10 para analisar 119 PDFs com `gemini-2.5-flash`

---

## 🚀 Quick Start

### 1. Clonar o Repositório

```bash
git clone https://github.com/<USER>/pndr_survey.git
cd pndr_survey
```

### 2. Configurar Ambiente Python

```bash
# Criar ambiente virtual
python -m venv .venv

# Ativar (Windows)
.venv\Scripts\activate

# Ativar (Linux/Mac)
source .venv/bin/activate

# Instalar dependências
pip install -r scripts/requirements.txt
```

### 3. Configurar Pipeline

```bash
# Copiar template de configuração
cp scripts/config.example.yaml scripts/config.yaml

# Editar config.yaml
# - Definir GEMINI_API_KEY (ou via variável de ambiente)
# - Configurar paths de dados externos (external_data_dir, external_shapefiles_dir)
```

### 4. Obter Dados Externos

Veja seção [Dados Externos](#dados-externos) para instruções detalhadas.

**Mínimo necessário para começar:**
- PDFs em `data/2-papers/2-2-papers-pdfs/` (para análise LLM)
- Dados RDS e shapefiles (para gerar figuras)

### 5. Executar Pipeline Completo

**Opção A: Makefile** (requer GNU Make via Git Bash/WSL):
```bash
make all
```

**Opção B: Build Script** (nativo Windows):
```cmd
build.bat all
```

**Opção C: Passo a passo** (veja [Pipeline Completo](#pipeline-completo))

---

## 🔄 Pipeline Completo

O pipeline é organizado em **9 etapas sequenciais**:

```
[1] Import     → Importar registros das 5 bases (RIS/Excel)
[2] Screen     → Triagem pré-LLM (tipo, idioma, palavras-chave)
[3] Analyze    → Análise LLM dos PDFs (3 estágios: triagem, metodologia, resultados)
[4] Merge      → Mesclar registros bibliográficos + classificação LLM
[5] Citations  → Matching de citações entre estudos + índice de citação
[6] References → Gerar RIS/BibTeX de estudos aprovados
[7] Tables     → Gerar todas as tabelas LaTeX
[8] Figures    → Gerar mapas e gráficos
[9] LaTeX      → Compilar artigo em PDF
```

### Execução Automática

```bash
# Makefile (Git Bash/WSL)
make all

# Build Script (Windows)
build.bat all
```

**Tempo estimado:**
- Etapas 1-2, 4-9: ~5-10 minutos
- Etapa 3 (análise LLM): **~2-4 horas** (119 PDFs, rate limit 4s)

**Outputs finais:**
- `latex/0-main.pdf` — Artigo compilado
- `data/1-records/processed/bib_records.json` — 119 registros normalizados
- `data/2-papers/2-2-papers.json` — JSON enriquecido (registros + LLM + triagem)
- `data/3-ref-bib/citation_index_results.json` — Índice de citação

---

## 📦 Etapas Individuais

Você pode executar cada etapa separadamente para diagnóstico ou re-execução parcial.

### [1] Import — Importar Registros

**O que faz:**
- Importa registros bibliográficos de 5 bases (Scopus, SciELO, CAPES, EconPapers, ANPEC)
- Normaliza campos (autores, título, DOI, ano, etc.)
- Deduplica por DOI + fuzzy matching de títulos (threshold 90%)
- Gera `data/1-records/processed/bib_records.json` (119 registros únicos)

**Executar:**
```bash
# Makefile
make import

# Build Script
build.bat import

# Comando direto
cd scripts
python main.py search --verbose \
  --import-scopus "../data/1-records/1-1-records-scopus/scopus_20260225.ris" \
  --import-scielo "../data/1-records/1-2-records-scielo/scielo_20260226.ris" \
  --import-capes "../data/1-records/1-3-records-capes/capes_20260224.ris" \
  --import-econpapers "../data/1-records/1-4-records-econpapers/econpapers_20260224.ris" \
  --import-anpec "../data/1-records/1-5-records-anpec/anpec_20260225.xlsx"
```

**Inputs:**
- `data/1-records/1-{1..5}-records-*/` (RIS/Excel versionados)

**Outputs:**
- `data/1-records/processed/bib_records.json` (119 registros)
- `data/1-records/processed/duplicates_removed.csv` (28 duplicatas)

---

### [2] Screen — Triagem Pré-LLM

**O que faz:**
- Filtra registros por tipo de documento (exclui teses, dissertações, livros, etc.)
- Valida idioma (português, inglês)
- Verifica presença de palavras-chave de relevância no título/resumo
- Gera `data/1-records/processed/bib_screened.json`

**Executar:**
```bash
# Makefile
make screen

# Build Script
build.bat screen

# Comando direto
cd scripts
python main.py screen --verbose --input-json "../data/1-records/processed/bib_records.json"
```

**Inputs:**
- `data/1-records/processed/bib_records.json`

**Outputs:**
- `data/1-records/processed/bib_screened.json` (registros após triagem)

---

### [3] Analyze — Análise LLM dos PDFs

**O que faz:**
- Extrai texto dos PDFs (via `pdfplumber`)
- Executa 3 estágios de análise via Gemini API:
  - **Stage 1**: Triagem (aprovado/rejeitado + justificativa)
  - **Stage 2**: Metodologia (unidade amostral, métodos quantitativos)
  - **Stage 3**: Resultados (instrumentos da PNDR avaliados, resultados por instrumento)
- Salva checkpoint incremental em `_llm_checkpoint.json`

**⚠️ Pré-requisitos:**
- PDFs em `data/2-papers/2-2-papers-pdfs/` (119 arquivos)
- `GEMINI_API_KEY` configurada
- Créditos na conta Gemini (~$5-10 para 119 PDFs)

**Executar:**
```bash
# Makefile
make analyze

# Build Script
build.bat analyze

# Comando direto
cd scripts
set GEMINI_API_KEY=sua-chave-aqui
python run_llm_all_papers.py
```

**Tempo estimado:** 2-4 horas (rate limit 4s entre requests)

**Inputs:**
- `data/2-papers/2-2-papers-pdfs/*.pdf` (119 PDFs)
- `questionnaires/stage_{1,2,3}.json` (questionários LLM)

**Outputs:**
- `data/2-papers/_llm_checkpoint.json` (checkpoint incremental)

**Retomar análise interrompida:**
O script detecta automaticamente o checkpoint e retoma do último paper processado.

---

### [4] Merge — Mesclar Registros + LLM

**O que faz:**
- Combina registros bibliográficos (`bib_records.json`) com classificação LLM (`_llm_checkpoint.json`)
- Adiciona metadados de triagem manual (se houver)
- Gera JSON enriquecido: `data/2-papers/2-2-papers.json`

**Executar:**
```bash
# Makefile
make merge

# Build Script
build.bat merge

# Comando direto
cd scripts
python merge_papers_to_json.py
```

**Inputs:**
- `data/1-records/processed/bib_records.json`
- `data/2-papers/_llm_checkpoint.json`

**Outputs:**
- `data/2-papers/2-2-papers.json` (119 registros enriquecidos)

---

### [5] Citations — Matching de Citações + Índice

**O que faz:**
- Extrai referências bibliográficas dos PDFs dos estudos aprovados (via Gemini)
- Estrutura referências em JSON por estudo
- Faz matching de citações cruzadas entre estudos da triagem
- Calcula índice de citação (IC) para estudos não-publicados

**Executar:**
```bash
# Makefile
make citations

# Build Script
build.bat citations

# Comando direto
cd scripts
python match_refs_to_studies.py
python citation_index.py
```

**Inputs:**
- `data/2-papers/2-2-papers.json`
- `data/2-papers/2-2-papers-pdfs/*.pdf` (PDFs dos aprovados)

**Outputs:**
- `data/3-ref-bib/refs_por_estudo/*.json` (referências por estudo)
- `data/3-ref-bib/citation_index_results.json` (índice de citação)
- `data/3-ref-bib/citation_index_report.txt` (relatório)

---

### [6] References — Gerar RIS/BibTeX Aprovados

**O que faz:**
- Filtra RIS para incluir apenas estudos aprovados na triagem
- Converte RIS → BibTeX (para citações no LaTeX)
- Gera tabela de índice de citação em LaTeX (com `\citeonline`)

**Executar:**
```bash
# Makefile
make references

# Build Script
build.bat references

# Comando direto
cd scripts
python generate_approved_ris.py
python generate_bibtex.py
python generate_ic_table.py
```

**Inputs:**
- `data/1-records/all_records.ris`
- `data/2-papers/2-2-papers.json`
- `data/3-ref-bib/citation_index_results.json`

**Outputs:**
- `data/3-ref-bib/approved_studies.ris` (35 estudos aprovados)
- `latex/references.bib` (BibTeX)
- `latex/tabela_ic.tex` (tabela de índice de citação)

---

### [7] Tables — Gerar Tabelas LaTeX

**O que faz:**
- Regenera todas as tabelas derivadas do artigo:
  - `tabelas/survey_estudos_ano.tex` — Distribuição de estudos por ano
  - `tabelas/survey_instrumentos.tex` — Instrumentos da PNDR avaliados
  - `tabelas/survey_autores.tex` — Autores mais frequentes
  - `tabelas/survey_unidade_amostral.tex` — Unidades amostrais
  - `tabelas/survey_metodos.tex` — Métodos quantitativos
  - E outras tabelas específicas da análise

**Executar:**
```bash
# Makefile
make tables

# Build Script
build.bat tables

# Comando direto
cd scripts
python generate_latex_tables.py
```

**Inputs:**
- `data/2-papers/2-2-papers.json`

**Outputs:**
- `latex/tabelas/*.tex` (tabelas LaTeX)

---

### [8] Figures — Gerar Figuras

**O que faz:**
- Executa scripts R para gerar figuras da seção de Política Regional:
  - `distribuicao_pib_relativo_municipal.png` — Mapas de PIB per capita relativo (2002, 2010, 2019, 2021)
  - `tipologia_II_simples_com_legenda.png` — Mapa de tipologia regional 2018
  - `icf_superint_setor.png` — Gráfico de incentivos fiscais por superintendência e setor

**⚠️ Pré-requisitos:**
- R instalado + pacotes (`ggplot2`, `sf`, `tidyverse`, `RColorBrewer`, `readxl`)
- Dados RDS da tese em `external_data_dir` (configurado em `config.yaml`)
- Shapefiles IBGE em `external_shapefiles_dir` (configurado em `config.yaml`)

**Executar:**
```bash
# Makefile
make figures

# Build Script
build.bat figures

# Comando direto
cd scripts
python generate_figures.py --verbose
```

**Listar status das figuras:**
```bash
cd scripts
python generate_figures.py --list
```

**Validar dependências:**
```bash
cd scripts
python generate_figures.py --validate
```

**Inputs:**
- `data/r_scripts/*.R` (scripts R)
- Dados RDS externos (tese)
- Shapefiles IBGE

**Outputs:**
- `figures/*.png` (3 figuras geradas)

**Nota:** A figura `tipologia_I.JPG` (Decreto nº 6.047/2007) é externa e não é gerada por script.

---

### [9] LaTeX — Compilar Artigo

**O que faz:**
- Compila o artigo em PDF usando `pdflatex` + `bibtex`
- 3 passagens para resolver referências cruzadas

**Executar:**
```bash
# Makefile
make latex

# Build Script
build.bat latex

# Comando direto
cd latex
pdflatex -interaction=nonstopmode 0-main.tex
bibtex 0-main
pdflatex -interaction=nonstopmode 0-main.tex
pdflatex -interaction=nonstopmode 0-main.tex
```

**Inputs:**
- `latex/0-main.tex` (arquivo principal)
- `latex/tabelas/*.tex` (tabelas)
- `figures/*.png` (figuras)
- `latex/references.bib` (BibTeX)

**Outputs:**
- `latex/0-main.pdf` (artigo final)

---

## 📂 Dados Externos

### 1. PDFs dos Estudos (119 arquivos)

**Localização esperada:** `data/2-papers/2-2-papers-pdfs/`

**Formato de nomeação:**
```
<index>-<authors>-<year>-<title>.pdf
```
Exemplo: `001-silva-carvalho-2015-impactos-fnee-nordeste.pdf`

**Obtenção:**

**Opção A: Download Automático** (futuro)
```bash
cd scripts
python download_pdfs.py --from-doi
```
⚠️ Script ainda não implementado. Requer DOIs válidos e acesso institucional.

**Opção B: Download Manual**
1. Consulte `data/2-papers/all_papers.xlsx` (lista de DOIs/URLs)
2. Baixe manualmente de editoras, Google Scholar, ou SciHub
3. Renomeie seguindo o formato acima
4. Coloque em `data/2-papers/2-2-papers-pdfs/`

**Opção C: Zenodo** (futuro)
Baixe o arquivo ZIP de PDFs do Zenodo:
```bash
# URL será adicionado quando o dataset for publicado
wget https://zenodo.org/record/XXXXXX/files/pndr_survey_pdfs.zip
unzip pndr_survey_pdfs.zip -d data/2-papers/2-2-papers-pdfs/
```

**Verificar PDFs:**
```bash
cd scripts
python -c "import os; print(len([f for f in os.listdir('../data/2-papers/2-2-papers-pdfs') if f.endswith('.pdf')]))"
# Deve retornar: 119
```

---

### 2. Dados RDS da Tese

**Localização esperada:** Configurado em `scripts/config.yaml` → `figures.external_data_dir`

**Exemplo:** `C:/OneDrive/github/tese/bulding_dataset_R/output/data`

**Arquivos necessários:**
- `pib_percapita_relativo_2002_2021.rds` — Dados de PIB per capita municipal
- `tipologia_2018.rds` — Tipologia regional MIR 2018
- `incentivos_fiscais_sudene_sudam.xlsx` — Dados de incentivos fiscais

**Obtenção:**

**Opção A: Clonar repositório da tese**
```bash
cd C:/OneDrive/github  # Ou outro diretório de sua preferência
git clone https://github.com/<USER>/tese.git
```
Ajuste `external_data_dir` em `scripts/config.yaml` para apontar para `<path>/tese/bulding_dataset_R/output/data`.

**Opção B: Zenodo** (futuro)
Baixe apenas os RDS necessários:
```bash
wget https://zenodo.org/record/XXXXXX/files/pndr_data_rds.zip
unzip pndr_data_rds.zip -d data/external_data/
```

---

### 3. Shapefiles IBGE

**Localização esperada:** Configurado em `scripts/config.yaml` → `figures.external_shapefiles_dir`

**Exemplo:** `C:/OneDrive/DATABASES`

**Estrutura de diretórios:**
```
C:/OneDrive/DATABASES/
├── BR_Municipios_2020/
│   └── BR_Municipios_2020.shp
├── BR_UF_2020/
│   └── BR_UF_2020.shp
├── Semiarido/
│   └── sab_2017.shp
└── AmazoniaLegal/
    └── amazonia_legal.shp
```

**Obtenção:**

**Fonte oficial:** [geoftp.ibge.gov.br](https://geoftp.ibge.gov.br/organizacao_do_territorio/malhas_territoriais/)

**Download direto (2020):**
```bash
# Municípios
wget https://geoftp.ibge.gov.br/organizacao_do_territorio/malhas_territoriais/malhas_municipais/municipio_2020/Brasil/BR/BR_Municipios_2020.zip
unzip BR_Municipios_2020.zip -d C:/OneDrive/DATABASES/BR_Municipios_2020/

# UFs
wget https://geoftp.ibge.gov.br/organizacao_do_territorio/malhas_territoriais/malhas_municipais/municipio_2020/Brasil/BR/BR_UF_2020.zip
unzip BR_UF_2020.zip -d C:/OneDrive/DATABASES/BR_UF_2020/
```

**Semiárido e Amazônia Legal:**
- Semiárido: [sudene.gov.br](https://www.sudene.gov.br/acesso-a-informacao/institucional/area-de-atuacao-da-sudene/semiarido)
- Amazônia Legal: [ibge.gov.br](https://www.ibge.gov.br/geociencias/cartas-e-mapas/mapas-regionais/15819-amazonia-legal.html)

---

## 🐛 Solução de Problemas

### Erro: "config.yaml not found"

**Solução:**
```bash
cp scripts/config.example.yaml scripts/config.yaml
# Edite config.yaml com suas configurações
```

---

### Erro: "GEMINI_API_KEY not configured"

**Solução:**
```bash
# Windows
set GEMINI_API_KEY=sua-chave-aqui

# Linux/Mac
export GEMINI_API_KEY=sua-chave-aqui
```

Ou edite `scripts/config.yaml`:
```yaml
llm:
  api_key: "sua-chave-aqui"  # Não use ${GEMINI_API_KEY}
```

---

### Erro: "PDFs directory not found or empty"

**Solução:**
Certifique-se de que os PDFs estão em `data/2-papers/2-2-papers-pdfs/`.

Verificar:
```bash
dir data\2-papers\2-2-papers-pdfs\*.pdf | find /C ".pdf"
# Deve retornar: 119
```

Se ausentes, veja seção [Dados Externos](#dados-externos).

---

### Erro: "R not found" ao gerar figuras

**Solução:**

1. Instale R: [cran.r-project.org](https://cran.r-project.org/)
2. Instale pacotes necessários:
   ```r
   install.packages(c("ggplot2", "sf", "tidyverse", "RColorBrewer", "readxl"))
   ```
3. Configure `r_executable` em `config.yaml` (deixe vazio para auto-detecção):
   ```yaml
   figures:
     r_executable: ""  # Auto-detect
   ```

Verificar instalação:
```bash
Rscript --version
```

---

### Erro: "external_data_dir not found" ao gerar figuras

**Solução:**

1. Clone o repositório da tese ou baixe os RDS (veja [Dados Externos](#dados-externos))
2. Ajuste `external_data_dir` em `config.yaml`:
   ```yaml
   figures:
     external_data_dir: "C:/OneDrive/github/tese/bulding_dataset_R/output/data"
   ```

Validar configuração:
```bash
cd scripts
python generate_figures.py --validate
```

---

### Erro: "Shapefiles not found" ao gerar figuras

**Solução:**

1. Baixe shapefiles IBGE (veja [Dados Externos](#dados-externos))
2. Ajuste `external_shapefiles_dir` em `config.yaml`:
   ```yaml
   figures:
     external_shapefiles_dir: "C:/OneDrive/DATABASES"
   ```

Validar:
```bash
cd scripts
python generate_figures.py --validate
```

---

### Erro: "pdflatex: command not found"

**Solução:**

Instale uma distribuição LaTeX:
- **Windows**: [MiKTeX](https://miktex.org/download) ou [TeX Live](https://www.tug.org/texlive/)
- **Linux**: `sudo apt install texlive-full`
- **Mac**: [MacTeX](https://www.tug.org/mactex/)

Verificar:
```bash
pdflatex --version
```

---

### Análise LLM muito lenta

**Diagnóstico:**
Rate limit configurado em `config.yaml`:
```yaml
llm:
  rate_limit_seconds: 4  # 4 segundos entre requests
```

**Soluções:**
1. **Reduzir rate limit** (se sua cota Gemini permitir):
   ```yaml
   llm:
     rate_limit_seconds: 2  # Mais rápido, mas pode atingir limite
   ```

2. **Usar modelo mais rápido** (mas menos preciso):
   ```yaml
   llm:
     model: gemini-1.5-flash  # Mais rápido que gemini-2.5-flash
   ```

3. **Processar subconjunto** (para testes):
   Edite `run_llm_all_papers.py` para limitar quantidade de papers.

---

### Compilação LaTeX falha com "references.bib not found"

**Solução:**
Gere o BibTeX antes de compilar:
```bash
cd scripts
python generate_bibtex.py
```

Ou execute o pipeline completo:
```bash
make references latex
# ou
build.bat references latex
```

---

## 📁 Estrutura de Arquivos

### Versionados (no Git)

```
pndr_survey/
├── scripts/                          # Pipeline Python
│   ├── main.py                       # CLI
│   ├── run_llm_all_papers.py         # Análise LLM
│   ├── generate_*.py                 # Geradores de outputs
│   ├── config.example.yaml           # Template de configuração
│   ├── requirements.txt              # Dependências Python
│   ├── src/                          # Módulos do pipeline
│   ├── keywords/                     # Queries de busca
│   └── questionnaires/               # Questionários LLM
├── data/
│   ├── 1-records/
│   │   └── 1-{1..5}-records-*/       # RIS/Excel das 5 bases (versionados)
│   ├── 2-papers/
│   │   └── 2-1-papers_scripts/       # Scripts de renomeação
│   └── 3-ref-bib/
│       └── (scripts Python/R)        # Scripts de extração/estruturação
├── latex/                            # Artigo LaTeX (editado manualmente)
│   ├── 0-main.tex                    # Arquivo principal
│   ├── *.tex                         # Seções do artigo
│   └── tabelas/                      # Tabelas manuais (não geradas)
├── figures/                          # Figuras (geradas ou externas)
├── docs/                             # Documentação do pipeline
├── Makefile                          # Orquestração (GNU Make)
├── build.bat                         # Build script (Windows)
├── REPRODUCING.md                    # Este arquivo
├── README.md                         # Visão geral do projeto
├── CLAUDE.md                         # Regras de desenvolvimento
└── .gitignore                        # Exclusões do Git
```

### Gerados (não versionados)

```
data/
├── 1-records/processed/              # Registros processados
│   ├── bib_records.json              # 119 registros normalizados
│   ├── bib_screened.json             # Após triagem pré-LLM
│   └── duplicates_removed.csv        # 28 duplicatas removidas
├── 2-papers/
│   ├── 2-2-papers.json               # JSON enriquecido (registros + LLM)
│   ├── 2-2-papers-pdfs/              # 119 PDFs (não versionados)
│   ├── _llm_checkpoint.json          # Checkpoint da análise LLM
│   └── all_papers_llm_classif*.xlsx  # Planilhas de classificação
└── 3-ref-bib/
    ├── refs_por_estudo/              # JSONs com referências por estudo
    ├── citation_index_results.json   # Índice de citação
    ├── citation_index_report.txt     # Relatório IC
    └── approved_studies.ris          # RIS filtrado (aprovados)

latex/
├── references.bib                    # BibTeX gerado
├── tabela_ic.tex                     # Tabela de índice de citação
├── tabelas/*.tex                     # Tabelas geradas
└── 0-main.pdf                          # Artigo compilado
```

---

## 📊 Estatísticas do Pipeline

| Etapa | Input | Output | Tempo Estimado |
|-------|-------|--------|----------------|
| Import | 5 bases RIS/Excel | 119 registros únicos | ~30s |
| Screen | 119 registros | 119 registros triados | ~10s |
| Analyze | 119 PDFs | 119 classificações LLM | **2-4h** |
| Merge | Registros + LLM | JSON enriquecido | ~5s |
| Citations | 35 PDFs aprovados | 104 citações cruzadas | ~15min |
| References | JSON + IC | RIS/BibTeX/Tabela IC | ~10s |
| Tables | JSON enriquecido | 5+ tabelas LaTeX | ~5s |
| Figures | RDS + shapefiles | 3 figuras PNG | ~30s |
| LaTeX | Tabelas + figuras | PDF final | ~1min |

**Total:** ~3-5 horas (dominado pela análise LLM)

---

## 📝 Citação

Se você usar este pipeline ou dados, por favor cite:

```bibtex
@article{pndr_survey_2026,
  title={Revisão Sistemática dos Instrumentos da PNDR: Evidências Empíricas 2000-2025},
  author={Autor, Nome},
  journal={Revista},
  year={2026},
  note={Pipeline reproduzível disponível em: https://github.com/<USER>/pndr_survey}
}
```

---

## 📧 Contato

Para dúvidas sobre reprodutibilidade:
- **Issues**: [github.com/<USER>/pndr_survey/issues](https://github.com/<USER>/pndr_survey/issues)
- **Email**: [email@example.com](mailto:email@example.com)

---

## 📜 Licença

- **Código**: MIT License
- **Dados**: CC BY 4.0 (com atribuição)
- **Artigo**: Copyright dos autores (após publicação: licença da revista)

---

**Última atualização:** 2026-03-03
**Versão:** 1.0.0
