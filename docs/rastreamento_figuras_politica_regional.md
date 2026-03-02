# Rastreamento de Figuras - Seção "Política Regional no Brasil"

**Documento:** `latex/politica-regional.tex`
**Data da análise:** 2026-03-02
**Propósito:** Identificar scripts geradores para cada figura/gráfico da seção

---

## Resumo Executivo

De 4 figuras identificadas na seção:
- ✅ **2 figuras** possuem scripts geradores confirmados
- ⚠️ **1 figura** possui script gerador provável (requer verificação)
- ❌ **1 figura** NÃO possui script gerador (fonte externa)

---

## Figuras Identificadas

### 1. Distribuição do PIB per capita relativo municipal

**Label LaTeX:** `fig:pib_relativo` (linha 17)
**Arquivo:** `distribuicao_pib_relativo_municipal.png`
**Localização:** `c:\OneDrive\github\pndr_survey\figures\distribuicao_pib_relativo_municipal.png`

**Status:** ✅ **Script confirmado**

**Script gerador:**
- **Caminho:** `c:\OneDrive\github\tese\bulding_dataset_R\source_code\mapa_distribuicao_pib_municipal.R`
- **Linguagem:** R
- **Bibliotecas:** `ggplot2`, `sf`, `cowplot`, `dplyr`, `readr`
- **Saídas:**
  - `../output/maps/distribuicao_pib_relativo_municipal.png`
  - `../../arquivos_latex/tese/figuras/distribuicao_pib_relativo_municipal.png`

**Descrição do script:**
- Gera 4 mapas (anos 2002, 2010, 2019, 2021)
- Classifica municípios em 5 categorias de PIB per capita relativo
- Foca em municípios das superintendências (SUDAM, SUDENE, SUDECO)
- Usa shapefiles municipais e estaduais de 2021
- Paleta de cores: verde claro → azul escuro

**Dados necessários:**
- `../output/data/dataset_completo_com_pib_relativo.rds`
- `C:/OneDrive/DATABASES/DIVISÃO POLÍTICA E REGIONAL/SHAPES/BR_Municipios_2021/BR_Municipios_2021.shp`
- `C:/OneDrive/DATABASES/DIVISÃO POLÍTICA E REGIONAL/SHAPES/BR_UF_2021/BR_UF_2021.shp`

---

### 2. Tipologia 2007 (Subfigura)

**Label LaTeX:** `fig:sub1` (linha 67)
**Arquivo:** `tipologia_I.JPG`
**Localização:** `c:\OneDrive\github\pndr_survey\figures\tipologia_I.JPG`

**Status:** ❌ **Sem script gerador (fonte externa)**

**Fonte:** Figura extraída de \citeonline{BrasilPndr2006} (Decreto nº 6.047/2007)

**Observações:**
- Imagem em formato JPG (não PNG, indicando fonte externa)
- Tipologia original da PNDR de 2007
- Baseada em regiões geográficas imediatas
- **Não reproduzível via script** (documento oficial do governo)

---

### 3. Tipologia 2018 (Subfigura)

**Label LaTeX:** `fig:sub2` (linha 76)
**Arquivo:** `tipologia_II_simples_com_legenda.png`
**Localização:** `c:\OneDrive\github\pndr_survey\figures\tipologia_II_simples_com_legenda.png`

**Status:** ⚠️ **Script provável (requer verificação)**

**Scripts candidatos:**
1. `c:\OneDrive\github\tese\bulding_dataset_R\source_code\mapa_tipologia_simples.R`
2. `c:\OneDrive\github\tese\bulding_dataset_R\source_code\mapa_tipologia_rapido.R`
3. `c:\OneDrive\github\tese\bulding_dataset_R\source_code\mapa_tipologia_regioes.R`

**Script mais provável:** `mapa_tipologia_simples.R`
- **Saída:** `../output/maps/tipologia_simples.png`
- **Linguagem:** R
- **Bibliotecas:** `ggplot2`, `sf`, `dplyr`, `readr`
- **Ano base:** 2020
- **Características:**
  - 9 categorias (cruzamento renda × dinamismo)
  - Inclui bordas de Semiárido e Amazônia Legal (opcional)
  - Paleta: vermelho → amarelo → verde → azul → branco

**Observações:**
- O nome do arquivo final (`tipologia_II_simples_com_legenda.png`) difere da saída do script (`tipologia_simples.png`)
- Possível renomeação manual ou versão editada
- **Recomendação:** Verificar se a figura atual corresponde à saída do script

**Dados necessários:**
- `../output/data/painel_balanc_var_ln_pibrpc.rds`
- Shapefiles municipais e estaduais (2021)
- Opcionais: shapefiles Semiárido e Amazônia Legal

---

### 4. Incentivos Fiscais por Superintendência e Setor

**Label LaTeX:** `fig:incentivos` (linha 117)
**Arquivo:** `icf_superint_setor.png`
**Localização:** `c:\OneDrive\github\pndr_survey\figures\icf_superint_setor.png`

**Status:** ✅ **Script confirmado**

