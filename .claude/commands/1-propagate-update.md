# Skill: propagate-update

Você é o orquestrador de atualizações do pipeline de revisão sistemática `pndr_survey`. Sua tarefa é diagnosticar uma alteração num estágio do pipeline, planejar a propagação para todos os estágios downstream, executar o plano com confirmação do usuário e gerar um relatório de implementação.

## Grafo de dependências do pipeline

```
[1] Importação (RIS/CSV/Excel)        → bib_records.json
      ↓
[2] Deduplicação (DOI+fuzzy+manual)   → bib_records.json, duplicates_removed.csv
      ↓
[3] Triagem pré-LLM (PRISMA)          → bib_screened.json
      ↓
[4] Coleta de PDFs                     → 2-2-papers-pdfs/
      ↓
[5] Análise LLM (S1→S2→S3)            → _llm_checkpoint.json, all_papers_llm_classif.xlsx
      ↓
[6] Triagem final (manual+LLM)        → all_papers_llm_classif_final.xlsx
      ↓
[7] Consolidação JSON                  → 2-2-papers.json (merge_papers_to_json.py)
      ↓
[7b] RIS aprovados                     → approved_papers.ris (generate_approved_ris.py)
      ↓
[7c] BibTeX referências                → references.bib (generate_bibtex.py)
      ↓
[8] Extração+matching refs             → refs_por_estudo/*.json (match_refs_to_studies.py)
      ↓
[9] Índice de citação                  → citation_index_results.json (citation_index.py)
      ↓
[9b] Tabela IC LaTeX                   → tabela_ic.tex (generate_ic_table.py)
      ↓
[10] Documentação                      → pipeline_extraction.md, README.md
```

**Regra de propagação:** Se o estágio N é afetado, todos os estágios N+1..10 devem ser avaliados. Nem todos precisam ser re-executados — alguns podem não ser afetados pela mudança específica.

## Cenários de atualização

| # | Cenário | Estágio origem | Estágios potencialmente afetados |
|---|---------|----------------|----------------------------------|
| 1 | Nova extração de registros | 1 | 2→3→4→5→6→7→8→9→10 |
| 2 | Novas duplicatas identificadas | 2 | 3→6→7→8→9→10 |
| 3 | Mudança nos critérios de triagem | 6 | 7→8→9→10 |
| 4 | Correções manuais na classificação LLM | 6 | 7→10 |
| 5 | Re-análise LLM (novo modelo/questionário) | 5 | 6→7→8→9→10 |

## Artefatos do pipeline e seus caminhos

```
data/1-records/processed/bib_records.json         # 137 registros normalizados
data/1-records/processed/bib_screened.json         # Registros pós-triagem pré-LLM
data/1-records/processed/duplicates_removed.csv    # Auditoria de duplicatas
data/1-records/all_records.ris                     # RIS consolidado
data/1-records/all_records.xlsx                    # Excel consolidado
data/2-papers/all_papers.xlsx                      # Controle: registros+download
data/2-papers/all_papers_llm_classif.xlsx          # Classificação LLM bruta
data/2-papers/all_papers_llm_classif_final.xlsx    # Classificação LLM revisada (MANUAL)
data/2-papers/_llm_checkpoint.json                 # Checkpoint LLM
data/2-papers/2-2-papers.json                      # JSON enriquecido (MASTER)
data/2-papers/approved_papers.ris                   # RIS dos estudos aprovados (generate_approved_ris.py)
latex/references.bib                                # BibTeX (manual + gerado por generate_bibtex.py)
latex/bibtex_key_map.json                           # Mapeamento PDF→chave BibTeX (generate_bibtex.py)
latex/tabela_ic.tex                                 # Tabela IC LaTeX (generate_ic_table.py)
data/2-papers/2-2-papers-pdfs/                     # PDFs renomeados
data/3-ref-bib/refs_por_estudo/                    # JSONs de referências por estudo
data/3-ref-bib/refs_por_estudo/_archived_duplicates/  # Refs arquivadas de duplicatas
data/3-ref-bib/citation_index_results.json         # Índice de citação
data/3-ref-bib/citation_index_report.txt           # Relatório IC
docs/pipeline_extraction.md                        # Metodologia e log
README.md                                          # Visão geral + status
```

## Scripts do pipeline e como executá-los

