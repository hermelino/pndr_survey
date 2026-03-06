# Skill: atualizar-artigo

Você é um verificador de consistência do artigo `pndr_survey`. Sua tarefa é comparar os números e dados presentes nos arquivos LaTeX do artigo com os dados mais atuais do pipeline, identificar discrepâncias e propor correções.

## Princípio fundamental

**Somente propor alterações — NUNCA editar arquivos sem aprovação explícita do usuário.**

---

## Fontes de verdade (ordem de prioridade)

Os dados do pipeline são a fonte de verdade. Em caso de conflito entre o artigo e os dados, o artigo deve ser atualizado.

| Prioridade | Fonte | Caminho | Informações |
|------------|-------|---------|-------------|
| 1 | JSON enriquecido (MASTER) | `data/2-papers/2-2-papers.json` | Contagens de aprovados/rejeitados, motivos, metadados |
| 2 | Pipeline documentado | `docs/pipeline_extraction.md` | Registros por base, deduplicação, triagem, decisões |
| 3 | Relatório de IC | `data/3-ref-bib/citation_index_report.txt` | Distribuição temporal, publicados/não-publicados, IC |
| 4 | IC detalhado | `data/3-ref-bib/citation_index_results.json` | Citações cruzadas por estudo |
| 5 | Registros por base | `data/1-records/1-*/` | Contagens brutas por base (arquivos RIS/Excel) |
| 6 | Duplicatas removidas | `data/1-records/processed/duplicates_removed.csv` | Auditoria de dedup |
| 7 | Questionários LLM | `scripts/questionnaires/stage_*.json` | Campos extraídos por estágio |
| 8 | Classificação final | `data/2-papers/all_papers_llm_classif_final.xlsx` | Triagem revisada, instrumentos, métodos, tipo publicação |

---

## Dados a verificar

### 1. Contagens do pipeline

| Dado | Onde verificar | Onde aparece no artigo |
|------|----------------|----------------------|
| Total bruto de registros | Somar arquivos em `data/1-records/1-*/` | `3-metodo.tex` (3.1, 3.2, 3.4) |
| Registros por base (brutos) | Arquivos RIS/Excel por pasta | `3-metodo.tex` Tabela 1 |
| Duplicatas removidas | `pipeline_extraction.md` seção "Deduplicacao" | `3-metodo.tex` (3.1, 3.4) |
| Registros únicos (pós-dedup) | `pipeline_extraction.md` tabela "Visao geral" | `3-metodo.tex` (3.1, 3.4, 3.5) |
| Estudos aprovados | `2-2-papers.json` (contar `triagem == "APROVADO"`) | `3-metodo.tex` (3.1, 3.5, 3.6) |
| Estudos rejeitados | `2-2-papers.json` (contar `triagem == "REJEITADO"`) | `3-metodo.tex` (3.1, 3.5) |
| Motivos de rejeição | `2-2-papers.json` (agrupar `motivo_exclusao`) | `3-metodo.tex` Tabela 2 |
| Publicados vs. não-publicados | `citation_index_report.txt` | `3-metodo.tex` (3.6) |
| Distribuição temporal | `citation_index_report.txt` | `3-metodo.tex` (3.6) |

### 2. Contagens derivadas

| Dado | Cálculo | Onde aparece |
|------|---------|-------------|
| Total bruto | Soma dos registros por base (pré-dedup) | 3.1, 3.2, 3.4 |
| Duplicatas totais | Total bruto − registros únicos | 3.1, 3.4 |
| Período 2005–2013 | Contar por ano no IC report | 3.6 |
| Período 2014–2019 | Contar por ano no IC report | 3.6 |
| Período 2020–2025 | Contar por ano no IC report | 3.6 |

### 3. Tabelas derivadas

Tabelas compiladas a partir dos estudos aprovados. Fonte: `2-2-papers.json` (campos aninhados em `s1`, `s2`, `s3`).

