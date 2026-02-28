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

Todos os PDFs estao em `data/2-papers/2-2-papers-pdfs/` e renomeados com a convencao `<base>-<ano>-<sobrenome1>-<sobrenome2>-<sobrenome3>.pdf`.

Scripts de renomeacao e verificacao: `data/2-papers/2-1-papers_scripts/`.

| Base | Total | Baixados | Faltando | % |
|------|-------|----------|----------|---|
| Scopus | 16 | 16 | 0 | 100% |
| SciELO | 4 | 4 | 0 | 100% |
| CAPES | 26 | 26 | 0 | 100% |
| EconPapers | 11 | 11 | 0 | 100% |
| ANPEC | 61 | 61 | 0 | 100% |
| **Total** | **118** | **118** | **0** | **100%** |

Controle detalhado: `data/2-papers/all_papers.xlsx` (planilha "Registros", colunas Baixado e Arquivo PDF).

### Dados processados

| Arquivo | Conteudo |
|---------|----------|
| `data/1-records/processed/bib_records.json` | 137 registros normalizados (BibRecord) |
| `data/1-records/processed/bib_screened.json` | Registros apos triagem pre-LLM |
| `data/1-records/processed/duplicates_removed.csv` | 9 duplicatas removidas (auditoria) |
| `data/2-papers/_llm_checkpoint.json` | Checkpoint com resultados LLM (stages 1-3) para 118 papers |
| `data/2-papers/all_papers_llm_classif.xlsx` | Classificacao LLM bruta (gerada automaticamente) |
| `data/2-papers/all_papers_llm_classif_final.xlsx` | Classificacao LLM revisada manualmente a partir de `all_papers_llm_classif.xlsx` (triagem final) |
| `data/2-papers/2-2-papers.json` | JSON enriquecido: registros + LLM + triagem (fonte principal) |

## Analise LLM

Analise via Google Gemini (modelo `gemini-2.0-flash`) em 3 estagios sequenciais, executada sobre os 118 PDFs coletados. Script: `scripts/run_llm_all_papers.py`.

### Stage 1 — Triagem

Identifica se o paper e estudo empirico sobre instrumentos da PNDR. Campos extraidos: tipo de trabalho, revista, titulo, autores, ano, instrumentos PNDR, metodologia, uso de econometria, questao-chave.

### Stage 2 — Metodologia

Extrai detalhes metodologicos: metodo econometrico, tipo de dados, variaveis dependentes e de controle, setor economico, area geografica, unidade de tempo/espaco, periodo amostral.

### Stage 3 — Resultados

Extrai resultados: efeito parcial, significancia, direcao do efeito, outros resultados, implicacoes, limitacoes, sugestoes.

### Triagem final

Apos a analise LLM, triagem manual em `all_papers_llm_classif_final.xlsx`:

| Resultado | Quantidade |
|-----------|-----------|
| APROVADO | 53 |
| REJEITADO | 65 |
| **Total** | **118** |

Motivos de rejeicao: sem metodo econometrico, anterior a 2005, sem instrumentos PNDR, artigo fora do escopo, documento nao-cientifico.

## Consolidacao JSON enriquecido

Script: `scripts/merge_papers_to_json.py`

Mescla tres fontes em um unico JSON (`data/2-papers/2-2-papers.json`):

1. `all_papers_llm_classif_final.xlsx` — triagem + classificacao LLM (S1/S2/S3)
2. `all_papers.xlsx` — URL, resumo, tipo, palavras-chave
3. `bib_records.json` — metadados completos das bases (abstract, volume, issue, pages, idioma)

Para campos duplicados, prioridade: registros das bases > all_papers > LLM.

Resultado: 118 papers com campos unificados, incluindo: metadados bibliograficos, resumo, palavras-chave, classificacao LLM em 3 stages, resultado da triagem e motivo de exclusao.

## Extracao e matching de referencias

### Extracao de referencias

Scripts: `data/3-ref-bib/extrair_referencias.py` e `estruturar_referencias.py`

Para 54 dos estudos aprovados, as listas de referencias bibliograficas foram extraidas dos PDFs via Gemini e estruturadas em JSON com campos: raw, autor, titulo, ano, periodico, volume, issue, pages.

Resultado: 54 JSONs em `data/3-ref-bib/refs_por_estudo/`, totalizando 1.410 referencias.

### Matching de citacoes entre estudos

Script: `scripts/match_refs_to_studies.py`

Para cada referencia de cada estudo, verifica se corresponde a outro estudo presente na lista de 118 papers (triagem). O matching usa:

1. **Filtro por ano** — duas faixas de tolerancia:
   - Anos iguais: threshold >= 75% (`FUZZY_THRESHOLD`)
   - Anos diferentes (±6 anos): threshold >= 90% (`YEAR_FLEX_THRESHOLD`), captura working papers citados pelo ano de publicacao diferente
