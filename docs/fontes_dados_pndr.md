# Fontes de Dados dos Instrumentos da PNDR

Este documento centraliza as fontes oficiais de todos os dados externos utilizados no projeto `pndr_survey` para a seção de Política Regional. Cada arquivo em `data/external_data/` está mapeado à sua fonte, período e status.

**Período-alvo:** 2002-2023

---

## 1. Fundos Constitucionais de Financiamento (FC)

**Fonte oficial:** Portal Brasileiro de Dados Abertos
**URL:** https://dados.gov.br/dados/conjuntos-dados/fundos-constitucionais-de-financiamento
**Descrição:** Contratações dos Fundos Constitucionais FNE (Nordeste), FNO (Norte) e FCO (Centro-Oeste), criados pela CF/1988 e regulamentados pela Lei nº 7.827/1989.
**Operadores:** BNB (FNE), BASA (FNO), BB (FCO)

| Arquivo em `data/external_data/fc/` | Período | Status |
|--------------------------------------|---------|--------|
| `FNE - Contratações 2000 a 2018.xlsx` | 2000-2018 | PENDENTE — copiar de `C:/OneDrive/DATABASES/FUNDOS CONSTITUCIONAIS/` |
| `FNO - Contratações 2000 a 2018.xlsx` | 2000-2018 | PENDENTE — copiar |
| `FCO - Contratações 2000 a 2018.xlsx` | 2000-2018 | PENDENTE — copiar |
| `Consolidado Dez_2019 - FCF.xlsx` | 2019 | PENDENTE — copiar |
| `Consolidado Dez_2020 - FCF.xlsx` | 2020 | PENDENTE — copiar |
| `Consolidado Dez_2021 - FCF.xlsx` | 2021 | PENDENTE — copiar |
| Consolidado 2022 | 2022 | PENDENTE — obter da fonte oficial |
| Consolidado 2023 | 2023 | PENDENTE — obter da fonte oficial |

---

## 2. Fundos de Desenvolvimento Regional (FD)

**Fonte oficial:** Portal Brasileiro de Dados Abertos
**URL:** https://dados.gov.br/dados/conjuntos-dados/fundos-de-desenvolvimento-regional
**Descrição:** Liberações e projetos aprovados dos Fundos de Desenvolvimento FDNE (Nordeste), FDA (Amazônia) e FDCO (Centro-Oeste). Fundos contábeis destinados a financiamento de investimentos privados de grande porte.
**Gestores:** SUDENE (FDNE), SUDAM (FDA), SUDECO (FDCO)

| Arquivo em `data/external_data/` | Instrumento | Período | Status |
|-----------------------------------|-------------|---------|--------|
| `fdne_liberacoes_ate_jun_2023.xlsx` | FDNE | 2008-2023 | OK |
| `fda_liberacoes_ate_2025.pdf` | FDA | 2007-2025 | OK (PDF — requer extração) |
| `fds_contratacoes.xlsx` | FDS | — | OK |
| Dados FDCO projetos aprovados | FDCO | 2014-2023 | PENDENTE — verificar fonte oficial |

---

## 3. Incentivos Fiscais (IF)

### 3a. SUDENE

**Fonte oficial:** Portal Brasileiro de Dados Abertos
**URL:** https://dados.gov.br/dados/conjuntos-dados/incentivos-e-beneficios-fiscais-e-financeiros
**Descrição:** Incentivos e benefícios fiscais administrados pela SUDENE: redução de 75% do IRPJ para empreendimentos prioritários na área de atuação (Lei nº 4.239/1963, MP nº 2.199-14/2001, Lei nº 14.753/2023).

| Arquivo em `data/external_data/` | Período | Status |
|-----------------------------------|---------|--------|
| `if_sudene.json` | 2010-2024 | OK |

### 3b. SUDAM

**Fonte oficial:** Repositório SUDAM
**URL:** http://repositorio.sudam.gov.br/sudam/incentivos-fiscais/relatorios
**Descrição:** Relatórios de incentivos fiscais (redução e isenção de IRPJ) administrados pela SUDAM para empreendimentos na área da Amazônia Legal.