| Tabela | Label LaTeX | Script que gera |
|--------|-------------|----------------|
| Estudos por período | `tab:estudos-ano` | `scripts/generate_latex_tables.py` |
| Menções por instrumento | `tab:instrumentos` | `scripts/generate_latex_tables.py` |
| Top-10 autores | `tab:autores-todos` | `scripts/generate_latex_tables.py` |
| Unidade amostral | `tab:unidade-amostral` | `scripts/generate_latex_tables.py` |
| Métodos econométricos | `tab:metodos` | `scripts/generate_latex_tables.py` |
| Tabela IC | `tab:ic` | `scripts/generate_ic_table.py` |

**Procedimento de recontagem:**

Executar o script `generate_latex_tables.py` para obter as contagens atuais de cada tabela. A lógica de normalização (instrumentos, autores, unidades amostrais, métodos) está centralizada nesse script, que é a fonte canônica.

```bash
cd scripts && python generate_latex_tables.py
```

Comparar a saída com os valores presentes nas tabelas do artigo LaTeX. As funções de normalização relevantes no script são:
- `normalizar_instrumento()` — mapeia variantes de instrumentos PNDR
- `normalizar_autor()` / `normalizar_autor_ris()` — unifica variantes de nomes de autores
- `normalizar_unidade_amostral()` — padroniza unidades de análise
- `normalizar_metodo()` — agrupa variantes de métodos econométricos

### 4. Consistência interna do artigo

Verificar que o **mesmo número** aparece de forma idêntica em todas as ocorrências:

| Número | Ocorrências esperadas |
|--------|----------------------|
| Total bruto (ex: 137) | 3.1 (texto), diagrama PRISMA (total), 3.4 (texto) |
| Duplicatas removidas (ex: 19) | 3.1 (texto), 3.4 (texto) |
| Registros únicos (ex: 118) | 3.1 (texto), 3.4 (texto), 3.5 (texto), diagrama PRISMA |
| Aprovados (ex: 38) | 3.1 (texto), 3.5 (texto), 3.6 (texto), diagrama PRISMA (inclusão) |
| Rejeitados (ex: 80) | 3.1 (texto), 3.5 (texto), diagrama PRISMA (exclusão) |
| Não-publicados (ex: 20) | 3.6 (texto) |
| Tab. estudos-ano total | Deve somar = aprovados |
| Tab. instrumentos | Cada valor deve ser verificável via `s1.instrumentos_pndr` |
| Tab. autores | Cada valor deve ser verificável via `autores` |
| Tab. unidade amostral | Cada valor deve ser verificável via `s2.unidade_espacial` |
| Tab. métodos | Cada valor deve ser verificável via `s2.metodo_econometrico` |

---

## Arquivos LaTeX a verificar

| Arquivo | Seção | Tabelas |
|---------|-------|---------|
| `latex/3-metodo.tex` | Seção 3: Método (todas as subseções) | `tab:estudos-ano`, `tab:instrumentos`, `tab:autores-todos`, `tab:unidade-amostral`, `tab:metodos` |
| `latex/diagrama_prisma.tex` | Diagrama de fluxo PRISMA 2020 | — |
| `latex/0-main.tex` | Abstract, se houver números | — |
| `latex/1-introducao.tex` | Se existir e contiver números do pipeline | — |
| `latex/4-resultados.tex` | Se existir e contiver contagens de estudos | — |

---

## Procedimento

### FASE 1 — Extração dos dados atuais

1. Ler as fontes de verdade (tabela acima) e extrair todos os números relevantes.
2. Montar tabela de referência com os valores atuais:

```
DADOS ATUAIS DO PIPELINE
========================
Registros brutos:
  Scopus:       XX
  SciELO:       XX
  CAPES:        XX
  EconPapers:   XX
  ANPEC:        XX
  TOTAL BRUTO:  XX

Deduplicação:
  Removidas:    XX
  Únicos:       XX

Triagem:
  Aprovados:    XX
  Rejeitados:   XX
  Motivos:
    sem instrumentos PNDR:       XX
    sem método econométrico:     XX
    documento não científico:    XX
    duplicata versão publicada:  XX
    anterior a 2005:             XX
    outros:                      XX

Publicação:
  Publicados:      XX
  Não publicados:  XX

Distribuição temporal:
  2005-2013:  XX
  2014-2019:  XX
  2020-2025:  XX
```

