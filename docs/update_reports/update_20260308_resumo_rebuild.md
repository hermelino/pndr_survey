# Relatório de Atualização — 2026-03-08

## Resumo
- Cenário: Aba Resumo desatualizada em all_papers_llm_classif_final.xlsx (38 aprovados vs 44 reais)
- Estágio origem: 6 (Triagem final)
- Estágios propagados: nenhum (correção isolada na aba Resumo; dados da aba principal já estavam corretos)

## Causa raiz
A aba "Resumo" foi gerada com base nos 118 registros originais das bases acadêmicas e nunca foi atualizada para refletir as 12 inclusões manuais (estudos de conferência e periódicos adicionados manualmente). A aba principal "Classificação LLM" já continha os 130 registros e 44 aprovados corretos.

## Estado anterior (aba Resumo)
- Total de registros: 118
- Aprovados: 38
- Rejeitados: 80
- Período: 2021–2025
- Motivos de exclusão: sem soma para "variáveis de resultado fora do escopo" (ausente)

## Alterações realizadas
1. **Novo script `scripts/_rebuild_resumo.py`** — gera `data/2-papers/resumo_classificacao.xlsx` a partir da aba "Classificação LLM" de `all_papers_llm_classif_final.xlsx`, sem modificar o arquivo original.
2. **Normalização robusta** — motivos de exclusão, métodos econométricos e unidades amostrais extraídos via keyword matching com suporte a acentos (unidecode).
3. **Período atualizado** — "2021–2025" → "2021–2026" para incluir estudos publicados em 2026.

## Estado posterior (resumo_classificacao.xlsx)
- Total de registros: 130 (+12)
- Aprovados: 44 (+6)
- Rejeitados: 86 (+6)
- Período: 2021–2026 (21 estudos neste intervalo)
- Motivos de exclusão: 39+24+10+8+3+2 = 86 (soma correta)

### Aprovados por período
| Período | Qtd |
|---------|-----|
| 2005–2010 | 2 |
| 2011–2015 | 5 |
| 2016–2020 | 16 |
| 2021–2026 | 21 |
| **TOTAL** | **44** |

### Métodos econométricos (21 distintos)
| Método | Estudos | MSM |
|--------|---------|-----|
| Diferenças em Diferenças (DiD) | 11 | 3 |
| Generalized Propensity Score (GPS) | 6 | 3 |
| Diferenças em Diferenças Escalonado | 6 | 3 |
| Painel de Efeitos Fixos | 6 | 3 |
| Propensity Score Matching (PSM) | 5 | 3 |
| Painel Espacial | 5 | 3 |
| Painel Dinâmico GMM | 4 | 3 |
| MQO/OLS | 3 | 2 |
| Equilíbrio Geral Computável (EGC) | 3 | n.c. |
| Análise Envoltória de Dados (DEA) | 3 | n.c. |
| Modelo de Erro Espacial | 3 | 3 |
| Primeiras Diferenças (FD) | 2 | 3 |
| Variáveis Instrumentais (IV) | 2 | 3 |
| Fronteira Estocástica (SFA) | 2 | n.c. |
| Controle Sintético Generalizado | 1 | 3 |
| Painel de Efeitos Aleatórios | 1 | 3 |
| Modelo de Efeito Limiar (Threshold) | 1 | 3 |
| Fronteira de Ordem-m | 1 | n.c. |
| Regressão Descontínua (RDD) | 1 | 4 |
| Análise de Sobrevivência | 1 | n.c. |
| Regressão Quantílica | 1 | 3 |

## Artefatos modificados
| Arquivo | Alteração |
|---------|-----------|
| `data/2-papers/resumo_classificacao.xlsx` | **Novo** — resumo standalone gerado a partir dos dados |
| `scripts/_rebuild_resumo.py` | **Novo** — script de geração do resumo |

## Validações
- Soma de motivos (86) = total rejeitados (86) ✓
- Soma de períodos (44) = total aprovados (44) ✓
- Contagens consistentes com `2-2-papers.json` (130 total, 44 aprovados) ✓
- Contagens consistentes com `citation_index_report.txt` (44 estudos) ✓

## Decisão arquitetural
O resumo foi extraído para arquivo separado (`resumo_classificacao.xlsx`) em vez de modificar `all_papers_llm_classif_final.xlsx`, respeitando a restrição de não alterar programaticamente o arquivo de decisões manuais do pesquisador. O script pode ser re-executado a qualquer momento para regenerar o resumo.

## Ações manuais pendentes
Nenhuma.
