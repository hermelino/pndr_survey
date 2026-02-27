# Pipeline de Extração

Data da extração: 25-26/02/2026

## Visao geral

Revisao sistematica sobre instrumentos da PNDR (2000-2025). Busca manual em 5 bases academicas, importacao via pipeline, deduplicacao automatica.

| # | Base | Registros | PDFs | % | Status |
|---|------|-----------|------|---|--------|
| 1-1 | Scopus | 16 | 16 | 100% | Concluido |
| 1-2 | SciELO | 4 | 4 | 100% | Concluido |
| 1-3 | Portal CAPES | 26 | 26 | 100% | Concluido |
| 1-4 | EconPapers/RePEc | 11 | 11 | 100% | Concluido |
| 1-5 | ANPEC | 61 | 61 | 100% | Concluido |
| **Total (apos dedup)** | | **118** | **118** | **100%** | **Concluido** |

## Estrategia de busca

Queries armazenadas em `scripts/keywords/`. Estrutura de 3 blocos booleanos:

```
(instrumentos: fundo constitucional, fundo de desenvolvimento, incentivo fiscal)
AND (organizacoes: FNE, FNO, FCO, FDNE, FDCO, SUDENE, SUDAM, PNDR)
AND (geografia: nordeste, amazonia, centro-oeste, brasil)
```

### EconPapers / CAPES

```
("fundo constitucional" OR "fundos constitucionais" OR "fundo de desenvolvimento"
OR "fundos de desenvolvimento" OR "incentivo fiscal" OR "incentivos fiscais")
AND ("FNE" OR "FNO" OR "FCO" OR "FDNE" OR "FDCO" OR "SUDENE" OR "SUDECO"
OR "SUDAM" OR "PNDR")
```

### Scopus

```
TITLE-ABS-KEY("fundo constitucional" OR "fundo de desenvolvimento"
OR "incentivo fiscal" OR "incentivos fiscais" OR "regional fund"
OR "constitutional fund" OR "development fund" OR "tax incentive")
AND TITLE-ABS-KEY("FNE" OR "FNO" OR "FCO" OR "FDNE" OR "FDCO"
OR "SUDENE" OR "SUDECO" OR "SUDAM" OR "PNDR")
```

### ANPEC (Google Search)

```
site:anpec.org.br ("fundo constitucional" OR "fundos constitucionais"
OR "fundo de desenvolvimento" OR "incentivo fiscal" OR "incentivos fiscais")
("FNE" OR "FNO" OR "FCO" OR "FDNE" OR "SUDENE" OR "SUDAM" OR "PNDR")
```

### SciELO

```
("fundo constitucional" OR "fundos constitucionais" OR "fundo de desenvolvimento" OR "fundos de desenvolvimento" OR "incentivo fiscal" OR "incentivos fiscais") AND ("FNE" OR "FNO" OR "FCO" OR "FDNE" OR "FDCO" OR "SUDENE" OR "SUDECO" OR "SUDAM" OR "PNDR")
```


## Metodo de coleta por base

| Base | Procedimento |
|------|-------------|
| **EconPapers** | Busca manual em econpapers.repec.org, exportacao RIS individual, unificacao em arquivo combinado. PDFs baixados manualmente das landing pages. |
| **CAPES** | Busca avancada no Portal de Periodicos CAPES via CAFe, exportacao RIS. |
| **Scopus** | Advanced query via proxy CAPES, exportacao RIS. |
| **ANPEC** | Google Search com `site:anpec.org.br`, extracao com extensao de navegador, exportacao Excel. Download automatico de PDFs. |
| **SciELO** | Busca manual em search.scielo.org, exportacao RIS. PDFs baixados manualmente. |

## Deduplicacao

Algoritmo em 3 fases:

1. **DOI exato** — normaliza lowercase, remove prefixos (modulo `src/dedup/deduplicator.py`)
2. **Titulo fuzzy** — `rapidfuzz.token_sort_ratio >= 80%`, com verificacao adicional: mesmo ano E (mesmo primeiro autor OU mesmo periodico) (modulo `src/dedup/deduplicator.py`)
3. **PDF identico** — registros de bases diferentes que apontam para o mesmo PDF (verificacao manual pos-coleta)

Prioridade de retencao: Scopus > SciELO > CAPES > EconPapers > ANPEC (em caso de duplicata, mantem a versao da base de maior prioridade).

### Removidos por DOI exato (5)

| Titulo | Base removida | Base mantida | DOI |
|--------|---------------|--------------|-----|
| Eficacia do gasto publico: uma avaliacao do FNE, FNO e FCO | CAPES | Scopus | 10.1590/s0101-41612009000100004 |
| Heifer Retention Program in the Pantanal: a study with DEA and Malmquist index | CAPES | Scopus | 10.1590/s1516-35982012000800019 |
| Measuring Micro- and Macro-Impacts of Regional Development Policies (FNE, 2000-2006) | CAPES | Scopus/EconPapers | 10.1080/00343404.2012.667872 |
| Momentos da trajetoria do Estado na Amazonia (FNO e FDA em Carajas) | CAPES | SciELO | 10.22296/2317-1529.rbeur.202245pt |
| Efeito dose resposta do FCO no estado de Goias | SciELO | Scopus | 10.1590/0103-6351/3397 |

### Removidos por titulo fuzzy (4)

