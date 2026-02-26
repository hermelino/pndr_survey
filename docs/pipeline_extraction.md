# Pipeline de Extração

Data da extração: 25/02/2026

## Visao geral

Revisao sistematica sobre instrumentos da PNDR (2000-2025). Busca manual em 4 bases academicas, importacao via pipeline, deduplicacao automatica.

| Base | Registros | PDFs | Status |
|------|-----------|------|--------|
| EconPapers/RePEc | 24 | 19 (manual) | Concluido |
| Portal CAPES | 30 | 0 | PDFs pendentes |
| Scopus | 16 | 0 | PDFs pendentes |
| ANPEC | 62 | 62 (auto) | Concluido |
| **Total bruto** | **132** | **81** | |
| **Apos deduplicacao** | **125** | **81** | |

## Estrategia de busca

Queries armazenadas em `scripts/keywords/`. Estrutura de 3 blocos booleanos:

```
(instrumentos: fundo constitucional, fundo de desenvolvimento, incentivo fiscal)
AND (organizacoes: FNE, FNO, FCO, FDNE, FDCO, SUDENE, SUDAM, PNDR)
AND (geografia: nordeste, amazonia, centro-oeste, brasil)
```

### EconPapers / CAPES

```
("fundo constitucional" OR "fundos constitucionais" OR "fundo de desenvolvimento"
OR "fundos de desenvolvimento" OR "incentivo fiscal" OR "incentivos fiscais")
AND ("FNE" OR "FNO" OR "FCO" OR "FDNE" OR "FDCO" OR "SUDENE" OR "SUDECO"
OR "SUDAM" OR "PNDR")
```

### Scopus

```
TITLE-ABS-KEY("fundo constitucional" OR "fundo de desenvolvimento"
OR "incentivo fiscal" OR "incentivos fiscais" OR "regional fund"
OR "constitutional fund" OR "development fund" OR "tax incentive")
AND TITLE-ABS-KEY("FNE" OR "FNO" OR "FCO" OR "FDNE" OR "FDCO"
OR "SUDENE" OR "SUDECO" OR "SUDAM" OR "PNDR")
```

### ANPEC (Google Search)

```
site:anpec.org.br ("fundo constitucional" OR "fundos constitucionais"
OR "fundo de desenvolvimento" OR "incentivo fiscal" OR "incentivos fiscais")
("FNE" OR "FNO" OR "FCO" OR "FDNE" OR "SUDENE" OR "SUDAM" OR "PNDR")
```

## Metodo de coleta por base

| Base | Procedimento |
|------|-------------|
| **EconPapers** | Busca manual em econpapers.repec.org, exportacao RIS individual, unificacao em arquivo combinado. PDFs baixados manualmente das landing pages. |
| **CAPES** | Busca avancada no Portal de Periodicos CAPES via CAFe, exportacao RIS. |
| **Scopus** | Advanced query via proxy CAPES, exportacao RIS. |
| **ANPEC** | Google Search com `site:anpec.org.br`, extracao com extensao de navegador, exportacao Excel. Download automatico de PDFs. |

## Deduplicacao

Algoritmo em 2 fases (modulo `src/dedup/deduplicator.py`):

1. **DOI exato** — normaliza lowercase, remove prefixos
2. **Titulo fuzzy** — `rapidfuzz.token_sort_ratio >= 80%`, com verificacao adicional: mesmo ano E (mesmo primeiro autor OU mesmo periodico)

### Removidos por DOI exato (3)

| Titulo | Base removida | Base mantida | DOI |
|--------|---------------|--------------|-----|
| Eficacia do gasto publico: uma avaliacao do FNE, FNO e FCO | CAPES | EconPapers/Scopus | 10.1590/s0101-41612009000100004 |
| Heifer Retention Program in the Pantanal: a study with DEA and Malmquist index | CAPES | Scopus | 10.1590/s1516-35982012000800019 |
| Measuring Micro- and Macro-Impacts of Regional Development Policies (FNE, 2000-2006) | CAPES | EconPapers/Scopus | 10.1080/00343404.2012.667872 |

