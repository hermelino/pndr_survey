# Relatorio de Atualizacao — 2026-03-06

## Resumo
- Cenario: Estudo aprovado `manual-2023-silva-azzoni-chagas` (Silva Filho, Azzoni e Chagas, 2023, TD NEREUS/USP) sem referencias extraidas, ausente do indice de citacao cruzada e da tabela IC LaTeX.
- Estagio origem: [8] Extracao+matching de referencias
- Estagios propagados: [8] -> [9] -> [9b] -> [10] -> [11]

## Estado anterior
- Papers em 2-2-papers.json: 129 (43 aprovados, 86 rejeitados)
- Estudos no IC: **42** (21 publicados, 21 nao-publicados)
- Refs ativas em refs_por_estudo/: 49 arquivos, 1.345 refs
- Citacoes cruzadas (IC): 137
- IC nao-publicados > 0: 10
- Nota: Silva2023 excluido do IC por nao ter referencias extraidas

## Alteracoes realizadas

### [8] Extracao de referencias
1. Extraido texto do PDF `manual-2023-silva-azzoni-chagas.pdf` via PyMuPDF
2. Identificada secao de referencias (header com mojibake: "REFER\xc3\x8ANCIAS BIBLIOGR\xc3\x81FICAS" em linha 863)
3. Criado `manual-2023-silva-azzoni-chagas_refs.txt` (5.733 chars)
4. Estruturado em `manual-2023-silva-azzoni-chagas_refs.json` (23 referencias, estilo APA detectado*)
5. Executado `match_refs_to_studies.py`: 2 matches encontrados (cita Resende 2014, Viana 2014)
   - *Nota: O estilo real e ABNT, mas o mojibake do PDF impede deteccao ABNT. O parsing APA funcionou adequadamente.

### [9] Indice de citacao
6. Executado `citation_index.py`: 43 estudos carregados (21 pub + 22 nao-pub), 142 citacoes cruzadas
7. Silva2023: IC_published = 0.00, IC_all = 0.0588 (citado por anpec-2025-souza-irffi-carneiro)
8. Cita 4 estudos da amostra: scopus-2014-resende, anpec-2005-oliveira-domingues, econpapers-2011-resende, scopus-2009-silva-resende-neto

### [9b] Tabela IC LaTeX
9. Executado `generate_ic_table.py`: tabela com 21 pub + 22 nao-pub
10. `\citeonline{Silva2023}` adicionado na coluna de nao publicados com IC = 0,00
11. Corrigido `OUTPUT_PATH` no script de `latex/tabela_ic.tex` para `latex/tabelas/tabela_ic.tex`

### [10] Documentacao
12. Atualizado `docs/pipeline_extraction.md`:
    - 49 JSONs ativos -> 50 JSONs ativos (43 com refs + 7 sem refs)
    - 67 citacoes cruzadas -> 120 citacoes cruzadas (match_refs_to_studies)
    - 137 citacoes cruzadas IC -> 142 citacoes cruzadas IC
    - Removida nota "Silva2023 excluido por nao ter referencias extraidas"

### [11] Artigo LaTeX
13. Verificado `latex/3-metodo.tex`: contagens 43/22/21/10/12 OK
14. Atualizado "137 citacoes cruzadas" -> "142 citacoes cruzadas" (linha 81)

## Estado posterior
- Papers em 2-2-papers.json: 129 (43 aprovados, 86 rejeitados) — sem alteracao
- Estudos no IC: **43** (21 publicados, **22** nao-publicados) — **+1 estudo**
- Refs ativas em refs_por_estudo/: **50** arquivos, **1.368** refs — **+1 arquivo, +23 refs**
- Citacoes cruzadas (IC): **142** — **+5**
- IC nao-publicados > 0: 10 — sem alteracao

## Artefatos modificados
| Arquivo | Alteracao |
|---------|-----------|
| `data/3-ref-bib/refs_por_estudo/manual-2023-silva-azzoni-chagas_refs.txt` | Criado (extracao) |
| `data/3-ref-bib/refs_por_estudo/manual-2023-silva-azzoni-chagas_refs.json` | Criado (estruturacao + matching) |
| `data/3-ref-bib/citation_index_results.json` | Regenerado (43 estudos) |
| `data/3-ref-bib/citation_index_report.txt` | Regenerado |
| `latex/tabelas/tabela_ic.tex` | Regenerado (22 nao-publicados) |
| `scripts/generate_ic_table.py` | Corrigido OUTPUT_PATH |
| `docs/pipeline_extraction.md` | Atualizado contagens |
| `latex/3-metodo.tex` | Atualizado 137->142 citacoes |

## Validacoes
- [x] 43 estudos no IC = 43 aprovados em 2-2-papers.json
- [x] 21 publicados + 22 nao-publicados = 43
- [x] Tabela IC com 21 + 22 = 43 entradas
- [x] Texto do artigo consistente com dados (43/22/21/10/12/142)
- [x] Silva2023 presente no bibtex_key_map.json e references.bib

## Acoes manuais pendentes
Nenhuma.