| Titulo | Base | Motivo |
|--------|------|--------|
| AVALIACAO DOS IMPACTOS ECONOMICOS DO FNE ENTRE 2004 A 2010 | EconPapers | Variacao de caixa do TD IPEA 1918 |
| EFEITOS DIFERENCIADOS DO FNE NO CRESCIMENTO ECONOMICO DOS MUNICIPIOS NORDESTINOS | EconPapers | Duplicata intra-base |
| EFEITOS DIFERENCIADOS DO FNE NO CRESCIMENTO ECONOMICO DOS MUNICIPIOS NORDESTINOS | EconPapers | Triplicata intra-base |
| Avaliacao dos Impactos Economicos do FCO Entre 2004 e 2010 | EconPapers | Variacao de caixa do TD IPEA 1969 |

### Removidos por PDF identico (10)

| Titulo | Base removida | Base mantida |
|--------|---------------|--------------|
| Measuring Micro- and Macro-Impacts of Regional Development Policies | EconPapers (2x) | Scopus |
| Tax Incentives and Job Creation in the Tourism Sector of Brazil's SUDENE | EconPapers (2x) | Scopus |
| Evaluation of the Brazilian regional development funds | EconPapers | Scopus |
| Regional funding and regional inequalities in the Brazilian Northeast | EconPapers | Scopus |
| Analysis of the Northeast Constitutional Financing Fund (FNE) on Municipal | EconPapers | Scopus |
| Uma nota sobre os impactos dos incentivos fiscais no mercado de trabalho | ANPEC | SciELO |
| Efeito dose resposta do FCO (variantes de titulo) | EconPapers (2x) | EconPapers |

Total de duplicatas: 9 (fase 1) + 10 (fase 3) = 19 removidas. **118 registros unicos**.

Arquivo de auditoria fase 1: `data/1-records/processed/duplicates_removed.csv`
Arquivo de auditoria fase 3: `data/2-papers/all_papers.xlsx` (aba "Duplicatas")

## Arquivos de dados

### Arquivos integrados (todos os registros)

| Arquivo | Conteudo |
|---------|----------|
| `data/1-records/all_records.ris` | 128 registros unicos em formato RIS (para Zotero/Mendeley) |
| `data/1-records/all_records.xlsx` | 128 registros unicos + 9 duplicatas + resumo |

### Registros por base

Cada pasta contem um `.ris` integrado (com data de extracao no nome) e um `.xlsx` com os mesmos registros.

| Pasta | RIS | Excel |
|-------|-----|-------|
| `1-1-records-scopus/` | `scopus_20260225.ris` (16) | `scopus_20260225.xlsx` |
| `1-2-records-scielo/` | `scielo_20260226.ris` (5) | `scielo_20260226.xlsx` |
| `1-3-records-capes/` | `capes_20260224.ris` (30) | `capes_20260224.xlsx` |
| `1-4-records-econpapers/` | `econpapers_20260224.ris` (24) | `econpapers_20260224.xlsx` |
| `1-5-records-anpec/` | — | `anpec_20260225.xlsx` (62) |

### PDFs

Todos os PDFs foram movidos para `data/2-papers/` (sem subpastas) e renomeados com a convencao `<base>-<ano>-<sobrenome1>-<sobrenome2>-<sobrenome3>.pdf`.

Scripts de renomeacao: `data/2-papers/rename_pdfs*.py` e `rename_scopus*.py`.

| Base | Total | Baixados | Faltando | % |
|------|-------|----------|----------|---|
| Scopus | 16 | 16 | 0 | 100% |
| SciELO | 4 | 4 | 0 | 100% |
| CAPES | 26 | 26 | 0 | 100% |
| EconPapers | 11 | 11 | 0 | 100% |
| ANPEC | 61 | 61 | 0 | 100% |
| **Total** | **118** | **118** | **0** | **100%** |

Controle detalhado: `data/2-papers/all_papers.xlsx` (planilha "Registros", colunas Baixado e Arquivo PDF).

Script de verificacao: `data/2-papers/status_pdfs.py` (gera tabela resumo e lista registros faltantes).

### Dados processados

| Arquivo | Conteudo |
|---------|----------|
| `data/1-records/processed/bib_records.json` | 137 registros normalizados (BibRecord) |
| `data/1-records/processed/bib_screened.json` | Registros apos triagem |
| `data/1-records/processed/duplicates_removed.csv` | 9 duplicatas removidas (auditoria) |

## Comando de importacao

```bash
cd scripts
python main.py --verbose search \
  --import-scopus "../data/1-records/1-1-records-scopus/scopus_20260225.ris" \
  --import-scielo "../data/1-records/1-2-records-scielo/scielo_20260226.ris" \
  --import-capes "../data/1-records/1-3-records-capes/capes_20260224.ris" \
  --import-econpapers "../data/1-records/1-4-records-econpapers/econpapers_20260224.ris" \
  --import-anpec "../data/1-records/1-5-records-anpec/anpec_20260225.xlsx"
```

## Decisoes metodologicas

- **Google Scholar excluido**: retorna 12.000+ resultados com proporcao elevada de irrelevantes; periodicos relevantes ja cobertos pelo CAPES e RePEc.
- **Web of Science excluido**: cobertura ja atendida pelo CAPES e RePEc.
- **PDFs do EconPapers**: 20 de 20 baixados (100%). Um arquivo em formato .doc (Goncalves et al. 2014).
- **PDFs de Scopus**: 16 de 16 baixados (100%).
- **PDFs de CAPES**: 26 de 26 baixados (100%).
- **PDFs de SciELO**: 4 de 4 baixados (100%). Os 2 ultimos foram inicialmente classificados como "extras" e depois associados aos registros SciELO corretos.

## Trabalho pendente

1. Executar triagem pre-LLM: `python main.py screen`
3. Executar analise LLM (Stages 1-3): `python main.py analyze`
4. Exportar resultados: `python main.py export`
5. Integrar resultados no artigo LaTeX
