# Relatório de Atualização — 2026-03-02

## Resumo
- Cenário: Inclusão manual de `manual-2026-oliveira-carneiro-souza.pdf` no fluxo PRISMA e propagação documental
- Estágio origem: [2] Deduplicação (entrada na triagem)
- Estágios propagados: [10] Documentação (pipeline_extraction.md, README.md, metodo.tex, diagrama_prisma.tex)

## Contexto

O estudo Oliveira et al. (2026), "Instrumentos da PNDR e Crescimento Econômico no Nordeste: Uma Análise Espacial do FNE, FDNE e Incentivos Fiscais", foi identificado em versão publicada (Revista Cadernos de Finanças Públicas) fora das 5 bases consultadas na busca sistemática. Já havia sido incluído nos artefatos de dados downstream (approved_papers.ris, 2-2-papers.json, references.bib, citation_index_results.json) em sessão anterior, mas o diagrama PRISMA e a documentação não refletiam a inclusão.

## Estado anterior

| Artefato | Valor |
|---|---|
| diagrama_prisma.tex | 118 no fluxo, 80 excluídos, 38 incluídos (inconsistente com dados) |
| pipeline_extraction.md | 118 papers, 36 aprovados, exclusões somando 82 |
| README.md | 118 PDFs, 36 aprovados, 83 rejeitados |
| metodo.tex | 118 únicos (L12), 119 na triagem final (L57) — inconsistência interna |
| approved_papers.ris | 36 entradas (35 bases + 1 manual) — já correto |
| 2-2-papers.json | 119 (36 aprov, 83 rej) — já correto |
| citation_index_results.json | 36 estudos (18 pub, 18 não-pub) — já correto |

## Alterações realizadas

### diagrama_prisma.tex
- Adicionada caixa "Inclusão manual (n=1)" à direita da Identificação
- Seta de inclusão manual → "Registros após remoção de duplicatas"
- Contagens atualizadas: 118→119 (n2, n3, n4)
- Excluídos: 80→83, com breakdown atualizado (22 econométrico, 8 WP, +1 escopo)
- Incluídos: 38→36 (corrigido para coincidir com dados reais)
- Verificação: 119 - 83 = 36 ✓

### pipeline_extraction.md
- Tabela de visão geral: adicionada linha "Inclusão manual" e "Total geral = 119"
- Tabela de PDFs: adicionada linha "Inclusão manual" e "Total geral = 119"
- Seção deduplicação: mencionada inclusão manual (118 bases + 1 manual = 119)
- Seção análise LLM: atualizado modelo (gemini-2.5-flash-lite), nota sobre manual não analisado
- Tabela triagem final: 35 aprovados (bases) + 1 aprovado (manual) + 83 rejeitados = 119
- Motivos de exclusão: detalhados com contagens (40+22+10+8+2+1=83)
- Contagem final: "35 aprovados (bases) + 1 manual = 36 aprovados, 83 rejeitados, 119 total"
- Consolidação JSON: mencionada composição "35 das bases + 1 inclusão manual"

### README.md
- PDFs: 118→119 (118 bases + 1 manual)
- Pipeline ASCII: "PDFs coletados (119)"
- Status etapa 2: mencionada inclusão manual = 119
- Status etapa 4: 119 de 119
- Status etapa 5: "118 papers das bases" (manual não analisado por LLM)
- Status etapa 6: "36 aprovados, 83 rejeitados, 119 total"
- Pipeline diagrama: "36 aprov., 83 rej."

### metodo.tex
- Linha 55: "118 registros únicos" → "119 registros" (consistência com L57 "Dos 119 registros")

## Estado posterior

| Artefato | Antes | Depois | Delta |
|---|---|---|---|
| PRISMA fluxo | 118 | 119 | +1 |
| PRISMA excluídos | 80 | 83 | +3 (correção) |
| PRISMA incluídos | 38 | 36 | -2 (correção) |
| pipeline_extraction.md total | 118 | 119 | +1 |
| README.md PDFs | 118 | 119 | +1 |
| metodo.tex L55 | 118 | 119 | +1 |

## Artefatos modificados

| Arquivo | Tipo de alteração |
|---|---|
| latex/diagrama_prisma.tex | Nó manual + contagens corrigidas |
| docs/pipeline_extraction.md | Contagens e menções atualizadas |
| README.md | Contagens atualizadas |
| latex/metodo.tex | Correção de inconsistência (L55: 118→119) |

## Validações

| Verificação | Resultado |
|---|---|
| PRISMA: 119 - 83 = 36 | ✓ |
| PRISMA breakdown: 40+22+10+8+2+1 = 83 | ✓ |
| metodo.tex L12 vs L57 consistentes | ✓ (118 bases + footnote manual → 119 total) |
| approved_papers.ris = 36 (35+1) | ✓ (sem alteração) |
| 2-2-papers.json = 119 (36+83) | ✓ (sem alteração) |
| citation_index = 36 (18+18) | ✓ (sem alteração) |

## Ações manuais pendentes

- **all_papers_llm_classif_final.xlsx**: O estudo manual não consta neste arquivo (apenas os 118 das bases). Se desejado, o pesquisador pode adicionar uma linha manualmente com "APROVADO" para `manual-2026-oliveira-carneiro-souza.pdf`.
