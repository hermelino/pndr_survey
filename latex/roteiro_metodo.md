# Roteiro — Seção 3: Método

Data de elaboração: 2026-02-28

---

## 3.1 Estratégia de busca e seleção (PRISMA 2020)

> **Descrição:** Apresentar o objetivo da revisão sistemática (avaliar estudos empíricos com abordagem econométrica sobre instrumentos da PNDR), justificar a adoção do protocolo PRISMA 2020 e descrever o fluxo geral de busca, triagem e seleção.
> **Fonte na tese:** `1-3-metodo.tex`, linhas 7–23
> **Adaptações necessárias:** `[REESCREVER]` Texto mais conciso e direto, adaptado a formato de artigo. Atualizar referência ao PRISMA com números do novo pipeline (5 bases, 128 registros brutos, 118 após dedup fase 1, 45 aprovados).

[DIAGRAMA] Diagrama 1: Fluxo PRISMA 2020
- Fonte: `figuras/1-survey/diagrama_prisma.tex` (tese) — a ser refeito
- Descrição: Fluxo de identificação, triagem, elegibilidade e inclusão dos estudos
- Adaptação: `[REESCREVER]` Refazer com números atualizados: 5 bases → 128 registros brutos → dedup (28 removidas em 4 fases) → 118 únicos → triagem LLM + manual → 45 aprovados, 73 rejeitados

---

## 3.2 Bases de dados consultadas

> **Descrição:** Descrever cada uma das 5 bases de busca (Scopus, SciELO, Portal CAPES, EconPapers/RePEc, ANPEC), com os respectivos procedimentos de coleta e número de registros obtidos. Justificar a escolha dessas bases e a exclusão de Google Scholar e Web of Science.
> **Fonte na tese:** `1-3-metodo.tex`, linhas 9, 27–32
> **Adaptações necessárias:** `[NOVO]` A tese usava 3 bases (ANPEC, CAPES, RePEc); o artigo usa 5 (adição de Scopus e SciELO). Reescrever integralmente com base em `pipeline_extraction.md`.

[TABELA] Tabela 1: Bases de dados, procedimentos e registros obtidos
- Fonte: `pipeline_extraction.md` (seções "Visao geral" e "Metodo de coleta por base")
- Descrição: Tabela com 5 linhas (Scopus: 16, SciELO: 4, CAPES: 26, EconPapers: 11, ANPEC: 61) + total (118 após dedup)
- Adaptação: `[NOVO]` Elemento inexistente na tese

---

## 3.3 Expressões de busca e critérios de inclusão/exclusão

> **Descrição:** Detalhar a estratégia de busca (3 blocos booleanos: instrumentos, organizações, geografia), com variações por base. Apresentar os critérios de inclusão (estudo empírico + instrumento PNDR + método econométrico) e exclusão (sem PNDR, apenas qualitativo, sem econometria, anterior a 2005).
> **Fonte na tese:** `1-3-metodo.tex`, linhas 22–26
> **Adaptações necessárias:** `[REESCREVER]` Atualizar as queries conforme `pipeline_extraction.md` (seção "Estrategia de busca"). Adicionar "anterior a 2005" como critério de exclusão explícito, e "duplicata de versão publicada". Manter os 3 critérios originais (a, b, c) e adicionar (d) e (e).

[QUADRO] Quadro 1: Expressões de busca por base
- Fonte: `pipeline_extraction.md` (seção "Estrategia de busca") e `scripts/keywords/`
- Descrição: Query exata usada em cada base (Scopus com TITLE-ABS-KEY, ANPEC via Google site:, etc.)
- Adaptação: `[NOVO]` Na tese, a query era apresentada em nota de rodapé; no artigo, merece quadro próprio

---

## 3.4 Processo de deduplicação `[NOVO]`

> **Descrição:** Descrever o algoritmo de deduplicação em 4 fases: (1) DOI exato — 5 removidas; (2) título fuzzy (token_sort_ratio ≥ 80%) — 4 removidas; (3) PDF idêntico — 10 removidas; (4) manual TD/WP (versões duplicadas de trabalhos publicados) — 9 removidas. Total: 28 duplicatas removidas. Explicar a prioridade de retenção (Scopus > SciELO > CAPES > EconPapers > ANPEC).
> **Fonte na tese:** Não descrito
> **Adaptações necessárias:** `[NOVO]` Seção inteiramente nova. Dados em `pipeline_extraction.md` (seção "Deduplicacao").

