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
| **Inclusao manual** | | **12** | **12** | **100%** | **Concluido** |
| **Total geral** | | **130** | **130** | **100%** | **Concluido** |

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

### Removidos manualmente — versoes TD/WP e duplicatas de publicacao (9)

Identificados apos a analise de indice de citacao. Estudos que apareceram como TD/congresso E como artigo publicado em periodico, ou mirrors EconPapers de artigos ja indexados no Scopus. A versao publicada (Scopus) foi mantida; as demais foram marcadas como duplicatas.

| Titulo (abrev.) | Entrada removida | Entrada mantida | DOI |
|--------|---------------|--------------|-----|
| Efeito dose resposta do FCO em Goias | econpapers-2015 (TD IPEA 2133) | scopus-2018-oliveira-terra-resende | 10.1590/0103-6351/3397 |
| Efeito dose resposta do FCO em Goias | anpec-2015 (congresso ANPEC) | scopus-2018-oliveira-terra-resende | 10.1590/0103-6351/3397 |
| Efeito dose resposta do FCO em Goias | econpapers-2018 (mirror EconPapers) | scopus-2018-oliveira-terra-resende | 10.1590/0103-6351/3397 |
| Avaliacao dos Efeitos dos FCFs | econpapers-2015 (TD IPEA 2145) | scopus-2018-resende-silva-filho | 10.1007/s10037-018-0123-5 |
| Evaluation of Brazilian regional development funds | econpapers-2018 (mirror EconPapers) | scopus-2018-resende-silva-filho | 10.1007/s10037-018-0123-5 |
| Eficacia do gasto publico: FNE, FNO e FCO | econpapers-2007 (TD IPEA 1259) | scopus-2009-silva-resende-neto | 10.1590/s0101-41612009000100004 |
| Avaliacao economica dos fundos (FNE, FNO, FCO) | anpec-2006 (congresso ANPEC) | scopus-2009-silva-resende-neto | 10.1590/s0101-41612009000100004 |
| Eficacia do gasto publico: FNE, FNO e FCO | scielo-2009 (mesma pub., sem DOI) | scopus-2009-silva-resende-neto | 10.1590/s0101-41612009000100004 |
| Efeitos regionais do FNE (congresso ANPEC 2013) | econpapers-2014-goncalves-soares-linhares (nome alternativo) | econpapers-2014-viana-goncalves-linhares (CEPAL Review) | — |

Total de duplicatas: 9 (fases 1-2, DOI + fuzzy titulo) + 10 (fase 3, PDF identico) + 9 (fase 4, manual TD/WP) = 28 removidas. **118 papers das bases** (mantidos para consistencia com LLM) + **12 inclusoes manuais** = **130 papers na base**, **44 aprovados** apos triagem.

Arquivo de auditoria fase 1: `data/1-records/processed/duplicates_removed.csv`
Arquivo de auditoria fase 3: `data/2-papers/all_papers.xlsx` (aba "Duplicatas")
Arquivo de auditoria fase 4: `data/1-records/processed/duplicates_removed.csv` (linhas com fase=manual_td_wp)
Refs arquivadas: `data/3-ref-bib/refs_por_estudo/_archived_duplicates/`

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
| **Total (bases)** | **118** | **118** | **0** | **100%** |
| Inclusao manual | 11 | 11 | 0 | 100% |
| **Total geral** | **129** | **129** | **0** | **100%** |

Controle detalhado: `data/2-papers/all_papers.xlsx` (planilha "Registros", colunas Baixado e Arquivo PDF). Os 11 estudos manuais foram incluidos por identificacao fora das bases consultadas (snowballing a partir do indice de citacao e revisao de literatura da tese de referencia).

### Dados processados