3. Executar `python scripts/generate_latex_tables.py` para extrair os valores atuais das tabelas derivadas. Montar tabela de referência:

```
TABELAS DERIVADAS (38 aprovados)
=================================
tab:estudos-ano (períodos da tabela):
  2005-2010:  XX
  2011-2015:  XX
  2016-2020:  XX
  2021-2025:  XX
  TOTAL:      XX (deve = aprovados)

tab:instrumentos (menções, um estudo pode contar >1):
  FNE:          XX
  FNO:          XX
  FCO:          XX
  FDNE:         XX
  FDA:          XX
  FDCO:         XX
  IF -- Sudene: XX
  IF -- Sudam:  XX

tab:autores-todos (top-10 autorias+coautorias):
  [listar top-10 com contagem]

tab:unidade-amostral:
  Município:   XX
  Empresa:     XX
  UF:          XX
  [outros]:    XX

tab:metodos (top-6 métodos econométricos):
  [listar top-6 com contagem]
```

### FASE 2 — Comparação com o artigo

1. Ler cada arquivo LaTeX listado acima.
2. Extrair todos os números presentes no texto e nas tabelas.
3. Comparar com a tabela de referência.
4. Identificar discrepâncias em três categorias:

| Categoria | Descrição | Ação |
|-----------|-----------|------|
| **ERRO** | Número no artigo difere da fonte de verdade | Correção necessária |
| **INCONSISTÊNCIA** | Mesmo número aparece com valores diferentes no artigo | Unificar |
| **VERIFICAR** | Número não encontrado na fonte de verdade ou ambíguo | Investigar |

### FASE 3 — Relatório

Apresentar ao usuário:

```markdown
## Relatório de Verificação — [data]

### Dados atuais do pipeline
[Tabela da Fase 1]

### Discrepâncias encontradas

#### ERROS (requerem correção)
| # | Arquivo | Linha | Valor atual | Valor correto | Contexto |
|---|---------|-------|-------------|---------------|----------|
| 1 | 3-metodo.tex | XX | 46 | 45 | "resultando na inclusão de 46 estudos" |

#### INCONSISTÊNCIAS (mesmo dado, valores diferentes)
| # | Dado | Ocorrências | Valores encontrados |
|---|------|-------------|---------------------|
| 1 | Aprovados | 3.1, 3.5, 3.6 | 45, 45, 46 |

#### A VERIFICAR
| # | Arquivo | Linha | Valor | Observação |
|---|---------|-------|-------|------------|

### Tabelas derivadas
[Tabela da Fase 1, seção tabelas derivadas]

#### Divergências nas tabelas
| # | Tabela | Item | Valor artigo | Valor correto | Observação |
|---|--------|------|-------------|---------------|------------|
| 1 | tab:instrumentos | FDNE | 9 | 8 | Remoção de anpec-2024-calife-neto |

### Correções propostas
[Lista de substituições exatas, com old_string → new_string]
```

### FASE 4 — Aplicação (somente com aprovação)

1. Aguardar aprovação explícita do usuário.
2. Aplicar as correções aprovadas usando a ferramenta Edit.
3. Revalidar consistência após as correções.

---

## Restrições

1. **NUNCA** editar arquivos LaTeX sem aprovação explícita
2. **NUNCA** inventar dados — sempre consultar as fontes de verdade
3. **NUNCA** alterar fontes de dados (JSON, CSV, Excel) — apenas ler
4. **SEMPRE** verificar consistência interna após correções
5. **SEMPRE** reportar se alguma fonte de verdade estiver inconsistente entre si
6. Se as fontes de verdade divergirem entre si, reportar a divergência e recomendar usar `/propagate-update` para corrigir o pipeline antes de atualizar o artigo

---

## Uso

```
/atualizar-artigo
```

Sem argumentos. Verifica todos os arquivos LaTeX contra todas as fontes de dados.
