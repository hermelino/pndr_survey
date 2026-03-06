# Relatorio de Atualizacao — 2026-03-06

## Resumo
- Cenario: Typo "Velooso" (duplo "o") no nome do autor Veloso, originado na extracao LLM (Stage 1), propagado para RIS, BibTeX, bibtex_key_map e tabela IC LaTeX.
- Estagio origem: [5] Analise LLM (s1.autores em 2-2-papers.json)
- Estagios propagados: [5] -> [7b] -> [7c] -> [9b]

## Estado anterior
- `2-2-papers.json` L6605: s1.autores = "VELOOSO, Pedro Alexandre Santos; ..."
- `approved_papers.ris` L479: AU = "VELOOSO, Pedro Alexandre Santos"
- `references.bib`: entrada duplicata `@inproceedings{Velooso2024,...}` (L1066-1072) alem da entrada correta `@inproceedings{Veloso2024,...}` (L795)
- `bibtex_key_map.json`: `"anpec-2024-veloso-costa-carneiro": "Velooso2024"`
- `tabela_ic.tex` L30: `\citeonline{Velooso2024}`
- `generate_resumo.py` L79: workaround `"Velooso, P. A. S.": "Veloso, P. A. S."`

## Alteracoes realizadas

### [5] 2-2-papers.json
1. Corrigido s1.autores: "VELOOSO" -> "VELOSO" (L6605)

### [7b] approved_papers.ris
2. Corrigido AU: "VELOOSO" -> "VELOSO" (L479)

### [7c] references.bib + bibtex_key_map.json
3. Removida entrada duplicata `Velooso2024` (L1066-1072) — a entrada correta `Veloso2024` (L795) ja existia
4. Atualizado bibtex_key_map.json: `"Velooso2024"` -> `"Veloso2024"` (L29)

### [9b] tabela_ic.tex
5. Regenerada via `generate_ic_table.py`: `\citeonline{Veloso2024}` agora correto (L30)

### Workaround removido
6. Removida linha de correcao em `generate_resumo.py` (L79) — nao mais necessaria

## Estado posterior
- Nenhuma contagem alterada (43 estudos, 21 pub, 22 nao-pub, 142 citacoes cruzadas)
- Todas as referencias a "Velooso" eliminadas dos artefatos ativos
- Unica ocorrencia remanescente: `docs/archive/avaliacao_metodo_20260304.md` (registro historico da deteccao do erro)

## Artefatos modificados
| Arquivo | Alteracao |
|---------|-----------|
| `data/2-papers/2-2-papers.json` | Corrigido s1.autores (VELOOSO -> VELOSO) |
| `data/2-papers/approved_papers.ris` | Corrigido AU (VELOOSO -> VELOSO) |
| `latex/references.bib` | Removida entrada duplicata Velooso2024 |
| `latex/bibtex_key_map.json` | Velooso2024 -> Veloso2024 |
| `latex/tabelas/tabela_ic.tex` | Regenerada (Veloso2024 correto) |
| `scripts/generate_resumo.py` | Removido workaround do typo |

## Validacoes
- [x] "Velooso" nao aparece em nenhum artefato ativo (apenas em docs/archive/)
- [x] Entrada `Veloso2024` existe em references.bib (L795) com autor correto
- [x] bibtex_key_map.json aponta para `Veloso2024`
- [x] tabela_ic.tex usa `\citeonline{Veloso2024}`
- [x] Contagens inalteradas: 43 estudos, 21 pub, 22 nao-pub

## Acoes manuais pendentes
Nenhuma.
