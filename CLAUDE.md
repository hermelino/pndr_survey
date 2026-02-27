# CLAUDE.md — Regras do Projeto pndr_survey

## Contexto

Revisao sistematica (SLR) sobre instrumentos da PNDR. Duas fases:
1. **Coleta** — busca manual em bases academicas, importacao, deduplicacao
2. **Analise** — extracao de texto de PDFs, analise Gemini (3 stages), exportacao

## Estrutura

```
scripts/            → Pipeline Python (main.py e o ponto de entrada)
  src/
    models.py       → BibRecord (bibliografico) + PaperRecord (analise LLM)
    config.py       → Carregamento YAML + validacao
    importer.py     → Importacao de RIS/CSV/Excel
    dedup/          → Deduplicacao DOI + fuzzy title
    extractors/     → Extracao de texto de PDFs
    analyzers/      → Analise via LLM (BaseAnalyzer ABC)
    screening/      → Triagem pre-LLM (PRISMA)
    exporters/      → Excel, CSV, RIS, JSON
    utils/          → Logging
  keywords/         → Queries de busca por base (.txt)
  questionnaires/   → Questionarios JSON para o LLM
data/1-records/     → Registros bibliograficos + saidas do pipeline
data/2-papers/      → PDFs dos artigos (nao versionados)
latex/              → Artigo LaTeX (nao modificar via scripts)
figures/            → Figuras para o artigo
docs/pipeline_extraction.md → Metodologia e log de extracao
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
- Figuras referenciadas com `\graphicspath{{../figures/}}`.
- Bibliografia via `natbib` + `apalike`.

## Fluxo de Trabalho

1. Ler o `README.md` e `docs/pipeline_extraction.md` antes de implementar.
2. Implementar uma etapa por vez.
3. Testar cada modulo isoladamente antes de integrar.

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

- **Projeto original:** `C:\github\tese\survey_extraction_system` (somente leitura)