| Arquivo em `data/external_data/if_sudam/` | Período | Status |
|--------------------------------------------|---------|--------|
| `Relação Incentivos Fiscais Redução e Isenção - 2010.pdf` | 2010 | OK |
| `Relação Incentivos Fiscais Redução e Isenção - 2011.pdf` | 2011 | OK |
| `Relação Incentivos Fiscais Redução e Isenção - 2012.pdf` | 2012 | OK |
| `Relação Incentivos Fiscais Redução e Isenção - 2013.pdf` | 2013 | OK |
| `Relação Incentivos Fiscais Redução e Isenção - 2014.pdf` | 2014 | OK |
| `Relação Incentivos Fiscais Redução e Isenção - 2015.pdf` | 2015 | OK |
| `Relação Incentivos Fiscais Redução e Isenção - 2016.pdf` | 2016 | OK |
| `Relação Incentivos Fiscais Redução e Isenção - 2017.pdf` | 2017 | OK |
| `Relação Incentivos Fiscais Redução e Isenção - 2018.pdf` | 2018 | OK |
| `Relação Incentivos Fiscais Redução e Isenção - 2019.pdf` | 2019 | OK |
| `Relação Incentivos Fiscais Redução e Isenção - 2020.pdf` | 2020 | OK |
| `Planilha - Aprovados 2021 Redução e Reinvestimento.pdf` | 2021 | OK |
| `Planilha - Aprovados 2022 Redução e Reinvestimento.pdf` | 2022 | OK |
| `Planilha - Aprovados 2023 Redução e Reinvestimento.pdf` | 2023 | OK |
| `Merged.pdf` | 2010-2023 | OK (consolidado dos PDFs acima) |
| `Merged.xlsx` | 2010-2023 | OK (versão estruturada do consolidado) |

---

## 4. Dados Auxiliares

### 4a. PIB Municipal (IBGE)

**Fonte oficial:** IBGE — Sistema de Contas Nacionais
**URL:** PENDENTE — documentar URL do SIDRA/IBGE
**Descrição:** Produto Interno Bruto dos Municípios, a preços correntes (R$ 1.000).

| Arquivo no projeto | Período | Status |
|---------------------|---------|--------|
| `pib_municipios_2002_2009.xlsx` (raiz) | 2002-2009 | OK |
| `pib_municipios_2010_2023.xlsx` (raiz) | 2010-2023 | OK |

### 4b. População Municipal (IBGE)

**Fonte oficial:** PENDENTE — documentar (IBGE Estimativas populacionais ou Censo)
**URL:** PENDENTE

| Arquivo | Descrição | Status |
|---------|-----------|--------|
| `populacao_municipios.csv` | População municipal por ano | PENDENTE — copiar para `data/external_data/auxiliar/` |

### 4c. Deflator IPCA (IBGE)

**Fonte oficial:** PENDENTE — documentar (IBGE/SIDRA ou IPEADATA)
**URL:** PENDENTE

| Arquivo | Descrição | Status |
|---------|-----------|--------|
| `br_ibge_ipca.anual_2002_2020.csv` | Fator IPCA anual para deflação | PENDENTE — copiar para `data/external_data/auxiliar/` e atualizar até 2023 |

### 4d. Tipologia PNDR 2007

**Fonte oficial:** Decreto nº 6.047/2007 — Anexo com classificação dos municípios
**URL:** PENDENTE — documentar URL oficial (MIN/SUDENE)

| Arquivo | Descrição | Status |
|---------|-----------|--------|
| `tipologia_2007.xlsx` | Tipologia PNDR 2007 (4 categorias: Alta Renda, Baixa Renda, Dinâmica, Estagnada) | PENDENTE — copiar para `data/external_data/auxiliar/` |

### 4e. Códigos de Municípios (IBGE)

**Fonte oficial:** IBGE — Cadastro de Municípios
**URL:** PENDENTE — documentar

| Arquivo | Descrição | Status |
|---------|-----------|--------|
| `cod_municipios_IBGE.csv` | Código IBGE (7 dígitos), nome e UF | PENDENTE — copiar para `data/external_data/auxiliar/` |

### 4f. Shapefiles Geoespaciais (IBGE)

**Fonte oficial:** IBGE — Malhas Territoriais
**URL:** https://www.ibge.gov.br/geociencias/downloads-geociencias.html
**Descrição:** Malhas municipais e estaduais para geração de mapas temáticos.

| Shapefile | Descrição | Status |
|-----------|-----------|--------|
| `BR_Municipios_2021.shp` | Malha municipal IBGE 2021 (5.570 municípios) | Externo (`C:/OneDrive/DATABASES/`) — não versionado |
| `BR_UF_2021.shp` | Malha estadual IBGE 2021 | Externo — não versionado |
| Semiárido (SUDENE) | Delimitação oficial do Semiárido | Externo — não versionado |
| Amazônia Legal (IBGE) | Municípios da Amazônia Legal | Externo — não versionado |

---

## Notas

- As URLs foram verificadas em março de 2026.
- Itens marcados como **PENDENTE** requerem ação: obter o dado, copiar para `data/external_data/` e documentar a URL de origem.
- Dados auxiliares (população, IPCA, tipologia, códigos IBGE) devem ser copiados para `data/external_data/auxiliar/` para que scripts não referenciem paths externos.
- Shapefiles são grandes (~200 MB) e ficam fora do repositório, configurados via `config.yaml`.
- Para cada dataset utilizado, documentar a **data de acesso** e a **versão** do conjunto de dados.
