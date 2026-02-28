# Skill: propagate-update

Voce e o orquestrador de atualizacoes do pipeline de revisao sistematica `pndr_survey`. Sua tarefa e diagnosticar uma alteracao num estagio do pipeline, planejar a propagacao para todos os estagios downstream, executar o plano com confirmacao do usuario e gerar um relatorio de implementacao.

## Grafo de dependencias do pipeline

```
[1] Importacao (RIS/CSV/Excel)        → bib_records.json
      ↓
[2] Deduplicacao (DOI+fuzzy+manual)   → bib_records.json, duplicates_removed.csv
      ↓
[3] Triagem pre-LLM (PRISMA)         → bib_screened.json
      ↓
[4] Coleta de PDFs                    → 2-2-papers-pdfs/
      ↓
[5] Analise LLM (S1→S2→S3)           → _llm_checkpoint.json, all_papers_llm_classif.xlsx
      ↓
[6] Triagem final (manual+LLM)       → all_papers_llm_classif_final.xlsx
      ↓
[7] Consolidacao JSON                 → 2-2-papers.json (merge_papers_to_json.py)
      ↓
[8] Extracao+matching refs            → refs_por_estudo/*.json (match_refs_to_studies.py)
      ↓
[9] Indice de citacao                 → citation_index_results.json (citation_index.py)
      ↓
[10] Documentacao                     → pipeline_extraction.md, README.md
```

**Regra de propagacao:** Se o estagio N e afetado, todos os estagios N+1..10 devem ser avaliados. Nem todos precisam ser re-executados — alguns podem nao ser afetados pela mudanca especifica.

## Cenarios de atualizacao

| # | Cenario | Estagio origem | Estagios potencialmente afetados |
|---|---------|----------------|----------------------------------|
| 1 | Nova extracao de registros | 1 | 2→3→4→5→6→7→8→9→10 |
| 2 | Novas duplicatas identificadas | 2 | 3→6→7→8→9→10 |
| 3 | Mudanca nos criterios de triagem | 6 | 7→8→9→10 |
| 4 | Correcoes manuais na classificacao LLM | 6 | 7→10 |
| 5 | Re-analise LLM (novo modelo/questionario) | 5 | 6→7→8→9→10 |

## Artefatos do pipeline e seus caminhos

```
data/1-records/processed/bib_records.json         # 137 registros normalizados
data/1-records/processed/bib_screened.json         # Registros pos-triagem pre-LLM
data/1-records/processed/duplicates_removed.csv    # Auditoria de duplicatas
data/1-records/all_records.ris                     # RIS consolidado
data/1-records/all_records.xlsx                    # Excel consolidado
data/2-papers/all_papers.xlsx                      # Controle: registros+download
data/2-papers/all_papers_llm_classif.xlsx          # Classificacao LLM bruta
data/2-papers/all_papers_llm_classif_final.xlsx    # Classificacao LLM revisada (MANUAL)
data/2-papers/_llm_checkpoint.json                 # Checkpoint LLM
data/2-papers/2-2-papers.json                      # JSON enriquecido (MASTER)
data/2-papers/2-2-papers-pdfs/                     # PDFs renomeados
data/3-ref-bib/refs_por_estudo/                    # JSONs de referencias por estudo
data/3-ref-bib/refs_por_estudo/_archived_duplicates/  # Refs arquivadas de duplicatas
data/3-ref-bib/citation_index_results.json         # Indice de citacao
data/3-ref-bib/citation_index_report.txt           # Relatorio IC
docs/pipeline_extraction.md                        # Metodologia e log
README.md                                          # Visao geral + status
```

## Scripts do pipeline e como executa-los

```
scripts/main.py search --import-{base} FILE  # Reimportacao de registros
scripts/main.py screen --input-json FILE     # Triagem pre-LLM
scripts/run_llm_all_papers.py                # Analise LLM em lote
scripts/merge_papers_to_json.py              # Consolidacao JSON
scripts/match_refs_to_studies.py             # Matching de citacoes
scripts/citation_index.py                    # Indice de citacao
scripts/mark_td_duplicates.py                # Marcacao de duplicatas TD/WP
```

## Restricoes criticas

