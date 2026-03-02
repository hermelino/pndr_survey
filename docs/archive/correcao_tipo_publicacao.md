# Correção: Tipo de publicação dos artigos aprovados

**Data:** 2026-02-28
**Arquivo:** `data/2-papers/all_papers_llm_classif_final.xlsx`, aba "Classificação LLM"

## Problema

A aba "Resumo" contabiliza **47 artigos publicados em periódico** entre os 46 aprovados. Porém, **24 desses não possuem periódico** na coluna "Periodico" (col G). A causa raiz é que o LLM classificou apresentações em congresso ANPEC como `"artigo publicado"` em `S1_tipo_trabalho`.

## Diagnóstico

### Grupo A — 20 artigos ANPEC (reclassificar)

Estes artigos são **apresentações no Encontro ANPEC**, não publicações em periódico. O LLM errou ao classificá-los como `"artigo publicado"`. Todos têm `S1_revista = "[ne]"`.

**Correção:** Alterar `S1_tipo_trabalho` para `"apresentação em congresso"`.

| ID | S1_tipo_trabalho (atual) | Título (resumido) |
|----|--------------------------|-------------------|
| 65 | artigo publicado | Considerações sobre o impacto dos fundos constitucionais |
| 80 | artigo publicado | Análise do Fundo Constitucional de Financiamento do... |
| 82 | artigo publicado | Efeitos não lineares dos fundos constitucionais de... |
| 84 | artigo publicado | Incentivos Fiscais Territoriais ao Desenvolvimento Local |
| 86 | artigo publicado | Os ventos que geram energia também... |
| 88 | artigo publicado [impl.] | Uma Avaliação do Fundo Constitucional de Financiamento... |
| 90 | artigo publicado | Avaliação de eficiência das empresas... |
| 94 | artigo publicado | Impactos dos incentivos... |
| 99 | artigo publicado | Incentivos Fiscais Estaduais: Desenvolvimento ou Captura... |
| 100 | artigo publicado | More GDP and Revenue, but no Social Development?... |
| 102 | artigo publicado | Análise do impacto dos instrumentos da PNDR sobre... |
| 104 | artigo publicado [impl.] | Credit and municipal agricultural production in the... |
| 105 | artigo publicado | Impactos do financiamento empresarial via FDNE sobre... |
| 106 | artigo publicado | Análise Espacial do Fundo... |
| 107 | artigo publicado [impl.] | Área 10 - economia regional e urbana |
| 108 | artigo publicado | Como os parques eólicos afetam a... |
| 113 | artigo publicado | XXX Encontro Regional de Economia Área 3 |
| 114 | artigo publicado [impl.] | Avaliação do impacto da consultoria SEBRAE e do crédito do... |
| 115 | artigo publicado | Efeitos dinâmicos dos instrumentos da PNDR sobre... |
| 116 | artigo publicado | Energia eólica e emprego: evidências da expansão dos... |

### Grupo B — 3 artigos EconPapers (preencher periódico)

Estes **são** artigos em periódico — o LLM identificou a revista em `S1_revista`, mas o nome não foi transferido para a coluna "Periodico".

**Correção:** Copiar o nome da revista para a coluna "Periodico" (col G).

| ID | S1_revista (LLM) | Periodico (corrigido) |
|----|-------------------|-----------------------|
| 51 | CEPAL REVIEW [p. 176] | CEPAL Review |
| 53 | Rev. Econ. do Centro-Oeste [p. 2] | Revista de Economia do Centro-Oeste |
| 57 | Revista Brasileira de Estudos Regionais e Urbanos | Revista Brasileira de Estudos Regionais e Urbanos |

### Grupo C — 1 artigo EconPapers (investigar)

| ID | S1_tipo_trabalho | S1_revista | Título |
|----|------------------|------------|--------|
| 37 | artigo publicado | [ne] | Efeitos diferenciados do FNE |

**Ação:** Verificar o PDF para determinar se é artigo publicado em periódico ou texto para discussão. Se for TD, alterar `S1_tipo_trabalho` para `"texto para discussão"`.

## Resultado esperado após correções

| Tipo de publicação | Antes | Depois |
|--------------------|-------|--------|
| Artigo publicado em periódico | ~43 | ~23 |
| Apresentação em congresso | 2 | 22 |
| Texto para discussão | 1 | 1–2 |

## Execução (2026-02-28)

Todas as correções foram aplicadas e propagadas:

1. **Correções manuais no Excel** — Grupos A, B e C aplicados pelo pesquisador
2. **Grupo C (ID 37)** — Identificado como duplicata de versão publicada (ID 51, CEPAL Review). Marcado como REJEITADO no Excel e como `is_duplicate` em `bib_records.json` / `bib_screened.json`
3. **bib_records / bib_screened** — Record "Goncalves et al. ANPEC 2013" marcado como duplicata de "Viana et al. 2014 CEPAL Review"
4. **duplicates_removed.csv** — Entrada adicionada (fase `manual_td_wp`)
5. **Refs arquivadas** — `econpapers-2014-goncalves-soares-linhares_refs.*` movidos para `_archived_duplicates/`
6. **update_resumo.py** — Aba Resumo regenerada (45 aprovados, 73 rejeitados)
7. **merge_papers_to_json.py** — `2-2-papers.json` atualizado
8. **citation_index.py** — Recalculado (47 estudos, 23 pub., 24 não-pub., 118 citações cruzadas)
9. **pipeline_extraction.md** — Documentação atualizada