| Arquivo | Conteudo |
|---------|----------|
| `data/1-records/processed/bib_records.json` | 137 registros normalizados (BibRecord) |
| `data/1-records/processed/bib_screened.json` | Registros apos triagem pre-LLM |
| `data/1-records/processed/duplicates_removed.csv` | 9 duplicatas removidas (auditoria) |
| `data/2-papers/_llm_checkpoint.json` | Checkpoint com resultados LLM (stages 1-3) para 118 papers |
| `data/2-papers/all_papers_llm_classif.xlsx` | Classificacao LLM bruta (gerada automaticamente) |
| `data/2-papers/all_papers_llm_classif_final.xlsx` | Classificacao LLM revisada manualmente (triagem final, somente leitura) |
| `data/2-papers/resumo_classificacao.xlsx` | Resumo estatistico gerado por `scripts/_rebuild_resumo.py` |
| `data/2-papers/2-2-papers.json` | JSON enriquecido: registros + LLM + triagem (fonte principal) |

## Analise LLM

Analise via Google Gemini (modelo `gemini-2.5-flash-lite`) em 3 estagios sequenciais, executada sobre os 118 PDFs das bases. Os 12 estudos incluidos manualmente nao passaram pela analise LLM. Script: `scripts/run_llm_all_papers.py`.

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
| APROVADO (bases) | 32 |
| APROVADO (inclusao manual) | 12 |
| REJEITADO | 86 |
| **Total** | **130** |

Motivos de rejeicao: sem instrumentos PNDR (39), sem metodo econometrico (24), documento nao-cientifico (10), duplicata de versao publicada (8), variaveis de resultado fora do escopo (3), anterior a 2005 (2). Resumo estatistico completo em `data/2-papers/resumo_classificacao.xlsx` (gerado por `scripts/_rebuild_resumo.py`).

### Alteracoes manuais em `all_papers_llm_classif_final.xlsx`

O arquivo `all_papers_llm_classif_final.xlsx` foi criado a partir de `all_papers_llm_classif.xlsx` (gerado automaticamente pelo pipeline LLM) e revisado manualmente pelo pesquisador. Sempre que `all_papers_llm_classif.xlsx` for regenerado, as alteracoes abaixo devem ser reincorporadas para produzir o `_final.xlsx` atualizado.

**Resumo:** 125 celulas alteradas em 78 registros, afetando 5 colunas.

#### 1. Triagem (35 registros: APROVADO → REJEITADO, revisao manual)

A triagem manual rejeitou 35 papers que o LLM havia aprovado (87 → 52 aprovados, 31 → 66 rejeitados):

