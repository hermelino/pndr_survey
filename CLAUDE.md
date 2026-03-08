# CLAUDE.md — Regras do Projeto pndr_survey

## Contexto

Revisao sistematica (SLR) sobre instrumentos da PNDR. Duas fases:
1. **Coleta** — busca manual em bases academicas, importacao, deduplicacao
2. **Analise** — extracao de texto de PDFs, analise Gemini (3 stages), exportacao

## Estrutura

```
scripts/                        → Pipeline Python
  main.py                       → CLI (search, screen, analyze, export, full)
  run_llm_all_papers.py         → Execucao da analise LLM em lote
  merge_papers_to_json.py       → Mescla registros + LLM → JSON enriquecido
  match_refs_to_studies.py      → Matching de citacoes entre estudos
  citation_index.py             → Indice de citacao (IC) para revisao sistematica
  generate_approved_ris.py      → Filtra RIS para estudos aprovados
  generate_bibtex.py            → Converte RIS aprovado → BibTeX (references.bib)
  generate_ic_table.py          → Gera tabela IC LaTeX com citeonline (tabelas/tabela_ic.tex)
  generate_latex_tables.py      → Regenera todas as tabelas derivadas do artigo (estudos-ano, instrumentos, autores, unidade-amostral, metodos)
  _rebuild_resumo.py            → Gera resumo estatistico (resumo_classificacao.xlsx) a partir de _classif_final.xlsx
  organize_bibtex.py            → Padroniza chaves BibTeX (formato curto) e atualiza citacoes nos .tex
  src/
    models.py                   → BibRecord (bibliografico) + PaperRecord (analise LLM)
    config.py                   → Carregamento YAML + validacao
    importer.py                 → Importacao de RIS/CSV/Excel
    dedup/                      → Deduplicacao DOI + fuzzy title
    extractors/                 → Extracao de texto de PDFs
    analyzers/                  → Analise via LLM (BaseAnalyzer ABC)
    screening/                  → Triagem pre-LLM (PRISMA)
    exporters/                  → Excel, CSV, RIS, JSON
    utils/                      → Logging
  keywords/                     → Queries de busca por base (.txt)
  questionnaires/               → Questionarios JSON para o LLM (3 stages)
data/1-records/                 → Registros bibliograficos + saidas do pipeline
  processed/                    → bib_records.json, bib_screened.json, duplicates_removed.csv
data/2-papers/                  → Artigos e classificacao
  2-2-papers.json               → JSON enriquecido (registros + LLM + triagem)
  2-2-papers-pdfs/              → 118 PDFs renomeados (nao versionados)
  2-1-papers_scripts/           → Scripts de renomeacao e verificacao
  _llm_checkpoint.json          → Checkpoint da analise LLM
  all_papers_llm_classif_final.xlsx → Classificacao revisada (somente leitura)
  resumo_classificacao.xlsx     → Resumo estatistico (gerado por _rebuild_resumo.py)
data/3-ref-bib/                → Referencias extraidas dos estudos
  refs_por_estudo/              → 54 JSONs com refs estruturadas + matching
  citation_index_results.json   → Indice de citacao por estudo (JSON)
  citation_index_report.txt     → Relatorio do indice de citacao
latex/                          → Artigo LaTeX (nao modificar via scripts)
figures/                        → Figuras para o artigo
docs/pipeline_extraction.md     → Metodologia e log de extracao
docs/update_reports/            → Relatorios de atualizacao do pipeline (propagate-update)
```

## Regras de Codigo

### Python
- Python 3.12+. Usar type hints em todas as funcoes.
- Cada modulo deve ter < 300 linhas. Se crescer, dividir.
- Usar `dataclasses` para modelos de dados, nunca dicionarios soltos.
- Configuracao via YAML (`config.yaml`), nunca hardcoded.
- Chaves API via variaveis de ambiente (`${GEMINI_API_KEY}`), nunca em codigo.
- Logging via `logging` stdlib — nunca `print()` em codigo de producao.
- Imports absolutos dentro de `src/` (ex: `from src.models import PaperRecord`).

### Padroes de Design
- Analisadores herdam de classes base abstratas (ABC).
- Pipeline orquestrado por `main.py` com CLI via `argparse`.

