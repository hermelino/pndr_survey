# Scripts R de Geração de Figuras

Este diretório contém scripts R para gerar figuras da seção de Política Regional do artigo LaTeX.

## Scripts Disponíveis

| Script | Figura Gerada | Descrição |
|--------|---------------|-----------|
| `mapa_distribuicao_pib_municipal.R` | `distribuicao_pib_relativo_municipal.png` | Mapas da distribuição do PIB per capita relativo (2002, 2010, 2019, 2021) |
| `mapa_tipologia_simples.R` | `tipologia_II_simples_com_legenda.png` | Mapa de tipologia regional 2018 (9 categorias: renda × dinamismo) |
| `grafico_resumo_icf.R` | `icf_superint_setor.png` | Gráfico de barras empilhadas: incentivos fiscais por superintendência e setor |
| `output_helpers.R` | (auxiliar) | Funções `save_plot()`, `save_map()` usadas pelos scripts acima |

## Dependências R

### Pacotes Necessários

Instale os pacotes R executando:

```r
if (!require("pacman")) install.packages("pacman")
pacman::p_load(
  readr,        # Leitura de dados CSV
  dplyr,        # Manipulação de dados
  magrittr,     # Pipe operator %>%
  ggplot2,      # Gráficos
  sf,           # Geometrias espaciais
  cowplot,      # Layouts de gráficos
  RColorBrewer, # Paletas de cores
  scales,       # Formatação de escalas
  readxl,       # Leitura de Excel
  tidyverse     # Conjunto de pacotes tidyverse
)
```

### Versão do R Testada

- **R version:** 4.4.2 (2024-10-31)
- **Platform:** x86_64-w64-mingw32/x64

## Dados Externos Necessários

Os scripts R dependem de dados processados e shapefiles externos, referenciados via `config.yaml`.

### 1. Dados RDS (do projeto `tese`)

**Localização padrão:** `C:/OneDrive/github/tese/bulding_dataset_R/output/data/`

| Arquivo | Tamanho | Usado por | Descrição |
|---------|---------|-----------|-----------|
| `dataset_completo_com_pib_relativo.rds` | ~48 MB | `mapa_distribuicao_pib_municipal.R` | PIB per capita relativo por município (2002-2021) |
| `painel_balanc_var_ln_pibrpc.rds` | ~12 MB | `mapa_tipologia_simples.R` | Painel balanceado para classificação tipológica |
| `classif_incent_fiscais.xlsx` | ~150 KB | `grafico_resumo_icf.R` | Classificação de incentivos fiscais por setor |
| `painel_icf.rds` | ~2 MB | `grafico_resumo_icf.R` | Painel de incentivos fiscais (SUDENE, SUDAM) |
| `populacao_fc.rds` | ~1 MB | `grafico_resumo_icf.R` | População municipal (fundos constitucionais) |

### 2. Dados Auxiliares

| Arquivo | Tamanho | Usado por | Descrição |
|---------|---------|-----------|-----------|
| `C:/OneDrive/DATABASES/MUNICÍPIOS/tipologia_2007.xlsx` | ~50 KB | `grafico_resumo_icf.R` | Tipologia PNDR 2007 (Decreto nº 6.047/2007) |

### 3. Shapefiles Geoespaciais

**Localização padrão:** `C:/OneDrive/DATABASES/DIVISÃO POLÍTICA E REGIONAL/`

#### Shapes Obrigatórios

| Shapefile | Tamanho | Usado por | Descrição |
|-----------|---------|-----------|-----------|
| `SHAPES/BR_Municipios_2021/BR_Municipios_2021.shp` | ~80 MB | Mapas PIB e Tipologia | Malha municipal IBGE 2021 |
| `SHAPES/BR_UF_2021/BR_UF_2021.shp` | ~5 MB | Mapas PIB e Tipologia | Malha estadual IBGE 2021 |

#### Shapes Opcionais (sobreposições)