2. **Similaridade de titulo** — `rapidfuzz.token_sort_ratio`, comparando com titulo do registro E titulo extraido pelo LLM (S1)
3. **Verificacao de sobrenomes** — pelo menos 1 sobrenome em comum (normalizado via unidecode), com fallback fuzzy (ratio >= 85%)
4. **Auto-exclusao** — nao marca o proprio estudo citante como match

Campos adicionados a cada referencia nos JSONs:

| Campo | Tipo | Descricao |
|-------|------|-----------|
| `cita_estudo_aprovado` | bool | True se match encontrado |
| `estudo_citado_pdf` | str/null | Arquivo PDF do estudo citado |
| `match_score` | float/null | Score do token_sort_ratio (75-100) |

Resultado: **80 citacoes cruzadas** encontradas em **23 dos 54 arquivos** de referencias.

### Indice de citacao (IC)

Script: `scripts/citation_index.py`

Calcula um indice de citacao para cada estudo, medindo a importancia que a literatura publicada atribui aos artigos nao-publicados (textos para discussao, apresentacoes em congresso). Usado como criterio para inclusao de artigos nao-publicados na revisao sistematica.

**Formula:**

```
IC(A) = citacoes recebidas de artigos publicados em [X+1, 2025]
        / total de artigos publicados em [X+1, 2025]

onde X = ano do artigo A
```

**Metodologia de matching (independente do match_refs_to_studies.py):**

1. **Matching por autor** — extrai sobrenomes do filename e compara com campo `autor` das referencias (normalizados via unidecode)
2. **Matching por ano** — tolerancia de ±2 anos (captura working papers citados pelo ano de publicacao)
3. **Matching por titulo** — similaridade de palavras-chave entre titulo do estudo e titulo/raw da referencia
4. **Restricao cronologica** — estudo citante deve ser do mesmo ano ou posterior ao estudo citado
5. **Penalizacao single-author** — autores unicos (ex: "Resende") exigem evidencia de titulo para evitar falsos positivos

**Classificacao publicado/nao-publicado:**

| Fonte | Classificacao | Justificativa |
|-------|---------------|---------------|
| scopus | Publicado | Periodicos indexados |
| scielo | Publicado | Periodicos indexados |
| capes | Publicado | Periodicos CAPES (todos tem journal) |
| anpec | Nao publicado | Apresentacoes em congresso |
| econpapers | Manual | TDs/WPs = nao publicado; artigos em periodico = publicado |

**Estudos com versao TD e versao publicada (mesmo trabalho, entradas distintas):**

Alguns estudos aparecem mais de uma vez no dataset porque foram primeiro divulgados como texto para discussao (TD) ou apresentacao em congresso e depois publicados em periodico. Eles nao sao duplicatas no sentido estrito (titulos e anos diferem), mas representam o mesmo trabalho em estagios diferentes. O pipeline os mantem como entradas separadas, pois vieram de bases diferentes e passaram na deduplicacao. Para fins do IC, a versao publicada e a que conta como "publicado"; a versao TD/congresso e classificada como "nao publicado".

| Versao nao-publicada | Versao publicada | Observacao |
|----------------------|------------------|------------|
| `econpapers-2015-oliveira-terra-resende` (TD, 2015) | `scopus-2018-oliveira-terra-resende` (periodico, 2018) | Mesmo estudo; TD do IPEA publicado posteriormente |
| `econpapers-2015-resende-silva-filho` (TD, 2015) | `scopus-2018-resende-silva-filho` (periodico, 2018) | Mesmo estudo; IPEA TD 2145 publicado posteriormente |
| `anpec-2006-silva-resende-neto` (congresso, 2006) + `econpapers-2007-silva-resende-neto` (TD, 2007) | `scielo-2009-silva-resende-neto` + `scopus-2009-silva-resende-neto` (periodico, 2009) | Mesmo estudo em 4 versoes (congresso → TD → periodico); scielo e scopus sao a mesma publicacao |

**Resultados:** 54 estudos (24 publicados, 30 nao-publicados), **141 citacoes cruzadas**, **13 artigos nao-publicados com IC > 0**.

Saidas:
- `data/3-ref-bib/citation_index_results.json` — dados completos por estudo
- `data/3-ref-bib/citation_index_report.txt` — relatorio com ranking e citacoes detalhadas

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
- **Analise LLM**: modelo Gemini 2.0 Flash, questionarios em 3 stages (`scripts/questionnaires/`). Checkpoint salvo em `_llm_checkpoint.json` para retomada.
- **Matching de citacoes**: duas faixas — threshold 75% para anos iguais, 90% para anos diferentes (±6), combinado com verificacao de sobrenomes. Captura working papers citados pelo ano de publicacao final.

## Trabalho pendente

1. Integrar resultados no artigo LaTeX
2. Gerar figuras de analise (rede de citacoes, distribuicao temporal, etc.)