| Arquivo PDF | Motivo Exclusao |
|-------------|-----------------|
| `anpec-2004-silva-silveira-ferreira.pdf` | sem instrumentos PNDR |
| `anpec-2005-jayme-crocco.pdf` | sem metodo econometrico |
| `anpec-2006-guanziroli.pdf` | sem metodo econometrico |
| `anpec-2008-carvalho.pdf` | sem instrumentos PNDR |
| `anpec-2010-correa-paula-oreiro.pdf` | sem instrumentos PNDR |
| `anpec-2010.pdf` | sem instrumentos PNDR |
| `anpec-2012-assuncao-ortiz-pereira.pdf` | sem instrumentos PNDR |
| `anpec-2013-artigos.pdf` | nao e estudo cientifico |
| `anpec-2013-campos-castelar.pdf` | sem instrumentos PNDR |
| `anpec-2021-okumura.pdf` | sem instrumentos PNDR |
| `anpec-2022-bastos-manso-finatti.pdf` | sem instrumentos PNDR |
| `anpec-2023-magalhaes-souza-domingues.pdf` | sem instrumentos PNDR |
| `anpec-2023-marin-griebeler.pdf` | sem instrumentos PNDR |
| `anpec-2023-shirasu.pdf` | sem metodo econometrico |
| `anpec-2024-lazaretti-davanzo-valente.pdf` | sem instrumentos PNDR |
| `anpec-2024-silva-castro.pdf` | sem instrumentos PNDR |
| `anpec-2025-premio.pdf` | nao e estudo cientifico |
| `anpec-2025-silva-chagas.pdf` | sem instrumentos PNDR |
| `anpec-nd-diniz.pdf` | sem instrumentos PNDR |
| `anpec-nd-silva-oliveira.pdf` | sem instrumentos PNDR |
| `capes-1998-rodrigues-guilhoto.pdf` | anterior a 2005 |
| `capes-2002-viola.pdf` | anterior a 2005 |
| `capes-2009-avellar.pdf` | sem instrumentos PNDR |
| `capes-2011-diniz-corrar.pdf` | sem instrumentos PNDR |
| `capes-2012-benavente-crespi-maffioli.pdf` | sem instrumentos PNDR |
| `capes-2013-vieira.pdf` | sem instrumentos PNDR |
| `capes-2015-araujo-santos-rebello.pdf` | sem metodo econometrico |
| `capes-2016-matsumoto-bittencourt-silva.pdf` | sem metodo econometrico |
| `capes-2017-macedo-pires-sampaio.pdf` | sem metodo econometrico |
| `capes-2019-yaguache-sandoval-inga.pdf` | sem instrumentos PNDR |
| `capes-2022-matias-elicker-pereira.pdf` | sem instrumentos PNDR |
| `econpapers-2022-guimaraes-queiroz-carvalho.pdf` | sem metodo econometrico |
| `scielo-2025-quaglio-lopes-heck.pdf` | sem metodo econometrico |
| `scopus-1991-binswanger.pdf` | sem metodo econometrico |
| `scopus-2015-junkes-tereso-afonso.pdf` | sem instrumentos PNDR |

#### 2. Correcao de motivo de exclusao (1 registro)

| Arquivo PDF | Motivo base | Motivo final |
|-------------|-------------|--------------|
| `anpec-2015-artigos.pdf` | LLM: sem metodo econometrico | LLM: nao e estudo cientifico |

#### 3. Correcao de instrumentos PNDR (2 registros)

| Arquivo PDF | S1_instrumentos_pndr base | S1_instrumentos_pndr final |
|-------------|---------------------------|----------------------------|
| `anpec-2024-calife-neto.pdf` | outros | FDNE |
| `anpec-2025-veloso.pdf` | outros | FDNE |

#### 4. Correcao de periodico/revista (6 registros)

| Arquivo PDF | Coluna | Valor base | Valor final |
|-------------|--------|------------|-------------|
| `anpec-2025-premio.pdf` | S1_revista | XIX Premio Banco do Nordeste de Economia Regional | Cadernos de Financas Publicas |
| `anpec-2025-premio.pdf` | Periodico | *(vazio)* | Cadernos de Financas Publicas |
| `scopus-2018-resende-silva-filho.pdf` | S1_revista | Springer-Verlag GmbH Germany, part of Springer Nature | Review of Regional Research |
| `capes-2009-avellar.pdf` | Periodico | Estudos Economicos (Sao Paulo) | Estudos Economicos |
| `econpapers-2017-oliveira-resende-oliveira.pdf` | Periodico | *(vazio)* | Revista Brasileira de Estudos Regionais e Urbanos |
| `scielo-2009-silva-resende-neto.pdf` | Periodico | Estudos Economicos (Sao Paulo) | Estudos Economicos |
| `scielo-2022-gumiero.pdf` | Periodico | Revista Brasileira de Estudos Urbanos e Regionais | Revista Brasileira de Estudos Regionais e Urbanos |
| `scopus-2009-silva-resende-neto.pdf` | Periodico | Estudos Economicos | Estudos Economicos |

#### 5. Triagem (6 registros: APROVADO → REJEITADO, duplicata de versao publicada)

Versoes TD/congresso do mesmo trabalho publicado em periodico, marcadas como REJEITADO com motivo "duplicata de versao publicada" (52 → 45 aprovados, 66 → 73 rejeitados):

