# CLAUDE.md — Regras do Projeto pndr_survey

## Contexto

Revisão sistemática (SLR) sobre instrumentos da PNDR. Duas fases:
1. **Busca e coleta** — buscar em bases acadêmicas, deduplicar, baixar PDFs
2. **Análise e síntese** — extração de texto, análise Gemini (3 stages), exportação

## Estrutura

```
latex/              → Artigo LaTeX (não modificar via scripts)
scripts/            → Pipeline Python (main.py é o ponto de entrada)
  src/
    models.py       → BibRecord (bibliográfico) + PaperRecord (análise LLM)
    config.py       → Carregamento YAML + validação
    searchers/      → Busca em bases acadêmicas (BaseSearcher ABC)
    dedup/          → Deduplicação DOI + fuzzy title
    extractors/     → Extração de texto de PDFs
    analyzers/      → Análise via LLM (BaseAnalyzer ABC)
    exporters/      → Excel, CSV, RIS, JSON
    utils/          → Logging
  keywords/         → Estratégias de busca por base (.txt)
  questionnaires/   → Questionários JSON para o LLM
data/papers/        → PDFs dos artigos (não versionados)
data/processed/     → Resultados da análise (não versionados)
figures/            → Figuras para o artigo
docs/PLAN.md        → Plano de construção detalhado
```

## Regras de Código

### Python
- Python 3.12+. Usar type hints em todas as funções.
- Cada módulo deve ter < 300 linhas. Se crescer, dividir.
- Usar `dataclasses` para modelos de dados, nunca dicionários soltos.
- Configuração via YAML (`config.yaml`), nunca hardcoded.
- Chaves API via variáveis de ambiente (`${GEMINI_API_KEY}`), nunca em código ou `.env` versionado.
- Logging via `logging` stdlib — nunca `print()` em código de produção.
- Imports absolutos dentro de `src/` (ex: `from src.models import PaperRecord`).

### Padrões de Design
- Seguir a arquitetura do `slr-disasters-birth-outcomes` como referência.
- Extratores/analisadores herdam de classes base abstratas (ABC).
- Factory pattern para instanciar componentes a partir de config.
- Pipeline orquestrado por `main.py` com CLI via `argparse`.

### Segurança
- `config.yaml` deve estar no `.gitignore`. Versionar apenas `config.example.yaml`.
- Nunca commitar chaves API, tokens ou credenciais.
- Sanitizar nomes de arquivo antes de salvar (sem path traversal).

### Git
- Mensagens de commit em inglês, imperativo ("Add PDF extractor", não "Added" ou "Adding").
- Um commit por etapa lógica concluída.
- Não versionar: PDFs, dados processados, `__pycache__/`, `.venv/`.

### LaTeX
- O artigo em `latex/` é editado separadamente do pipeline.
- Figuras referenciadas com `\graphicspath{{../figures/}}`.
- Bibliografia via `natbib` + `apalike`.

## Fluxo de Trabalho

1. Ler o `docs/PLAN.md` antes de implementar qualquer etapa.
2. Implementar uma etapa por vez, na ordem do plano.
3. Testar cada módulo isoladamente antes de integrar.
4. Ao concluir uma etapa, atualizar o status na tabela do `docs/PLAN.md`.

## Dependências

```
# Busca e coleta
requests>=2.31
beautifulsoup4>=4.12
rapidfuzz>=3.0
rispy>=0.8
unidecode>=1.3

# Extração e análise
pdfplumber>=0.11
google-generativeai>=0.8

# Exportação
pandas>=2.0
openpyxl>=3.1

# Configuração
pyyaml>=6.0
```

Instalar com: `pip install -r scripts/requirements.txt`

## Referências

- **Projeto original:** `C:\github\tese\survey_extraction_system` (somente leitura, não modificar)
- **Referência de arquitetura:** `C:\github\slr-disasters-birth-outcomes`
