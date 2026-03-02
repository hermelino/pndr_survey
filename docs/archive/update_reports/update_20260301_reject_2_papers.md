# Relatório de Atualização — 2026-03-01

## Resumo
- Cenário: #4 — Correções manuais na classificação LLM (2 rejeições)
- Estágio origem: 6 (Triagem final)
- Estágios propagados: 7, 8, 9, 10

## Estado anterior
- Papers em `all_papers_llm_classif_final.xlsx`: 118 (40 aprovados, 78 rejeitados)
- Papers em `2-2-papers.json`: 118 (37 aprovados, 81 rejeitados — desatualizado)
- Refs ativas em `refs_por_estudo/`: 47 arquivos, ~1.249 refs
- Citações cruzadas (match_refs): 71 em 20 arquivos
- Citações cruzadas (citation_index): 117
- IC estudos: 40 (18 publicados, 22 não-publicados)

## Alterações realizadas

### Estágio 6 — Triagem final (alterações manuais no Excel)
Duas rejeições manuais já aplicadas pelo pesquisador no `all_papers_llm_classif_final.xlsx`:

| Arquivo PDF | Triagem | Motivo Exclusão |
|-------------|---------|-----------------|
| `anpec-2025-silva-chagas-azzoni.pdf` | APROVADO → REJEITADO | sem instrumentos PNDR |
| `anpec-2024-calife-neto.pdf` | APROVADO → REJEITADO | sem instrumentos PNDR |

**Nota:** `anpec-2024-quaglio.pdf` permanece APROVADO (correção do pesquisador).

### Estágio 7 — Consolidação JSON
- Re-executado `scripts/merge_papers_to_json.py`
- `2-2-papers.json` regenerado: 118 papers (38 aprovados, 80 rejeitados)

### Estágio 8 — Referências
- Arquivados 4 arquivos (2 JSON + 2 TXT) para `_archived_duplicates/`:
  - `anpec-2025-silva-chagas-azzoni_refs.json` + `.txt`
  - `anpec-2024-calife-neto_refs.json` + `.txt`
- Re-executado `scripts/match_refs_to_studies.py`
  - 45 JSONs processados, 1.196 refs, 68 matches em 19 arquivos

### Estágio 9 — Índice de citação
- Re-executado `scripts/citation_index.py`
  - 38 estudos (18 publicados, 20 não-publicados)
  - 114 citações cruzadas

### Estágio 10 — Documentação
- `docs/pipeline_extraction.md`: adicionada seção 10 com as 2 rejeições; contagens atualizadas em 7 locais
- `README.md`: contagens atualizadas (triagem, refs, matching, IC)

## Estado posterior

| Métrica | Antes | Depois | Delta |
|---------|-------|--------|-------|
| Papers aprovados | 40 | 38 | -2 |
| Papers rejeitados | 78 | 80 | +2 |
| Refs ativas (arquivos) | 47 | 45 | -2 |
| Refs ativas (total) | ~1.249 | ~1.196 | -53 |
| Citações cruzadas (matching) | 71 | 68 | -3 |
| Citações cruzadas (IC) | 117 | 114 | -3 |
| Estudos no IC | 40 | 38 | -2 |
| Estudos não-publicados no IC | 22 | 20 | -2 |

## Artefatos modificados

| Artefato | Tipo de alteração |
|----------|------------------|
| `data/2-papers/2-2-papers.json` | Regenerado |
| `data/3-ref-bib/refs_por_estudo/_archived_duplicates/anpec-2025-silva-chagas-azzoni_refs.*` | Arquivado |
| `data/3-ref-bib/refs_por_estudo/_archived_duplicates/anpec-2024-calife-neto_refs.*` | Arquivado |
| `data/3-ref-bib/refs_por_estudo/*.json` (45 ativos) | Regenerados (matching) |
| `data/3-ref-bib/citation_index_results.json` | Regenerado |
| `data/3-ref-bib/citation_index_report.txt` | Regenerado |
| `docs/pipeline_extraction.md` | Editado (seção 10 + contagens) |
| `README.md` | Editado (contagens) |

## Validações
- `merge_papers_to_json.py`: 118/118 matched, 38 aprovados + 80 rejeitados = 118 ✓
- `match_refs_to_studies.py`: 45 JSONs processados, 68 matches ✓
- `citation_index.py`: 38 estudos, 114 citações cruzadas ✓
- Refs arquivadas: 4 arquivos movidos para `_archived_duplicates/` ✓
- Contagens consistentes entre artefatos ✓

## Ações manuais pendentes
Nenhuma.