### Seguranca
- `config.yaml` deve estar no `.gitignore`. Versionar apenas `config.example.yaml`.
- Nunca commitar chaves API, tokens ou credenciais.

### Git
- Mensagens de commit em ingles, imperativo ("Add PDF extractor", nao "Added").
- Um commit por etapa logica concluida.
- Nao versionar: PDFs, dados processados, `__pycache__/`, `.venv/`.

### LaTeX
- O artigo em `latex/` e editado separadamente do pipeline.
- Classe `abntex2` em modo `article` (sem chapters).
- Citacoes via `abntex2cite` com opcao `alf` (ABNT alfabetico).
- Figuras referenciadas com `\graphicspath{{../figures/}}`.

## Fluxo de Trabalho

1. Ler o `README.md` e `docs/pipeline_extraction.md` antes de implementar.
2. Implementar uma etapa por vez.
3. Testar cada modulo isoladamente antes de integrar.

## Skills Disponiveis

- `/propagate-update` — Diagnostica alteracoes no pipeline, planeja a propagacao para estagios downstream, executa com confirmacao do usuario e gera relatorio. Usar sempre que uma alteracao num estagio do pipeline precise ser propagada (nova extracao, novas duplicatas, mudanca de criterios, correcoes manuais, re-analise LLM). Definicao em `.claude/commands/1-propagate-update.md`.

- `/escrever-artigo [secao]` — Redator academico para o artigo LaTeX. Sugere roteiro de topicos com marcacoes especiais (tabelas, figuras, quadros) baseado no Cap. 1 da tese, incorporando as inovacoes metodologicas do pndr_survey (5 bases, LLM, IC, deduplicacao). Somente escreve conteudo apos aprovacao explicita do usuario. Secoes: `introducao`, `politica`, `metodo`, `resultados`, `conclusao`, `resumo`, `todos`. Definicao em `.claude/commands/2-escrever-artigo.md`.

- `/processar-dados [comando]` — Converte, escreve e revisa scripts de manipulacao de dados e estatisticas descritivas do projeto tese para o contexto pndr_survey. Executa conversao R → Python, gera tabelas LaTeX/Excel, cria graficos academicos e valida datasets. Comandos: `explorar` (lista scripts R disponiveis), `converter [script.R]` (converte script especifico), `stats` (estatisticas descritivas), `plot [tipo]` (graficos), `validar` (validacao de dados). Exclui estimacao econometrica. Definicao em `.claude/commands/5-processar-dados.md`.

- `/revisor-latex [escopo]` — Revisor automatizado de comandos LaTeX. Verifica consistencia estrutural (ambientes, labels, referencias cruzadas), conformidade ABNT/abntex2 (\fonte{}, \cite/\citeonline, caption/label), tipografia (non-breaking spaces, espacamento) e corrige automaticamente erros seguros sem necessidade de aprovacao. Nunca altera conteudo textual, dados numericos ou conteudo de tabelas. Escopo: `main`, `metodo`, `resultados`, `politica`, `tabelas`, `todos` (padrao). Definicao em `.claude/commands/6-revisor-latex.md`.

- `/organizar-bib` — Organiza `latex/references.bib` com conformidade ABNT NBR 6023: renomeia chaves para formato curto (PrimeiroAutorAno, excluindo particulas e sufixos), resolve conflitos (segundo autor ou sufixo), ordena por sobrenome do 1o autor → ano → desambiguacao, corrige capitalizacao de titulos e atualiza citacoes em todos os `.tex`. Usa `scripts/organize_bibtex.py` com modos `--dry-run` (padrao), `--execute`, `--fix-titles` e `--archive`. Definicao em `.claude/commands/7-organizar-bib.md`.

## Dependencias

```
rapidfuzz>=3.0      # Deduplicacao fuzzy
rispy>=0.8          # Parsing RIS
unidecode>=1.3      # Normalizacao de texto
pdfplumber>=0.11    # Extracao de PDF
google-generativeai>=0.8  # API Gemini
pandas>=2.0         # Importacao CSV/Excel
openpyxl>=3.1       # Exportacao Excel
pyyaml>=6.0         # Configuracao
```

Instalar com: `pip install -r scripts/requirements.txt`

## Referencias

- **Projeto original (tese):** `C:\OneDrive\github\tese` (somente leitura, capitulo de referencia em `arquivos_latex/latex_tese/2-textuais/1-survey/`)