| Shapefile | Tamanho | Usado por | Descrição |
|-----------|---------|-----------|-----------|
| `LIM_Semiarido_Municipal_OFICIAL/LIM_Semiarido_Municipal_OFICIAL.shp` | ~20 MB | `mapa_tipologia_simples.R` | Delimitação oficial do Semiárido |
| `AMAZONIA LEGAL/Mun_Amazonia_Legal_2022_shp/Mun_Amazonia_Legal_2022.shp` | ~15 MB | `mapa_tipologia_simples.R` | Municípios da Amazônia Legal |

## Configuração

### Passo 1: Instalar R

Download: https://cran.r-project.org/bin/windows/base/

### Passo 2: Instalar Pacotes

Execute o script de instalação acima no console R.

### Passo 3: Configurar Paths

Edite `scripts/config.yaml` para apontar para os diretórios corretos:

```yaml
figures:
  # Diretório de dados RDS do projeto tese
  external_data_dir: "C:/OneDrive/github/tese/bulding_dataset_R/output/data"

  # Diretório base de shapefiles e dados geoespaciais
  external_shapefiles_dir: "C:/OneDrive/DATABASES"

  # Executável R (auto-detect se vazio)
  r_executable: ""  # Ou: "C:/Program Files/R/R-4.4.2/bin/Rscript.exe"
```

## Execução

### Via Python (Recomendado)

```bash
cd scripts
python generate_figures.py                # Gera todas (incremental)
python generate_figures.py --force        # Força regeneração
python generate_figures.py --list         # Lista status
python generate_figures.py --validate     # Valida dependências
```

### Diretamente via R (Debug)

```bash
cd data/r_scripts
Rscript mapa_distribuicao_pib_municipal.R
```

**Nota:** Scripts R salvam outputs em `../../tese/bulding_dataset_R/output/maps/` (paths relativos ao projeto original). O wrapper Python copia automaticamente para `pndr_survey/figures/`.

## Saídas Geradas

| Figura | Formato | Resolução | Tamanho Típico |
|--------|---------|-----------|----------------|
| `distribuicao_pib_relativo_municipal.png` | PNG | 300 DPI | ~1-2 MB |
| `tipologia_II_simples_com_legenda.png` | PNG | 300 DPI | ~2-3 MB |
| `icf_superint_setor.png` | PNG | 300 DPI | ~100-200 KB |

## Troubleshooting

### Erro: "Rscript.exe não encontrado"

- Instale R: https://cran.r-project.org/bin/windows/base/
- Configure `r_executable` no `config.yaml` com o path completo

### Erro: "Pacote 'sf' não instalado"

```r
install.packages("sf")
```

### Erro: "Shapefile não encontrado"

- Verifique se `external_shapefiles_dir` no `config.yaml` está correto
- Execute `python generate_figures.py --validate` para listar arquivos ausentes

### Erro: "Dados RDS não encontrados"

- Verifique se `external_data_dir` no `config.yaml` aponta para `tese/bulding_dataset_R/output/data/`
- Certifique-se de que o projeto `tese` está clonado e atualizado

## Versionamento

**Scripts copiados de:** `C:/OneDrive/github/tese/bulding_dataset_R/source_code/`
**Data da cópia:** 2026-03-02
**Versão do projeto tese:** commit bc913e8 (2026-03-02)

Para atualizar os scripts R:
1. Copie manualmente do projeto `tese`
2. Ou refaça a cópia: `cp C:/OneDrive/github/tese/bulding_dataset_R/source_code/*.R ./`

## Referências

- **IBGE Shapefiles:** https://www.ibge.gov.br/geociencias/downloads-geociencias.html
- **Tipologia PNDR 2007:** Decreto nº 6.047/2007
- **Pacote `sf` (R):** https://r-spatial.github.io/sf/
- **Pacote `ggplot2` (R):** https://ggplot2.tidyverse.org/

---

**Última atualização:** 2026-03-02
**Responsável:** Claude Code Agent