1. **NUNCA modificar `all_papers_llm_classif_final.xlsx` programaticamente** — arquivo de decisoes manuais do pesquisador. Apenas ler. Se alteracoes forem necessarias neste arquivo, instruir o usuario a faze-las manualmente e listar as alteracoes no relatorio.
2. **Re-analise LLM consome API paga** — sempre alertar sobre custo antes de propor.
3. **Documentacao e artefato obrigatorio** — `pipeline_extraction.md` e `README.md` devem refletir os dados reais apos qualquer atualizacao. Contagens, tabelas e totais devem ser verificados.
4. **Auditabilidade** — toda alteracao deve ser rastreavel. Duplicatas em `duplicates_removed.csv`, mudancas em `pipeline_extraction.md`.
5. **Duplicatas arquivadas** — ao remover estudos duplicados do dataset ativo de referencias, mover os JSONs para `refs_por_estudo/_archived_duplicates/`.

## Procedimento

### FASE 1 — DIAGNOSTICO

1. Perguntar ao usuario qual estagio do pipeline foi afetado e a natureza da alteracao.
2. Ler o estado atual dos artefatos relevantes para quantificar o "antes":
   - Contar registros em `bib_records.json` (total, duplicatas, unicos)
   - Contar papers em `2-2-papers.json` (total, aprovados, rejeitados)
   - Contar refs em `refs_por_estudo/` (arquivos ativos, total de refs)
   - Ler contagens atuais em `pipeline_extraction.md` e `README.md`
3. Registrar snapshot "antes" para o relatorio.

### FASE 2 — PLANO DE PROPAGACAO

1. Usando o grafo de dependencias e o cenario identificado, listar:
   - Estagios que precisam ser re-executados (com script/comando especifico)
   - Estagios que podem ser pulados (com justificativa)
   - Artefatos que serao regenerados
   - Artefatos que precisam de edicao manual (com instrucoes para o usuario)
   - Atualizacoes documentais necessarias (secoes especificas de pipeline_extraction.md e README.md)
2. Apresentar o plano ao usuario em formato tabular claro.
3. Alertar sobre custos (API LLM) se aplicavel.
4. **Aguardar aprovacao explicita do usuario antes de prosseguir.**

### FASE 3 — EXECUCAO

1. Executar cada passo do plano aprovado em sequencia.
2. Apos cada passo, validar o resultado:
   - Contagens consistentes entre artefatos
   - Arquivos gerados existem e nao estao vazios
   - Nenhum dado perdido inadvertidamente
3. Se algum passo falhar, parar e reportar — nao tentar forcar.
4. Atualizar `pipeline_extraction.md` e `README.md` com as novas contagens.

### FASE 4 — RELATORIO

Apos a execucao, gerar um relatorio de implementacao em `docs/update_reports/` com o nome `update_YYYYMMDD_HHMMSS.md` contendo:

```markdown
# Relatorio de Atualizacao — YYYY-MM-DD

## Resumo
- Cenario: [descricao]
- Estagio origem: [N]
- Estagios propagados: [lista]

## Estado anterior
- Registros em bib_records.json: X (Y duplicatas)
- Papers em 2-2-papers.json: X (A aprovados, R rejeitados)
- Refs ativas em refs_por_estudo/: X arquivos, Y refs
- Citacoes cruzadas: X
- IC nao-publicados > 0: X

## Alteracoes realizadas
[Lista detalhada de cada acao executada, com artefato e resultado]

## Estado posterior
[Mesmas metricas do estado anterior, com deltas]

## Artefatos modificados
[Lista de arquivos alterados com tipo de alteracao]

## Validacoes
[Resultados das verificacoes de consistencia]

## Acoes manuais pendentes (se houver)
[Instrucoes para o usuario sobre o que falta fazer manualmente]
```

## Notas de implementacao

- Todos os caminhos sao relativos a raiz do projeto (`C:\OneDrive\github\pndr_survey`).
- Scripts Python devem ser executados a partir de `scripts/` (ou com paths absolutos).
- O projeto usa Python 3.12+. Ambiente virtual em `.venv/`.
- Encoding UTF-8 em todos os arquivos.
- `config.yaml` nao e versionado; usar `config.example.yaml` como referencia.
- API key via variavel de ambiente `GEMINI_API_KEY`.
