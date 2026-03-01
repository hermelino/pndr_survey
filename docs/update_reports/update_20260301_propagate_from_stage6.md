# Relatório de Atualização — 2026-03-01

## Resumo
- Cenário: Propagação a partir do estágio 6 (triagem final) após revisões manuais em `all_papers_llm_classif_final.xlsx`
- Estágio origem: [6] Triagem final
- Estágios propagados: [7] Consolidação JSON → [8] Matching refs → [9] Índice de citação → [10] Documentação

## Estado anterior
- Papers em `all_papers_llm_classif_final.xlsx`: 118 (40 aprovados, 78 rejeitados)
- Papers em `2-2-papers.json`: 118 (40 aprovados, 78 rejeitados)
- Refs ativas em `refs_por_estudo/`: 47 arquivos, ~1.249 refs
- Citações cruzadas (match_refs): 74 em 21/48 arquivos
- Citações cruzadas (citation_index): 118
- Estudos no índice de citação: 45 (22 pub, 23 não-pub)
- IC não-publicados > 0: 9
- README.md (stage 6): **46 aprovados, 72 rejeitados** (DESATUALIZADO)
- README.md (stage 8): **48 estudos ativos** (DESATUALIZADO)
- README.md (stage 9): **74 citações cruzadas**
- README.md (stage 10): **9 não-publicados com IC > 0**

## Alterações realizadas

### Estágio [7] — Consolidação JSON (`merge_papers_to_json.py`)
- Regenerado `data/2-papers/2-2-papers.json`
- 118 papers (40 aprovados, 78 rejeitados), 91 com resumo, 24 com palavras-chave, 52 com volume/issue/pages

### Estágio [8] — Matching de referências (`match_refs_to_studies.py`)
- Reprocessados 47 JSONs de referências
- 1.249 referências processadas, 71 matches em 20/47 arquivos

### Estágio [9] — Índice de citação (`citation_index.py`)
- Regenerados `citation_index_results.json` e `citation_index_report.txt`
- 40 estudos (18 publicados, 22 não-publicados), 117 citações cruzadas
- Script ignorou 7 estudos rejeitados na triagem (antes incluía 45 estudos; agora corretamente filtra para 40 aprovados)
- 8 não-publicados com IC > 0

### Estágio [10] — Documentação
- `README.md`: Corrigidos 5 valores desatualizados na tabela de status
- `pipeline_extraction.md`: Corrigidos 2 valores nas seções de matching e índice de citação

## Estado posterior

| Métrica | Antes | Depois | Delta |
|---------|-------|--------|-------|
| Papers em 2-2-papers.json | 118 (40A/78R) | 118 (40A/78R) | = |
| Refs ativas (refs_por_estudo/) | 47 arquivos, ~1.249 refs | 47 arquivos, ~1.249 refs | = |
| Matches (match_refs_to_studies) | 74 em 21/48 arq. | 71 em 20/47 arq. | -3 matches, -1 arq. |
| Estudos no índice de citação | 45 (22 pub, 23 np) | 40 (18 pub, 22 np) | -5 estudos |
| Citações cruzadas (citation_index) | 118 | 117 | -1 |
| Não-publicados com IC > 0 | 9 | 8 | -1 |
| README stage 6 | 46A/72R | 40A/78R | corrigido |
| README stage 8 | 48 estudos | 47 estudos | corrigido |
| README stage 9 | 74 citações | 71 citações | corrigido |
| README stage 10 | 9 IC>0 | 8 IC>0 | corrigido |

## Artefatos modificados

| Artefato | Tipo de alteração |
|----------|-------------------|
| `data/2-papers/2-2-papers.json` | Regenerado (merge_papers_to_json.py) |
| `data/3-ref-bib/refs_por_estudo/*.json` | Reprocessados (match_refs_to_studies.py) |
| `data/3-ref-bib/citation_index_results.json` | Regenerado (citation_index.py) |
| `data/3-ref-bib/citation_index_report.txt` | Regenerado (citation_index.py) |
| `README.md` | Edição manual (5 valores corrigidos) |
| `docs/pipeline_extraction.md` | Edição manual (2 valores corrigidos) |

## Validações
- `merge_papers_to_json.py`: 118/118 papers matched com bib_records — OK
- `match_refs_to_studies.py`: 47 JSONs processados, 1.249 refs — OK
- `citation_index.py`: 40 estudos carregados (7 rejeitados ignorados), 117 citações — OK
- Consistência xlsx → JSON: 40 aprovados em ambos — OK
- Documentação reflete dados atuais — OK

## Ações manuais pendentes
Nenhuma.