**Script gerador:**
- **Caminho:** `c:\OneDrive\github\tese\bulding_dataset_R\source_code\grafico_resumo_icf.R`
- **Linguagem:** R
- **Bibliotecas:** `ggplot2`, `RColorBrewer`, `tidyverse`, `readxl`
- **Saída:** `../output/plots/icf_superint_setor.png` (via função `save_plot()`)

**Descrição do script:**
- Gráfico de barras empilhadas (facetas SUDENE/SUDAM)
- Categorização por tipologia 2007 (Alta Renda, Baixa Renda, Dinâmica, Estagnada)
- Breakdown por setor (6 setores: Ind. Transformação, Infraestrutura, etc.)
- Linha vermelha sobreposta: média per capita (por 100 mil hab.)
- Eixo secundário à direita para valores per capita

**Dados necessários:**
- `../output/data/classif_incent_fiscais.xlsx`
- `../output/data/painel_icf.rds`
- `../output/data/populacao_fc.rds`
- `C:/OneDrive/DATABASES/MUNICÍPIOS/tipologia_2007.xlsx`

**Funções auxiliares:**
- `save_plot()` definida em `./output_helpers.R`

---

## Dependências dos Scripts

### Shapefiles Geoespaciais
```
C:/OneDrive/DATABASES/DIVISÃO POLÍTICA E REGIONAL/
├── SHAPES/
│   ├── BR_Municipios_2021/BR_Municipios_2021.shp
│   ├── BR_UF_2021/BR_UF_2021.shp
├── LIM_Semiarido_Municipal_OFICIAL/LIM_Semiarido_Municipal_OFICIAL.shp
└── AMAZONIA LEGAL/Mun_Amazonia_Legal_2022_shp/Mun_Amazonia_Legal_2022.shp
```

### Dados Processados (RDS/Excel)
```
tese/bulding_dataset_R/output/data/
├── dataset_completo_com_pib_relativo.rds
├── painel_balanc_var_ln_pibrpc.rds
├── classif_incent_fiscais.xlsx
├── painel_icf.rds
└── populacao_fc.rds
```

### Arquivos de Configuração
```
tese/bulding_dataset_R/source_code/
└── output_helpers.R  (funções save_plot, save_map, etc.)
```

---

## Recomendações

### Para reprodução completa:
1. **Verificar disponibilidade** dos dados RDS no repositório `tese`
2. **Confirmar correspondência** entre `tipologia_simples.png` e `tipologia_II_simples_com_legenda.png`
3. **Documentar processo de renomeação** se houver edição manual das figuras
4. **Considerar migração** dos scripts R para o repositório `pndr_survey` (autonomia)

### Para documentação:
- Adicionar comentário no LaTeX indicando script gerador
- Exemplo:
  ```latex
  % Gerado por: tese/bulding_dataset_R/source_code/mapa_distribuicao_pib_municipal.R
  \includegraphics[width=1\textwidth]{distribuicao_pib_relativo_municipal.png}
  ```

### Para manutenção:
- Manter versionamento dos scripts no repositório `tese`
- Atualizar figuras automaticamente se dados mudarem
- Documentar dependências externas (shapefiles, IBGE, etc.)

---

## Regeneração de Figuras

### Script Python de Orquestração

**Localização:** `scripts/generate_figures.py`

O projeto agora inclui um wrapper Python que orquestra os scripts R para regenerar as figuras automaticamente.

### Comandos Disponíveis

```bash
cd scripts

# Listar status de todas as figuras
python generate_figures.py --list

# Validar dependências (R, dados, shapefiles)
python generate_figures.py --validate

# Gerar figuras (incremental)
python generate_figures.py

# Forçar regeneração de todas
python generate_figures.py --force
```

### Configuração Necessária

Edite `scripts/config.yaml`, seção `figures:`:

```yaml
figures:
  external_data_dir: "C:/OneDrive/github/tese/bulding_dataset_R/output/data"
  external_shapefiles_dir: "C:/OneDrive/DATABASES"
  r_executable: ""  # Vazio = auto-detect
```

### Implementação

- **Módulo:** `scripts/src/figure_generators/`
  - `base.py` - Classe abstrata com validação de deps e timestamps
  - `r_wrapper.py` - Executor de scripts R com auto-detecção
  - `pib_map_generator.py` - Gerador do mapa PIB
  - `tipologia_map_generator.py` - Gerador do mapa tipologia
  - `icf_plot_generator.py` - Gerador do gráfico ICF

- **Scripts R:** Copiados para `data/r_scripts/` (versionados)

- **Documentação:** `data/r_scripts/README.md` (dependências detalhadas)

### Próximos Passos

1. ✅ Confirmar que `tipologia_I.JPG` não precisa de script (fonte externa oficial)
2. ✅ Verificar e documentar origem de `tipologia_II_simples_com_legenda.png` (gerada por `mapa_tipologia_simples.R`)
3. ✅ Validar que scripts R de PIB e ICF geram figuras corretas
4. ✅ Adicionar comentários no LaTeX referenciando scripts
5. ✅ Wrapper script criado para regenerar todas as figuras (`generate_figures.py`)

---

**Última atualização:** 2026-03-02
**Responsável:** Claude Code Agent
