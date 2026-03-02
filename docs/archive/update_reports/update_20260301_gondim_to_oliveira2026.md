# Relatório de Atualização — 2026-03-01

## Resumo
- Cenário: Substituição de versão WP/congresso (anpec-2025-gondim) por versão publicada (manual-2026-oliveira-carneiro-souza) na Revista Cadernos de Finanças Públicas (2026, Edição Especial)
- Estágio origem: 6 (Triagem final)
- Estágios propagados: 7, 7b, 7c, 8, 9, 9b, 10

## Estado anterior
- Papers em 2-2-papers.json: 118 (36 aprovados, 82 rejeitados)
- Publicados / Não publicados: 17 / 19
- Refs ativas em refs_por_estudo/: 43 arquivos
- Citações cruzadas: 114
- IC não-publicados > 0: 8
- gondim status: APROVADO, apresentação em congresso, Publicado=Não

## Alterações realizadas

### Passo 0 — Edições manuais (usuário)
- `all_papers_llm_classif_final.xlsx`: anpec-2025-gondim.pdf → REJEITADO (motivo: duplicata de versão publicada)
- `all_papers_llm_classif_final.xlsx`: nova linha manual-2026-oliveira-carneiro-souza.pdf → APROVADO (artigo publicado, Revista Cadernos de Finanças Públicas, 2026)
- PDF renomeado: `Artigo+Português.pdf` → `manual-2026-oliveira-carneiro-souza.pdf`

### Passo 0b — citation_index.py
- Adicionado `manual-2026-oliveira-carneiro-souza` a PUBLISHED_KEYS

### Passo 1 — merge_papers_to_json.py
- 119 papers (36 aprovados, 83 rejeitados)
- manual-2026 sem match em bib_records (esperado: inclusão manual)

### Passo 2 — generate_approved_ris.py
- Entrada gondim removida do RIS, nova entrada manual-2026 adicionada
- 36 entradas validadas

### Passo 3 — generate_bibtex.py
- Chave Gondiim2025 removida, nova chave Oliveira2026 gerada
- bibtex_key_map.json atualizado (36 entradas)

### Passo 4 — Refs
- Copiados anpec-2025-gondim_refs.{json,txt} → manual-2026-oliveira-carneiro-souza_refs.{json,txt}
- Meta atualizada (estudo_num, autores, titulo, pdf)
- Originais arquivados em _archived_duplicates/
- match_refs_to_studies.py re-executado: 5/46 matches (consistente)

### Passo 5 — citation_index.py
- 36 estudos: 18 publicados, 18 não-publicados
- 114 citações cruzadas (mantidas)

### Passo 6 — generate_ic_table.py
- Tabela IC com 18 entradas (era 19, Gondiim2025 removido)

### Passo 7 — Documentação
- metodo.tex: 82→83 rejeitados, n=7→n=8 WP duplicatas, 19→18 não-pub, 17→18 pub, 2005-2025→2005-2026
- pipeline_extraction.md: 82→83 rejeitados, 118→119 papers, 17→18 pub, 19→18 não-pub
- README.md: 82→83 rejeitados, 17→18 pub, 19→18 não-pub

## Estado posterior
- Papers em 2-2-papers.json: 119 (36 aprovados, 83 rejeitados) [+1 total, +1 rejeitado]
- Publicados / Não publicados: 18 / 18 [+1 pub, -1 não-pub]
- Refs ativas em refs_por_estudo/: 43 arquivos [mantido]
- Citações cruzadas: 114 [mantido]
- IC não-publicados > 0: 8 [mantido]

## Artefatos modificados
| Artefato | Tipo de alteração |
|----------|-------------------|
| all_papers_llm_classif_final.xlsx | Edição manual (gondim rejeitado + nova linha) |
| data/2-papers/2-2-papers.json | Regenerado (merge_papers_to_json.py) |
| data/2-papers/approved_papers.ris | Regenerado (generate_approved_ris.py) |
| latex/references.bib | Regenerado (generate_bibtex.py) |
| latex/bibtex_key_map.json | Regenerado (generate_bibtex.py) |
| data/3-ref-bib/refs_por_estudo/manual-2026-oliveira-carneiro-souza_refs.json | Novo (copiado de gondim) |
| data/3-ref-bib/refs_por_estudo/manual-2026-oliveira-carneiro-souza_refs.txt | Novo (copiado de gondim) |
| data/3-ref-bib/refs_por_estudo/_archived_duplicates/anpec-2025-gondim_refs.* | Arquivado |
| data/3-ref-bib/citation_index_results.json | Regenerado (citation_index.py) |
| data/3-ref-bib/citation_index_report.txt | Regenerado (citation_index.py) |
| latex/tabela_ic.tex | Regenerado (generate_ic_table.py) |
| scripts/citation_index.py | Editado (PUBLISHED_KEYS) |
| latex/metodo.tex | Editado (contagens) |
| docs/pipeline_extraction.md | Editado (contagens) |
| README.md | Editado (contagens) |

## Validações
- [x] 36 aprovados no JSON == 36 entradas no RIS == 36 entradas no BibTeX
- [x] 18 publicados + 18 não-publicados = 36
- [x] 36 + 83 = 119 total
- [x] gondim arquivado em _archived_duplicates
- [x] manual-2026 classificado como publicado no IC
- [x] Tabela IC com 18 não-publicados (gondim removido)
- [x] 114 citações cruzadas mantidas

## Ações manuais pendentes
Nenhuma.
