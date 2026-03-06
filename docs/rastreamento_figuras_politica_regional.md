# Rastreamento de Figuras - Seção "Política Regional no Brasil"

**Documento:** `latex/politica-regional.tex`
**Data da análise:** 2026-03-02
**Propósito:** Identificar scripts geradores para cada figura/gráfico da seção

---

## Resumo Executivo

De 5 figuras identificadas na seção:
- ✅ **3 figuras** possuem scripts geradores confirmados (2 Python local + 1 R/tese)
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

**Status:** ✅ **Script confirmado (Python, dados locais)**

**Script gerador:**
- **Caminho:** `c:\OneDrive\github\pndr_survey\scripts\generate_policy_figures.py` → `generate_if_figure()`
- **Linguagem:** Python (matplotlib)
- **Execução:** `python scripts/generate_policy_figures.py --only if`

**Descrição:**
- 2 painéis (SUDENE / SUDAM) com barras empilhadas por tipologia 2007
- Breakdown por setor (6 setores: Ind. Transformação, Infraestrutura, etc.)
- Sem eixo secundário

**Dados necessários (todos em `data/external_data/`):**
- `classif_incent_fiscais.xlsx`

**Referência R original:** `tese/bulding_dataset_R/source_code/grafico_resumo_icf.R`

---

### 5. Valor Liberado pelos Fundos de Desenvolvimento

**Label LaTeX:** `fig:fd` (linha ~66)
**Arquivo:** `fd_fundo_setor.png`
**Localização:** `c:\OneDrive\github\pndr_survey\figures\fd_fundo_setor.png`

**Status:** ✅ **Script confirmado (Python, dados locais)**

**Script gerador:**
- **Caminho:** `c:\OneDrive\github\pndr_survey\scripts\generate_policy_figures.py` → `generate_fd_figure()`
- **Linguagem:** Python (matplotlib)
- **Execução:** `python scripts/generate_policy_figures.py --only fd`

**Descrição:**
- 3 painéis (FDNE / FDA / FDCO) com barras empilhadas por tipologia 2007
- Breakdown por setor (Infraestrutura, Ind. Transformação, Ind. Extrativa, Serviços)
- Linha vermelha sobreposta: participação % média no PIB local
- Eixo secundário à direita para % do PIB

**Dados necessários (todos em `data/external_data/`):**
- `resumo_fd.xlsx` (sheets: `por_fundo_setor_tipologia`, `medias_pib_tipologia`)

**Pré-processamento:** `python scripts/process_fd_data.py` (gera as sheets necessárias)

**Referência R original:** `tese/bulding_dataset_R/source_code/grafico_resumo_fd.R`

---

## Dependências dos Scripts

### Figuras 4 e 5 (IF e FD) — Dados locais em `data/external_data/`
```
data/external_data/
├── classif_incent_fiscais.xlsx   (IF: classificação por superintendência/tipologia/setor)
├── resumo_fd.xlsx                (FD: resumo por fundo/setor/tipologia + % PIB)
├── painel_fd_agregado.rds        (FD: painel municipal para cálculo % PIB)
├── pib_municipios.xlsx           (PIB municipal IBGE)
└── tipologia_2007.xlsx           (Tipologia PNDR 2007)
```

### Figuras 1 e 3 (Mapas PIB e tipologia) — Dependências externas
```
C:/OneDrive/DATABASES/DIVISÃO POLÍTICA E REGIONAL/
├── SHAPES/
│   ├── BR_Municipios_2021/BR_Municipios_2021.shp
│   ├── BR_UF_2021/BR_UF_2021.shp
├── LIM_Semiarido_Municipal_OFICIAL/LIM_Semiarido_Municipal_OFICIAL.shp
└── AMAZONIA LEGAL/Mun_Amazonia_Legal_2022_shp/Mun_Amazonia_Legal_2022.shp

tese/bulding_dataset_R/output/data/
├── dataset_completo_com_pib_relativo.rds
└── painel_balanc_var_ln_pibrpc.rds
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

### Figuras com dados locais (sem dependências externas)

```bash
# FD e IF — gerados inteiramente com dados locais
python scripts/generate_policy_figures.py --only fd   # → figures/fd_fundo_setor.png
python scripts/generate_policy_figures.py --only if   # → figures/icf_superint_setor.png

# Pré-processar dados FD (se necessário regenerar sheets)
python scripts/process_fd_data.py
```

### Figuras com dependências externas (mapas)

Requerem acesso a shapefiles e dados RDS do projeto tese:

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
3. ✅ Figuras FD e ICF migradas para Python com dados locais (`generate_policy_figures.py`)
4. ✅ Adicionar comentários no LaTeX referenciando scripts
5. ⬜ Migrar mapas (PIB e tipologia) para dados locais (requer cópia de shapefiles)

---

**Última atualização:** 2026-03-05
**Responsável:** Claude Code Agent