| Arquivo PDF | Versao publicada mantida |
|-------------|-------------------------|
| `econpapers-2015-oliveira-terra-resende.pdf` | `scopus-2018-oliveira-terra-resende.pdf` |
| `anpec-2015-oliveira-terra-resende.pdf` | `scopus-2018-oliveira-terra-resende.pdf` |
| `econpapers-2015-resende-silva-filho.pdf` | `scopus-2018-resende-silva-filho.pdf` |
| `econpapers-2007-silva-resende-neto.pdf` | `scopus-2009-silva-resende-neto.pdf` |
| `anpec-2006-silva-resende-neto.pdf` | `scopus-2009-silva-resende-neto.pdf` |
| `scielo-2009-silva-resende-neto.pdf` | `scopus-2009-silva-resende-neto.pdf` |
| `econpapers-2014-goncalves-soares-linhares.pdf` | `econpapers-2014-viana-goncalves-linhares.pdf` |

#### 6. Correcao de tipo de publicacao (20 registros ANPEC: artigo publicado → apresentacao em congresso)

O LLM classificou 20 apresentacoes em congresso ANPEC como `"artigo publicado"` em `S1_tipo_trabalho`. Todos tinham `S1_revista = "[ne]"` (nao encontrada). Correcao manual: `S1_tipo_trabalho` alterado para `"apresentação em congresso"`.

IDs corrigidos: 65, 80, 82, 84, 86, 88, 90, 94, 99, 100, 102, 104, 105, 106, 107, 108, 113, 114, 115, 116.

#### 7. Correcao de periodico faltante (3 registros EconPapers)

O LLM identificou a revista em `S1_revista`, mas o nome nao foi transferido para a coluna `Periodico`. Correcao manual:

| Arquivo PDF | Periodico (corrigido) |
|-------------|----------------------|
| `econpapers-2014-viana-goncalves-linhares.pdf` | CEPAL Review |
| `econpapers-2014-resende-cravo-pires.pdf` | Revista de Economia do Centro-Oeste |
| `econpapers-2016-sousa-damasceno-vieira.pdf` | Revista Brasileira de Estudos Regionais e Urbanos |

#### 8. Triagem (1 registro: APROVADO → REJEITADO, duplicata de versao publicada)

Versao congresso ANPEC 2013 do mesmo trabalho publicado na CEPAL Review (Viana et al., 2014):

| Arquivo PDF | Versao publicada mantida |
|-------------|-------------------------|
| `econpapers-2014-goncalves-soares-linhares.pdf` | `econpapers-2014-viana-goncalves-linhares.pdf` |

Contagem apos secao 8: 45 aprovados, 73 rejeitados.

#### 9. Triagem (5 registros: APROVADO → REJEITADO, revisao manual pos-analise)

Revisao manual adicional apos analise de instrumentos e metodos:

| Arquivo PDF | Motivo Exclusao | Justificativa |
|-------------|-----------------|---------------|
| `capes-2009-nascimento-lima.pdf` | sem metodo econometrico | Usa metodo Shift-Share (decomposicao contabil), nao econometria |
| `capes-2008-paes-siqueira.pdf` | fora do escopo | CGE para reforma fiscal visando equidade regional; nao avalia efeitos dos instrumentos PNDR |
| `scielo-2022-gumiero.pdf` | sem metodo econometrico | Analise qualitativa de documentos institucionais sobre FNO/FDA em Carajas |
| `anpec-2021-bezerra-ramos.pdf` | sem instrumentos PNDR | Analise de controle sintetico para energia eolica no semiarido; nao avalia instrumentos PNDR |
| `capes-2007-porsse-haddad-ribeiro.pdf` | sem instrumentos PNDR | EGC para incentivos fiscais regionais genericos (Sudene/Sudam/Sudeco); nao avalia instrumentos especificos da PNDR |