[TABELA] Tabela 2: Duplicatas removidas por fase
- Fonte: `pipeline_extraction.md` + `data/1-records/processed/duplicates_removed.csv`
- Descrição: 4 fases × quantidade removida, com exemplos representativos
- Adaptação: `[NOVO]`

`[NOTA]` A fase 4 (manual TD/WP) foi realizada após a análise de índice de citação, quando se identificou que 9 entradas correspondiam a versões working paper/congresso de artigos já publicados em periódicos. A versão publicada (Scopus ou EconPapers/periódico) foi mantida.

---

## 3.5 Análise assistida por LLM `[NÃO INCLUIR]`

> **Descrição:** Descrever o pipeline de classificação automatizada via Gemini 2.0 Flash em 3 estágios sequenciais, aplicado aos 118 PDFs. Stage 1 (Triagem): identifica tipo de trabalho, instrumentos PNDR, uso de econometria. Stage 2 (Metodologia): extrai método econométrico, variáveis, amostra. Stage 3 (Resultados): extrai efeitos parciais, significância, direção. Descrever o papel do LLM como assistente (não como decisor) e a revisão manual subsequente.
> **Fonte na tese:** Não existe
> **Adaptações necessárias:** `[NOVO]` Seção inteiramente nova. Dados nos questionários (`scripts/questionnaires/stage_1_screening.json`, `stage_2_methods.json`, `stage_3_results.json`) e em `pipeline_extraction.md` (seção "Analise LLM").

[DIAGRAMA] Diagrama 2: Pipeline de classificação LLM
- Fonte: A criar
- Descrição: Fluxo: PDF → extração de texto → Stage 1 (triagem) → Stage 2 (metodologia) → Stage 3 (resultados) → triagem manual
- Adaptação: `[NOVO]`

[QUADRO] Quadro 2: Campos extraídos por estágio do LLM
- Fonte: `scripts/questionnaires/stage_*.json`
- Descrição: Para cada estágio, listar os campos extraídos (Stage 1: 9 campos; Stage 2: 10 campos; Stage 3: 7 campos)
- Adaptação: `[NOVO]`

---

## 3.6 Triagem final `[NOVO]`

> **Descrição:** Descrever o processo de triagem final combinando resultado do LLM (Stage 1) com revisão manual do pesquisador. Apresentar os números: de 118 registros, 45 aprovados e 73 rejeitados. Detalhar os motivos de rejeição: sem instrumentos PNDR (35), sem método econométrico (17), não é estudo científico (10), anterior a 2005 (2), duplicata de versão publicada (7), outros (2). Destacar que a revisão manual rejeitou 35 papers que o LLM havia aprovado (taxa de correção de ~40%).
> **Fonte na tese:** `1-3-metodo.tex`, linhas 26 (parcial — na tese era 37 aprovados com fluxo diferente)
> **Adaptações necessárias:** `[REESCREVER]` Números completamente diferentes (45 vs. 37). Processo de triagem novo (LLM + manual vs. apenas manual).

[TABELA] Tabela 3: Resultado da triagem final
- Fonte: `data/2-papers/2-2-papers.json` (campo `triagem` e `motivo_exclusao`)
- Descrição: Tabela com motivos de rejeição e quantidades
- Adaptação: `[NOVO]`

---

## 3.7 Índice de citação (IC) `[NÃO INCLUIR]`

> **Descrição:** Apresentar o índice de citação como ferramenta para medir a relevância dos estudos não publicados dentro da rede de literatura sobre PNDR. Fórmula: IC(A) = citações recebidas de artigos publicados em [X+1, 2025] / total de artigos publicados em [X+1, 2025]. Descrever a metodologia de matching (autor + ano + título, com tolerância) e a classificação publicado/não-publicado por base. Apresentar ranking dos principais estudos e destacar que 8 dos 23 artigos não publicados possuem IC > 0.
> **Fonte na tese:** Não existe
> **Adaptações necessárias:** `[NOVO]` Seção inteiramente nova. Dados em `citation_index_report.txt` e `citation_index_results.json`.