```
scripts/main.py search --import-{base} FILE  # Reimportação de registros
scripts/main.py screen --input-json FILE     # Triagem pré-LLM
scripts/run_llm_all_papers.py                # Análise LLM em lote
scripts/merge_papers_to_json.py              # Consolidação JSON
scripts/generate_approved_ris.py             # RIS dos estudos aprovados
scripts/generate_bibtex.py                  # RIS → BibTeX (atualiza references.bib)
scripts/match_refs_to_studies.py             # Matching de citações
scripts/citation_index.py                    # Índice de citação
scripts/generate_ic_table.py                # Tabela IC LaTeX (usa bibtex_key_map.json)
scripts/mark_td_duplicates.py                # Marcação de duplicatas TD/WP
```

## Restrições críticas

1. **NUNCA modificar `all_papers_llm_classif_final.xlsx` programaticamente** — arquivo de decisões manuais do pesquisador. Apenas ler. Se alterações forem necessárias neste arquivo, instruir o usuário a fazê-las manualmente e listar as alterações no relatório.
2. **Re-análise LLM consome API paga** — sempre alertar sobre custo antes de propor.
3. **Documentação é artefato obrigatório** — `pipeline_extraction.md` e `README.md` devem refletir os dados reais após qualquer atualização. Contagens, tabelas e totais devem ser verificados.
4. **Auditabilidade** — toda alteração deve ser rastreável. Duplicatas em `duplicates_removed.csv`, mudanças em `pipeline_extraction.md`.
5. **Duplicatas arquivadas** — ao remover estudos duplicados do dataset ativo de referências, mover os JSONs para `refs_por_estudo/_archived_duplicates/`.

## Procedimento

### FASE 1 — DIAGNÓSTICO

1. Perguntar ao usuário qual estágio do pipeline foi afetado e a natureza da alteração.
2. Ler o estado atual dos artefatos relevantes para quantificar o "antes":
   - Contar registros em `bib_records.json` (total, duplicatas, únicos)
   - Contar papers em `2-2-papers.json` (total, aprovados, rejeitados)
   - Contar refs em `refs_por_estudo/` (arquivos ativos, total de refs)
   - Ler contagens atuais em `pipeline_extraction.md` e `README.md`
3. Registrar snapshot "antes" para o relatório.

### FASE 2 — PLANO DE PROPAGAÇÃO

1. Usando o grafo de dependências e o cenário identificado, listar:
   - Estágios que precisam ser re-executados (com script/comando específico)
   - Estágios que podem ser pulados (com justificativa)
   - Artefatos que serão regenerados
   - Artefatos que precisam de edição manual (com instruções para o usuário)
   - Atualizações documentais necessárias (seções específicas de pipeline_extraction.md e README.md)
2. Apresentar o plano ao usuário em formato tabular claro.
3. Alertar sobre custos (API LLM) se aplicável.
4. **Aguardar aprovação explícita do usuário antes de prosseguir.**

### FASE 3 — EXECUÇÃO

1. Executar cada passo do plano aprovado em sequência.
2. Após cada passo, validar o resultado:
   - Contagens consistentes entre artefatos
   - Arquivos gerados existem e não estão vazios
   - Nenhum dado perdido inadvertidamente
3. Se algum passo falhar, parar e reportar — não tentar forçar.
4. Atualizar `pipeline_extraction.md` e `README.md` com as novas contagens.

### FASE 4 — RELATÓRIO

Após a execução, gerar um relatório de implementação em `docs/update_reports/` com o nome `update_YYYYMMDD_HHMMSS.md` contendo:

```markdown
# Relatório de Atualização — YYYY-MM-DD

## Resumo
- Cenário: [descrição]
- Estágio origem: [N]
- Estágios propagados: [lista]

## Estado anterior
- Registros em bib_records.json: X (Y duplicatas)
- Papers em 2-2-papers.json: X (A aprovados, R rejeitados)
- Refs ativas em refs_por_estudo/: X arquivos, Y refs
- Citações cruzadas: X
- IC não-publicados > 0: X

## Alterações realizadas
[Lista detalhada de cada ação executada, com artefato e resultado]

## Estado posterior
[Mesmas métricas do estado anterior, com deltas]

## Artefatos modificados
[Lista de arquivos alterados com tipo de alteração]

## Validações
[Resultados das verificações de consistência]

## Ações manuais pendentes (se houver)
[Instruções para o usuário sobre o que falta fazer manualmente]
```

## Notas de implementação

- Todos os caminhos são relativos à raiz do projeto (`C:\OneDrive\github\pndr_survey`).
- Scripts Python devem ser executados a partir de `scripts/` (ou com paths absolutos).
- O projeto usa Python 3.12+. Ambiente virtual em `.venv/`.
- Encoding UTF-8 em todos os arquivos.
- `config.yaml` não é versionado; usar `config.example.yaml` como referência.
- API key via variável de ambiente `GEMINI_API_KEY`.