### Removidos por titulo fuzzy (4)

| Titulo | Base | Motivo |
|--------|------|--------|
| AVALIACAO DOS IMPACTOS ECONOMICOS DO FNE ENTRE 2004 A 2010 | EconPapers | Variacao de caixa do TD IPEA 1918 |
| EFEITOS DIFERENCIADOS DO FNE NO CRESCIMENTO ECONOMICO DOS MUNICIPIOS NORDESTINOS | EconPapers | Duplicata intra-base |
| EFEITOS DIFERENCIADOS DO FNE NO CRESCIMENTO ECONOMICO DOS MUNICIPIOS NORDESTINOS | EconPapers | Triplicata intra-base |
| Avaliacao dos Impactos Economicos do FCO Entre 2004 e 2010 | EconPapers | Variacao de caixa do TD IPEA 1969 |

Arquivo de auditoria: `data/processed/duplicates_removed.csv`

## Arquivos de dados

### Arquivos integrados (todos os registros)

| Arquivo | Conteudo |
|---------|----------|
| `data/all_records.ris` | 125 registros unicos em formato RIS (para Zotero/Mendeley) |
| `data/all_records.xlsx` | 132 registros com todos os campos, URLs de download, e aba de resumo |

### Registros por base (arquivos originais)

| Arquivo | Conteudo |
|---------|----------|
| `data/econpapers/econpapers_combined.ris` | 24 registros RIS unificados |
| `data/econpapers/individuais/` | 24 arquivos RIS individuais |
| `data/capes/Periodicos-CAPES-RIS.ris` | 30 registros RIS |
| `data/scopus/scopus_export_Feb 25-2026_*.ris` | 16 registros RIS |
| `data/anpec/resultados_anpec_pesquisa_250226_1030.xlsx` | 62 registros Excel |

### PDFs

| Diretorio | Quantidade | Origem |
|-----------|------------|--------|
| `data/papers/papers_econpapers/` | 24 arquivos (19 PDFs + 1 DOC + duplicatas) | Download manual |
| `data/papers/papers_anpec/` | 62 PDFs | Download automatico via extensao |

### Dados processados

| Arquivo | Conteudo |
|---------|----------|
| `data/processed/bib_records.json` | 132 registros normalizados (BibRecord) |
| `data/processed/bib_screened.json` | Registros apos triagem |
| `data/processed/duplicates_removed.csv` | 7 duplicatas removidas (auditoria) |

## Comando de importacao

```bash
cd scripts
python main.py --verbose search \
  --import-econpapers "../data/econpapers/econpapers_combined.ris" \
  --import-capes "../data/capes/Periodicos-CAPES-RIS.ris" \
  --import-scopus "../data/scopus/scopus_export_Feb 25-2026_bd09397c-fbc7-4454-8d88-0d42afc92ae6.ris" \
  --import-anpec "../data/anpec/resultados_anpec_pesquisa_250226_1030.xlsx"
```

## Decisoes metodologicas

- **Google Scholar excluido**: retorna 12.000+ resultados com proporcao elevada de irrelevantes; periodicos relevantes ja cobertos pelo CAPES e RePEc.
- **Web of Science excluido**: cobertura ja atendida pelo CAPES e RePEc.
- **PDFs do EconPapers**: 19 de 24 baixados manualmente (5 nao disponiveis ou duplicatas). URLs em `data/econpapers/econpapers_urls.txt`.
- **PDFs de CAPES e Scopus**: nao possuem URL direta para PDF nos metadados exportados. Download manual pendente via acesso institucional ou resolucao de DOI.

## Trabalho pendente

1. Baixar manualmente os PDFs de CAPES (30) e Scopus (16) → `data/papers/`
2. Executar triagem pre-LLM: `python main.py screen`
3. Executar analise LLM (Stages 1-3): `python main.py analyze`
4. Exportar resultados: `python main.py export`
5. Integrar resultados no artigo LaTeX