[TABELA] Tabela 4: Ranking dos estudos por índice de citação (top 10–15)
- Fonte: `data/3-ref-bib/citation_index_report.txt`
- Descrição: Estudo, ano, publicado?, citações, N, IC, tipo
- Adaptação: `[NOVO]`

[EQUAÇÃO] Fórmula do IC
- Descrição: IC(A) = citações de publicados em [X+1, 2025] / total de publicados em [X+1, 2025]

`[NOTA]` O IC foi utilizado como critério complementar para validar a inclusão de estudos não publicados (TDs e apresentações em congresso). Estudos não publicados sem citações de artigos publicados podem indicar menor impacto acadêmico, mas não são excluídos automaticamente — a decisão de inclusão baseia-se nos critérios substantivos (seção 3.3).

---

## 3.8 Descrição dos estudos obtidos

> **Descrição:** Caracterizar a amostra final de 45 estudos (2005–2025): distribuição temporal, tipo de publicação (22 publicados em periódicos, 23 não publicados — TDs e congressos), autores mais recorrentes, panorama metodológico (escala MSM), distribuição por instrumento avaliado (FC, FD, IF). Incluir mapa de distribuição da literatura.
> **Fonte na tese:** `1-3-metodo.tex`, linhas 34–60
> **Adaptações necessárias:** `[REESCREVER]` Atualizar todos os números (37→45, 18 publicados→22, etc.). Adaptar distribuição temporal. Manter escala MSM mas atualizar contagens de métodos.

[FIGURA] Figura 1: Mapa de distribuição dos artigos (litmap)
- Fonte: `figuras/1-survey/litmap_0910.png` (tese)
- Descrição: Mapa visual da distribuição da literatura
- Adaptação: `[REESCREVER]` Refazer com 45 estudos e dados atualizados

`[REMOVER]` Detalhamento excessivo da escala MSM (parágrafos sobre escore 5 e aleatoriedade, que ocupam espaço desproporcional no formato artigo). Manter apenas parágrafo-síntese do panorama metodológico.

---

## Resumo das diferenças tese → artigo (seção Método)

| Aspecto | Tese (Cap. 1) | Artigo (pndr_survey) |
|---------|---------------|---------------------|
| Bases de busca | 3 (ANPEC, CAPES, RePEc) | 5 (Scopus, SciELO, CAPES, EconPapers, ANPEC) |
| Registros coletados | ~135 | 128 brutos → 118 após dedup fase 1 |
| Estudos aprovados | 37 | 45 |
| Deduplicação | Não descrita | 4 fases (28 removidas) |
| Classificação | Manual | LLM-assistida (Gemini 2.0 Flash, 3 estágios) + revisão manual |
| Índice de citação | Não disponível | IC calculado para 45 estudos (118 citações) |
| Subseções novas | — | 3.4, 3.5, 3.6, 3.7 (todas `[NOVO]`) |

---

## Inventário de elementos não textuais

| # | Tipo | Título | Status |
|---|------|--------|--------|
| 1 | DIAGRAMA | Fluxo PRISMA 2020 | `[REESCREVER]` com números atualizados |
| 2 | TABELA | Bases de dados e registros | `[NOVO]` |
| 3 | QUADRO | Expressões de busca por base | `[NOVO]` |
| 4 | TABELA | Duplicatas removidas por fase | `[NOVO]` |
| 5 | DIAGRAMA | Pipeline de classificação LLM | `[NÃO INCLUIR]` a criar |
| 6 | QUADRO | Campos extraídos por estágio LLM | `[NÃO INCLUIR]` |
| 7 | TABELA | Resultado da triagem final | `[NOVO]` |
| 8 | TABELA | Ranking por índice de citação | `[NÃO INCLUIR]` |
| 9 | EQUAÇÃO | Fórmula do IC | `[NÃO INCLUIR]` |
| 10 | FIGURA | Mapa de distribuição dos artigos | `[REESCREVER]` |
