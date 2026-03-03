# Dados Externos — pndr_survey

Este arquivo documenta todos os dados externos necessários para reproduzir completamente a revisão sistemática. Esses dados **não estão versionados** no repositório Git por serem grandes demais ou pertencerem a terceiros.

## 📋 Índice

- [Visão Geral](#visão-geral)
- [1. PDFs dos Estudos](#1-pdfs-dos-estudos)
- [2. Dados RDS da Tese](#2-dados-rds-da-tese)
- [3. Shapefiles IBGE](#3-shapefiles-ibge)
- [Verificação](#verificação)

---

## 🎯 Visão Geral

| Dataset | Tamanho | Necessário Para | Alternativa |
|---------|---------|-----------------|-------------|
| **PDFs dos estudos** | ~119 MB | Análise LLM | Usar `2-2-papers.json` pré-processado (Nível 2) |
| **Dados RDS da tese** | ~50 MB | Gerar figuras (mapas PIB, tipologia) | Usar figuras PNG já geradas (Nível 3) |
| **Shapefiles IBGE** | ~200 MB | Gerar figuras (mapas) | Usar figuras PNG já geradas (Nível 3) |

**Nota:** Se você quer apenas compilar o artigo LaTeX (Nível 3), **não precisa** desses dados. Eles são necessários apenas para reproduzir completamente o pipeline (Nível 1).

---

## 1. PDFs dos Estudos

### Descrição

119 artigos científicos coletados nas bases Scopus, SciELO, CAPES, EconPapers e ANPEC. São os insumos para a análise LLM (extração de texto + classificação em 3 estágios).

### Localização Esperada

```
data/2-papers/2-2-papers-pdfs/
```

### Formato de Nomeação

```
<index>-<authors>-<year>-<title>.pdf
```

**Exemplos:**
- `001-silva-carvalho-2015-impactos-fne-nordeste.pdf`
- `042-almeida-perobelli-2018-fdne-convergencia-regional.pdf`
- `118-ribeiro-2023-incentivos-fiscais-sudene.pdf`

### Estatísticas

- **Quantidade:** 119 PDFs
- **Tamanho total:** ~119 MB
- **Período:** 2000-2025
- **Idiomas:** Português (78), Inglês (41)
- **Fontes:**
  - Scopus: 16
  - SciELO: 5
  - CAPES: 30
  - EconPapers: 24
  - ANPEC: 44

### Obtenção

#### Opção A: Download Manual (Atual)

1. Consulte a lista de estudos em `data/2-papers/all_papers.xlsx`
2. Campos úteis: `doi`, `url`, `title`, `authors`, `year`
3. Baixe manualmente de:
   - Editoras acadêmicas (se tiver acesso institucional)
   - Google Scholar → PDF disponível
   - SciHub (⚠️ legalidade varia por país)
   - Repositórios institucionais (para teses/dissertações)
4. Renomeie seguindo o formato acima
5. Coloque em `data/2-papers/2-2-papers-pdfs/`

**Script auxiliar de renomeação:**
```bash
cd data/2-papers/2-1-papers_scripts
python rename_pdfs.py --input ../baixados/ --output ../2-2-papers-pdfs/
```

#### Opção B: Zenodo (Futuro)

⚠️ **Ainda não disponível.** Será publicado após aceitação do artigo.

```bash
# URL será adicionado quando o dataset for publicado
wget https://zenodo.org/record/XXXXXX/files/pndr_survey_pdfs.zip
unzip pndr_survey_pdfs.zip -d data/2-papers/2-2-papers-pdfs/
```

#### Opção C: Download Automático via DOI (Futuro)

⚠️ **Script não implementado.**

```bash
cd scripts
python download_pdfs.py --from-doi --output ../data/2-papers/2-2-papers-pdfs/
```

Limitações:
- Requer DOIs válidos (nem todos os estudos têm)
- Requer acesso institucional ou Unpaywall API
- Taxa de sucesso: ~60-70% (nem todos os PDFs estão abertos)

### Verificação

```bash
# Windows
dir /B data\2-papers\2-2-papers-pdfs\*.pdf | find /C ".pdf"

# Linux/Mac
ls -1 data/2-papers/2-2-papers-pdfs/*.pdf | wc -l
```

**Saída esperada:** `119`

---

## 2. Dados RDS da Tese

### Descrição

Datasets processados do projeto de tese relacionado, contendo dados de PIB per capita municipal, tipologia regional MIR 2018, e incentivos fiscais SUDENE/SUDAM. Usados para gerar as figuras da seção de Política Regional do artigo.

### Localização Esperada

Configurada em `scripts/config.yaml` → `figures.external_data_dir`

**Exemplo:**
```yaml
figures:
  external_data_dir: "C:/OneDrive/github/tese/bulding_dataset_R/output/data"
```

### Estrutura de Diretórios

```
<external_data_dir>/
├── pib_percapita_relativo_2002_2021.rds       # PIB per capita relativo municipal (4 anos)
├── tipologia_2018.rds                         # Tipologia MIR 2018 (9 categorias)
├── incentivos_fiscais_sudene_sudam.xlsx       # Dados de ICF por setor e superintendência
└── ...                                        # Outros datasets da tese (não usados)
```

### Estatísticas

- **Formato:** RDS (R Data Serialization) + XLSX
- **Tamanho total:** ~50 MB
- **Dados:**
  - PIB: 5570 municípios × 4 anos (2002, 2010, 2019, 2021)
  - Tipologia: 5570 municípios × 9 categorias (renda × dinamismo)
  - ICF: Agregados por superintendência (SUDENE, SUDAM) e setor (industrial, agropecuário, comércio/serviços)

### Obtenção

#### Opção A: Clonar Repositório da Tese (Recomendado)

```bash
cd C:/OneDrive/github  # Ou outro diretório de sua preferência
git clone https://github.com/<USER>/tese.git
```

Ajuste `external_data_dir` em `scripts/config.yaml`:
```yaml
figures:
  external_data_dir: "C:/OneDrive/github/tese/bulding_dataset_R/output/data"
```

**Vantagem:** Acesso a todos os dados e scripts da tese.

#### Opção B: Zenodo (Futuro)

⚠️ **Ainda não disponível.**

```bash
wget https://zenodo.org/record/XXXXXX/files/pndr_data_rds.zip
unzip pndr_data_rds.zip -d data/external_data/
```

Ajuste `config.yaml`:
```yaml
figures:
  external_data_dir: "./data/external_data"  # Caminho relativo
```

#### Opção C: Gerar do Zero (Avançado)

Se você tem acesso aos dados brutos (IBGE, RAIS, IPEADATA):

1. Clone o repositório da tese
2. Execute o pipeline R de construção dos datasets:
   ```bash
   cd tese/bulding_dataset_R
   Rscript build_all.R
   ```

**Tempo estimado:** ~2-3 horas (download de dados + processamento)

### Verificação

```bash
cd scripts
python generate_figures.py --validate
```

**Saída esperada:**
```
Validando distribuicao_pib_relativo_municipal.png...
  [OK] Todas as dependências OK
Validando tipologia_II_simples_com_legenda.png...
  [OK] Todas as dependências OK
Validando icf_superint_setor.png...
  [OK] Todas as dependências OK
```

---

## 3. Shapefiles IBGE

### Descrição

Malhas territoriais do IBGE (municípios, UFs) e delimitações de regiões especiais (Semiárido, Amazônia Legal). Usados para gerar mapas temáticos.

### Localização Esperada

Configurada em `scripts/config.yaml` → `figures.external_shapefiles_dir`

**Exemplo:**
```yaml
figures:
  external_shapefiles_dir: "C:/OneDrive/DATABASES"
```

### Estrutura de Diretórios

```
<external_shapefiles_dir>/
├── BR_Municipios_2020/
│   ├── BR_Municipios_2020.shp       # Shapefile principal
│   ├── BR_Municipios_2020.dbf       # Atributos
│   ├── BR_Municipios_2020.shx       # Índice espacial
│   └── BR_Municipios_2020.prj       # Projeção (SIRGAS 2000)
├── BR_UF_2020/
│   └── BR_UF_2020.shp (+ .dbf, .shx, .prj)
├── Semiarido/
│   └── sab_2017.shp (+ .dbf, .shx, .prj)
└── AmazoniaLegal/
    └── amazonia_legal.shp (+ .dbf, .shx, .prj)
```

### Estatísticas

- **Formato:** ESRI Shapefile (.shp + auxiliares)
- **Tamanho total:** ~200 MB (comprimido: ~50 MB)
- **Projeção:** SIRGAS 2000 (EPSG:4674)
- **Resolução:**
  - Municípios: 5570 polígonos (2020)
  - UFs: 27 polígonos (2020)
  - Semiárido: Delimitação SUDENE 2017
  - Amazônia Legal: Lei nº 1.806/1953 com alterações

### Obtenção

#### Opção A: Download Direto IBGE (Recomendado)

**Fonte oficial:** [geoftp.ibge.gov.br](https://geoftp.ibge.gov.br/organizacao_do_territorio/malhas_territoriais/)

**Municípios 2020:**
```bash
wget https://geoftp.ibge.gov.br/organizacao_do_territorio/malhas_territoriais/malhas_municipais/municipio_2020/Brasil/BR/BR_Municipios_2020.zip
unzip BR_Municipios_2020.zip -d C:/OneDrive/DATABASES/BR_Municipios_2020/
```

**UFs 2020:**
```bash
wget https://geoftp.ibge.gov.br/organizacao_do_territorio/malhas_territoriais/malhas_municipais/municipio_2020/Brasil/BR/BR_UF_2020.zip
unzip BR_UF_2020.zip -d C:/OneDrive/DATABASES/BR_UF_2020/
```

**Semiárido:**
- **Fonte:** [SUDENE — Delimitação do Semiárido](https://www.sudene.gov.br/acesso-a-informacao/institucional/area-de-atuacao-da-sudene/semiarido)
- **Resolução CONDEL nº 107/2017**

```bash
# Link direto (se disponível)
wget https://www.sudene.gov.br/.../sab_2017.zip
unzip sab_2017.zip -d C:/OneDrive/DATABASES/Semiarido/
```

**Amazônia Legal:**
- **Fonte:** [IBGE — Amazônia Legal](https://www.ibge.gov.br/geociencias/cartas-e-mapas/mapas-regionais/15819-amazonia-legal.html)

```bash
wget https://geoftp.ibge.gov.br/.../amazonia_legal.zip
unzip amazonia_legal.zip -d C:/OneDrive/DATABASES/AmazoniaLegal/
```

#### Opção B: Repositório Consolidado (Futuro)

⚠️ **Ainda não disponível.**

```bash
wget https://zenodo.org/record/XXXXXX/files/ibge_shapefiles_2020.zip
unzip ibge_shapefiles_2020.zip -d C:/OneDrive/DATABASES/
```

#### Opção C: Pacote R `geobr` (Alternativa)

Se preferir baixar programaticamente via R:

```r
install.packages("geobr")
library(geobr)

# Municípios 2020
municipios <- read_municipality(year = 2020)
sf::st_write(municipios, "C:/OneDrive/DATABASES/BR_Municipios_2020/BR_Municipios_2020.shp")

# UFs 2020
ufs <- read_state(year = 2020)
sf::st_write(ufs, "C:/OneDrive/DATABASES/BR_UF_2020/BR_UF_2020.shp")

# Semiárido
semiarido <- read_semiarid()
sf::st_write(semiarido, "C:/OneDrive/DATABASES/Semiarido/sab_2017.shp")

# Amazônia Legal
amazonia <- read_amazon()
sf::st_write(amazonia, "C:/OneDrive/DATABASES/AmazoniaLegal/amazonia_legal.shp")
```

### Verificação

```bash
cd scripts
python generate_figures.py --validate
```

**Saída esperada:**
```
Validando distribuicao_pib_relativo_municipal.png...
  [OK] Shapefile encontrado: C:/OneDrive/DATABASES/BR_Municipios_2020/BR_Municipios_2020.shp
  [OK] Shapefile encontrado: C:/OneDrive/DATABASES/BR_UF_2020/BR_UF_2020.shp
  [OK] Todas as dependências OK
```

---

## ✅ Verificação Completa

Execute o script de validação para verificar **todos** os dados externos de uma vez:

```bash
cd scripts
python generate_figures.py --validate
```

**Saída esperada se tudo estiver OK:**
```
=== VALIDAÇÃO DE DEPENDÊNCIAS ===

Validando distribuicao_pib_relativo_municipal.png...
  [OK] Todas as dependências OK

Validando tipologia_II_simples_com_legenda.png...
  [OK] Todas as dependências OK

Validando icf_superint_setor.png...
  [OK] Todas as dependências OK

[OK] Todas as dependências estão disponíveis.
```

---

## 📊 Checklist de Dados

Use esta checklist para garantir que você tem todos os dados necessários:

- [ ] **PDFs dos estudos** (119 arquivos em `data/2-papers/2-2-papers-pdfs/`)
  - [ ] Verificado com `dir /B ... | find /C ".pdf"` → retorna 119
- [ ] **Dados RDS da tese** (configurado em `config.yaml`)
  - [ ] `pib_percapita_relativo_2002_2021.rds` existe
  - [ ] `tipologia_2018.rds` existe
  - [ ] `incentivos_fiscais_sudene_sudam.xlsx` existe
- [ ] **Shapefiles IBGE** (configurado em `config.yaml`)
  - [ ] `BR_Municipios_2020/BR_Municipios_2020.shp` existe
  - [ ] `BR_UF_2020/BR_UF_2020.shp` existe
  - [ ] `Semiarido/sab_2017.shp` existe (opcional, para mapas específicos)
  - [ ] `AmazoniaLegal/amazonia_legal.shp` existe (opcional, para mapas específicos)
- [ ] **Validação executada** com sucesso
  - [ ] `python generate_figures.py --validate` → sem erros

---

## 📝 Notas

1. **Dados sensíveis:** Nenhum dos datasets contém dados pessoais ou sensíveis. Todos são dados públicos agregados (IBGE, SUDENE, SUDAM).

2. **Licenças:**
   - Dados IBGE: Domínio público (Lei nº 12.527/2011)
   - Shapefiles SUDENE/IBGE: CC BY 4.0
   - PDFs dos estudos: Copyright dos autores/editoras (uso acadêmico justificado por revisão sistemática)

3. **Privacidade:** Os PDFs são usados apenas para extração automatizada de texto. Não redistribuímos os PDFs publicamente (apenas metadados e classificações).

4. **Reprodutibilidade parcial:** Se você **não** conseguir obter os PDFs ou dados RDS, ainda pode:
   - **Nível 2:** Usar os JSONs processados (`2-2-papers.json`) para regenerar tabelas
   - **Nível 3:** Usar as figuras PNG já geradas para compilar o artigo LaTeX

---

## 📧 Contato

Se você tiver dificuldades para obter algum dataset:
- **Issues:** [github.com/<USER>/pndr_survey/issues](https://github.com/<USER>/pndr_survey/issues)
- **Email:** [email@example.com](mailto:email@example.com)

Podemos fornecer orientações adicionais ou, em casos específicos, compartilhar datasets via canais privados (respeitando direitos autorais).

---

**Última atualização:** 2026-03-03
