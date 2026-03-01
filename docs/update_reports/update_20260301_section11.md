# Relatório de Atualização — 2026-03-01

## Resumo
- Cenário: #3 — Mudança na triagem final (rejeições manuais)
- Estágio origem: 6 (Triagem final)
- Estágios propagados: 7, 8, 9, 10

## Alteração original
Duas rejeições manuais em `all_papers_llm_classif_final.xlsx` (seção 11 do pipeline_extraction.md):

| Arquivo PDF | Motivo Exclusão | Justificativa |
|---|---|---|
| `anpec-2024-quaglio.pdf` | sem metodo econometrico | Análise espacial descritiva do FNE no Pronaf; não aplica método econométrico |
| `scopus-2012-abreu-gomes-mello.pdf` | outras variaveis de resultado | Avalia retenção de novilhas no Pantanal via DEA e índice Malmquist; variáveis de resultado fora do escopo da PNDR |

Ambos os estudos tinham IC = 0 (nenhuma citação recebida de outros estudos no dataset).

## Estado anterior

| Métrica | Valor |
|---|---|
| Papers em 2-2-papers.json | 118 (38 aprovados, 80 rejeitados) |
| Refs ativas em refs_por_estudo/ | 45 arquivos, ~1.196 refs |
| Citações cruzadas (matching) | 68 em 19/45 arquivos |
| Citações cruzadas (IC) | 114 |
| Estudos no IC | 38 (18 publicados, 20 não-publicados) |

## Alterações realizadas

| # | Ação | Artefato | Resultado |
|---|---|---|---|
| 1 | Re-gerar JSON enriquecido | `2-2-papers.json` | 118 papers (36 aprovados, 82 rejeitados) |
| 2 | Arquivar refs rejeitados | `refs_por_estudo/` → `_archived_duplicates/` | `anpec-2024-quaglio_refs.json` e `scopus-2012-abreu-gomes-mello_refs.json` movidos |
| 3 | Re-rodar matching citações | `refs_por_estudo/*.json` | 67 citações em 18/43 arquivos |
| 4 | Re-rodar índice citação | `citation_index_results.json`, `citation_index_report.txt` | 36 estudos, 114 citações cruzadas |
| 5 | Atualizar README.md | `README.md` | Contagens atualizadas (triagem, refs, matching, IC) |
| 6 | Atualizar pipeline doc | `pipeline_extraction.md` | Contagens de refs (43 ativos, ~1.138 refs), matching (67/18), trabalho pendente |

## Estado posterior

| Métrica | Antes | Depois | Delta |
|---|---|---|---|
| Papers aprovados | 38 | 36 | -2 |
| Papers rejeitados | 80 | 82 | +2 |
| Refs ativas (arquivos) | 45 | 43 | -2 |
| Refs ativas (total) | ~1.196 | ~1.138 | -58 |
| Citações cruzadas (matching) | 68 | 67 | -1 |
| Arquivos com match | 19 | 18 | -1 |
| Citações cruzadas (IC) | 114 | 114 | 0 |
| Estudos no IC | 38 | 36 | -2 |
| Publicados no IC | 18 | 17 | -1 |
| Não-publicados no IC | 20 | 19 | -1 |

## Artefatos modificados

| Arquivo | Tipo de alteração |
|---|---|
| `data/2-papers/2-2-papers.json` | Regenerado (merge_papers_to_json.py) |
| `data/3-ref-bib/refs_por_estudo/_archived_duplicates/anpec-2024-quaglio_refs.json` | Movido de refs_por_estudo/ |
| `data/3-ref-bib/refs_por_estudo/_archived_duplicates/scopus-2012-abreu-gomes-mello_refs.json` | Movido de refs_por_estudo/ |
| `data/3-ref-bib/refs_por_estudo/*.json` (43 ativos) | Atualizados (match_refs_to_studies.py) |
| `data/3-ref-bib/citation_index_results.json` | Regenerado (citation_index.py) |
| `data/3-ref-bib/citation_index_report.txt` | Regenerado (citation_index.py) |
| `docs/pipeline_extraction.md` | Editado (seção 11, contagens refs/matching/IC) |
| `README.md` | Editado (contagens na tabela Status) |

## Validações

- `2-2-papers.json`: 118 papers, 36 APROVADO + 82 REJEITADO = 118 (consistente)
- `refs_por_estudo/`: 43 JSONs ativos (45 - 2 arquivados)
- `citation_index.py`: 36 estudos = 17 pub + 19 não-pub (consistente)
- IC manteve 114 citações — esperado pois ambos estudos removidos tinham IC = 0
- Matching caiu de 68 → 67 (1 citação a menos, coerente com remoção de estudos-alvo)

## Ações manuais pendentes

Nenhuma. Propagação completa.