Contagem apos secao 9: 40 aprovados, 78 rejeitados.

#### 10. Triagem (2 registros: APROVADO → REJEITADO, revisao manual pos-analise)

Revisao manual adicional apos verificacao de instrumentos e metodos:

| Arquivo PDF | Motivo Exclusao | Justificativa |
|-------------|-----------------|---------------|
| `anpec-2025-silva-chagas-azzoni.pdf` | sem instrumentos PNDR | Avalia impacto de energia eolica no emprego via incentivos Sudene, sem instrumentos especificos da PNDR |
| `anpec-2024-calife-neto.pdf` | sem instrumentos PNDR | Avalia impacto da industria automotiva em Goiana-PE via FDNE; FDNE isolado nao configura instrumento especifico da PNDR |

Contagem apos secao 10: 38 aprovados, 80 rejeitados.

#### 11. Triagem (2 registros: APROVADO → REJEITADO, revisao manual pos-analise)

Revisao manual adicional apos verificacao de metodos e variaveis de resultado:

| Arquivo PDF | Motivo Exclusao | Justificativa |
|-------------|-----------------|---------------|
| `anpec-2024-quaglio.pdf` | sem metodo econometrico | Analise espacial descritiva do FNE no Pronaf; nao aplica metodo econometrico |
| `scopus-2012-abreu-gomes-mello.pdf` | outras variaveis de resultado | Avalia retencao de novilhas no Pantanal via DEA e indice Malmquist; variaveis de resultado fora do escopo da PNDR |

Contagem apos secao 11: 34 aprovados, 84 rejeitados.

#### 12. Triagem (1 registro: APROVADO → REJEITADO, revisao manual pos-analise)

Revisao manual adicional apos verificacao de escopo:

| Arquivo PDF | Motivo Exclusao | Justificativa |
|-------------|-----------------|---------------|
| `scopus-2025-borges-rodrigues.pdf` | fora do escopo | Avalia distribuicao da oferta de credito rural do FCO, nao o efeito do instrumento sobre o crescimento regional |

Contagem final (bases): 32 aprovados, 86 rejeitados. Com inclusao manual: **43 aprovados**, 86 rejeitados, **129 total**.

## Consolidacao JSON enriquecido

Script: `scripts/merge_papers_to_json.py`

Mescla tres fontes em um unico JSON (`data/2-papers/2-2-papers.json`):

1. `all_papers_llm_classif_final.xlsx` — triagem + classificacao LLM (S1/S2/S3)
2. `all_papers.xlsx` — URL, resumo, tipo, palavras-chave
3. `bib_records.json` — metadados completos das bases (abstract, volume, issue, pages, idioma)

Para campos duplicados, prioridade: registros das bases > all_papers > LLM.

Resultado: 129 papers com campos unificados (43 aprovados — 32 das bases + 11 inclusao manual —, 86 rejeitados), incluindo: metadados bibliograficos, resumo, palavras-chave, classificacao LLM em 3 stages, resultado da triagem e motivo de exclusao.

## Extracao e matching de referencias

### Extracao de referencias

Scripts: `data/3-ref-bib/extrair_referencias.py` e `estruturar_referencias.py`

Para os estudos aprovados (incluindo os estudos manuais), as listas de referencias bibliograficas foram extraidas dos PDFs via Gemini e estruturadas em JSON com campos: raw, autor, titulo, ano, periodico, volume, issue, pages. Apos a remocao de 7 estudos duplicados (versoes TD/congresso) e 5 estudos rejeitados em revisao posterior, restam 50 JSONs ativos (43 com referencias extraidas + 7 sem referencias); os 12 removidos foram arquivados em `refs_por_estudo/_archived_duplicates/`.

Resultado: 50 JSONs ativos em `data/3-ref-bib/refs_por_estudo/`.

### Matching de citacoes entre estudos

Script: `scripts/match_refs_to_studies.py`

