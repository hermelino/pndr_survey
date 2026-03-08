# Relatório de Atualização — 2026-03-08

## Resumo
- Cenário: Inclusão manual de novo estudo (Bastos et al. 2026)
- Estágio origem: 4 (coleta de PDFs)
- Estágios propagados: 4→5→6→7→7b→7c→8→9→9b→10→11

## Estudo incluído
- **Título:** Acesso ao Crédito Reduz Desigualdade Salarial de Gênero? Um Estudo Sobre Os Impactos do FNE nos Municípios Nordestinos
- **Autores:** Bastos, Felipe de Sousa; Carneiro, Diego Rafael Fonseca; Shirasu, Maitê Rimekka; Irffi, Guilherme Diniz
- **Ano:** 2026
- **Periódico:** Revista Cadernos de Finanças Públicas, Edição Especial (30º Prêmio Tesouro Nacional)
- **Método:** Generalized Propensity Score (GPS)
- **Instrumento PNDR:** FNE
- **Resultado:** Efeito positivo — aumento nos salários femininos e redução da desigualdade salarial de gênero em municípios com >60% de crédito FNE direcionado a mulheres
- **PDF:** manual-2026-bastos-carneiro-shirasu-irffi.pdf
- **Chave BibTeX:** Bastos2026

## Estado anterior
- Papers em 2-2-papers.json: 129 (43 aprovados, 86 rejeitados)
- Inclusões manuais: 11
- Refs ativas em refs_por_estudo/: 50 arquivos
- Citações cruzadas: 142
- IC: 43 estudos (21 pub, 22 não-pub)
- PRISMA — inclusão manual: n=11
- PRISMA — após dedup: n=129
- PRISMA — incluídos: n=43

## Alterações realizadas

1. **PDF renomeado:** `Artigo+Português.pdf` → `manual-2026-bastos-carneiro-shirasu-irffi.pdf`
2. **all_papers.xlsx:** Adicionada linha #129 (Registros sheet)
3. **Análise LLM:** Gemini 2.5 Flash Lite — 3 stages (S1 triagem, S2 metodologia, S3 resultados), APROVADO
4. **all_papers_llm_classif.xlsx:** Regenerado com 129 papers (128+1)
5. **all_papers_llm_classif_final.xlsx:** Adicionada linha #130 com Triagem=APROVADO
6. **2-2-papers.json:** Regenerado — 130 papers (44 aprovados, 86 rejeitados)
7. **references.bib:** Adicionada entrada @article{Bastos2026,...} na seção manual
8. **bibtex_key_map.json:** Adicionado mapeamento manual-2026-bastos-carneiro-shirasu-irffi → Bastos2026
9. **Refs extraídas:** 35 referências (ABNT), 0 matches com estudos da revisão
10. **citation_index.py:** Adicionado Bastos2026 à lista PUBLISHED_KEYS
11. **Citation index:** Recalculado — 44 estudos (22 pub, 22 não-pub), 142 citações cruzadas
12. **tabela_ic.tex:** Regenerada com 44 estudos
13. **generate_latex_tables.py:** Regeneradas tabelas (estudos-ano, instrumentos, unidade-amostral, métodos, autores)

## Estado posterior

| Métrica | Antes | Depois | Delta |
|---------|-------|--------|-------|
| Papers em 2-2-papers.json | 129 | 130 | +1 |
| Aprovados | 43 | 44 | +1 |
| Rejeitados | 86 | 86 | 0 |
| Inclusões manuais | 11 | 12 | +1 |
| Refs ativas (arquivos) | 50 | 51 | +1 |
| Total referências extraídas | 1204 | 1239 | +35 |
| Citações cruzadas | 142 | 142 | 0 |
| IC — publicados | 21 | 22 | +1 |
| IC — não publicados | 22 | 22 | 0 |
| PRISMA — inclusão manual | 11 | 12 | +1 |
| PRISMA — após dedup | 129 | 130 | +1 |
| PRISMA — incluídos | 43 | 44 | +1 |

## Artefatos modificados

| Artefato | Tipo de alteração |
|----------|-------------------|
| data/2-papers/2-2-papers-pdfs/manual-2026-bastos-carneiro-shirasu-irffi.pdf | Novo (renomeado) |
| data/2-papers/all_papers.xlsx | Linha adicionada |
| data/2-papers/all_papers_llm_classif.xlsx | Regenerado |
| data/2-papers/all_papers_llm_classif_final.xlsx | Linha adicionada |
| data/2-papers/_llm_checkpoint.json | Entrada adicionada |
| data/2-papers/2-2-papers.json | Regenerado |
| data/3-ref-bib/refs_por_estudo/manual-2026-bastos-carneiro-shirasu-irffi_refs.txt | Novo |
| data/3-ref-bib/refs_por_estudo/manual-2026-bastos-carneiro-shirasu-irffi_refs.json | Novo |
| data/3-ref-bib/citation_index_results.json | Regenerado |
| data/3-ref-bib/citation_index_report.txt | Regenerado |
| data/3-ref-bib/referencias_consolidadas.txt | Regenerado |
| data/3-ref-bib/referencias_estruturadas.json | Regenerado |
| scripts/citation_index.py | PUBLISHED_KEYS atualizado |
| latex/references.bib | Entrada Bastos2026 adicionada |
| latex/bibtex_key_map.json | Mapeamento adicionado |
| latex/tabelas/tabela_ic.tex | Regenerada |
| latex/diagrama_prisma.tex | Números atualizados (12/130/130/44) |
| latex/0-main.tex | 43→44, 37→38 |
| latex/1-introducao.tex | 43→44, 37→38 |
| latex/3-metodo.tex | 11→12, 129→130, 43→44, tabelas atualizadas |
| latex/4-resultados.tex | 43→44, 37→38, 31→32 |
| latex/5-consideracoes.tex | 43→44, 37→38, 31→32 |
| docs/pipeline_extraction.md | 11→12, 129→130, 43→44 |
| README.md | Contagens atualizadas |

## Validações
- 2-2-papers.json: 130 papers (44 APROVADO + 86 REJEITADO = 130) ✓
- PRISMA: 137 bases + 12 manual - 19 dedup = 130 ✓
- Excluídos: 130 - 44 = 86 ✓
- IC: 22 pub + 22 não-pub = 44 ✓
- Chave BibTeX Bastos2026 presente em references.bib e bibtex_key_map.json ✓
- Tabela IC inclui Bastos2026 com IC=0,00 ✓

## Ações manuais pendentes
Nenhuma.