Para cada referencia de cada estudo, verifica se corresponde a outro estudo presente na lista de 129 papers (triagem). O matching usa:

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

Resultado: **120 citacoes cruzadas** encontradas em **29 dos 50 arquivos** de referencias.

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

**Estudos com versao TD e versao publicada — resolvidos como duplicatas:**

Tres grupos de estudos foram identificados como duplicatas verdadeiras: o mesmo trabalho publicado em estagios diferentes (congresso → TD → periodico). As versoes nao-publicadas foram marcadas como duplicatas e removidas do dataset ativo. Apenas a versao publicada em periodico (Scopus) permanece.

| Versoes removidas (duplicatas) | Versao mantida (publicada) |
|---|---|
| `econpapers-2015-oliveira-terra-resende` (TD IPEA 2133) + `anpec-2015-oliveira-terra-resende` (congresso) | `scopus-2018-oliveira-terra-resende` (DOI 10.1590/0103-6351/3397) |
| `econpapers-2015-resende-silva-filho` (TD IPEA 2145) | `scopus-2018-resende-silva-filho` (DOI 10.1007/s10037-018-0123-5) |
| `anpec-2006-silva-resende-neto` (congresso) + `econpapers-2007-silva-resende-neto` (TD IPEA 1259) + `scielo-2009-silva-resende-neto` (pub. sem DOI) | `scopus-2009-silva-resende-neto` (DOI 10.1590/s0101-41612009000100004) |
| `econpapers-2014-goncalves-soares-linhares` (congresso ANPEC 2013) | `econpapers-2014-viana-goncalves-linhares` (CEPAL Review) |

Script de marcacao: `scripts/mark_td_duplicates.py`

**Resultados:** 43 estudos aprovados (21 publicados, 22 nao-publicados), **142 citacoes cruzadas**. IC calculado para todos os 43 estudos.

Saidas:
- `data/3-ref-bib/citation_index_results.json` — dados completos por estudo
- `data/3-ref-bib/citation_index_report.txt` — relatorio com ranking e citacoes detalhadas

## Geracao de tabelas derivadas para o artigo

Script: `scripts/generate_latex_tables.py`

Regenera automaticamente as tabelas derivadas do artigo LaTeX a partir dos dados consolidados em `2-2-papers.json`:

- **tab:estudos-ano** — Distribuicao temporal dos estudos aprovados por periodo (2005-2010, 2011-2015, 2016-2020, 2021-2026)
- **tab:instrumentos** — Frequencia de mencoes a cada instrumento da PNDR (FNE, FNO, FCO, FDNE, FDA, FDCO, IF Sudene, IF Sudam, BNDES)
- **tab:autores-todos** — Top-10 autores por autorias e coautorias
- **tab:unidade-amostral** — Unidades de analise (Municipio, Empresa, UF, Area Minima Comparavel)
- **tab:metodos** — Metodos econometricos mais frequentes (top-6) com classificacao MSM

O script aplica normalizacao automatica:
- **Instrumentos:** Remove referencias de pagina, unifica variantes (ex: "incentivo fiscal Sudene" → "IF -- Sudene")
- **Autores:** Preserva formato "Sobrenome, Iniciais" conforme campo `autores` do JSON
- **Unidades:** Normaliza variantes (ex: "municipio"/"municipal" → "Municipio", "empresa"/"firma" → "Empresa")
- **Metodos:** Unifica variantes de nomes (ex: "DiD"/"Diferencas em Diferencas" → "Diferencas em Diferencas (DiD)")

Uso:
```bash
cd scripts
python generate_latex_tables.py > ../latex/tabelas_geradas.tex
```

Saida: Fragmentos LaTeX prontos para insercao em `3-metodo.tex`.

**Nota:** Este script deve ser executado sempre que houver mudancas nos estudos aprovados (ex: adicao/remocao de estudos, correcoes em metadados LLM).

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
