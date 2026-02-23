# Plano de Construção — pndr_survey

## Visão Geral

Reimplementação limpa do sistema `survey_extraction_system` (projeto "tese") como pipeline
autônomo para revisão sistemática da literatura sobre PNDR. Cobre duas fases:

1. **Busca e coleta** — identificar artigos em bases acadêmicas, baixar PDFs, deduplicar
2. **Análise e síntese** — extrair informações estruturadas via LLM, exportar resultados

O projeto `slr-disasters-birth-outcomes` serve como referência de arquitetura.

---

## Diagnóstico do Sistema Original

| Aspecto | Estado Atual | Problema |
|---------|-------------|----------|
| **EconPapers extractor** | HTTP + BeautifulSoup, funcional | Código razoável, precisa limpeza e testes |
| **ANPEC extractor** | Lê Excel pré-exportado, baixa URLs | Não busca — depende de planilha manual |
| **CAPES extractor** | Selenium, método faltando | Quebrado: `search_capes_basic()` não implementado |
| **Keywords** | 4 arquivos .txt bem documentados | Migrar diretamente |
| `llm_analyzer.py` | 1.361 linhas, monolítico | Mistura extração de PDF, chamadas API, parsing, exportação |
| Exportação | 3+ conversores JSON→Excel redundantes | Duplicação de código |
| Configuração | `settings.yaml` + `.env` com API key exposta | Inseguro, não portável |
| Citation analysis | Subsistema isolado (430 citações, 3 algoritmos) | Útil mas separado do pipeline principal |
| Questionários | `questionario.json` + `questionario_etapas.json` | Bem feitos, migrar diretamente |

---

## Arquitetura Alvo

```
scripts/
├── main.py                     # Ponto de entrada CLI
├── config.yaml                 # Configuração (não versionado)
├── config.example.yaml         # Template de configuração
├── requirements.txt
│
├── questionnaires/             # Questionários JSON para análise LLM
│   ├── stage_1_screening.json  # Triagem: é estudo empírico sobre PNDR?
│   ├── stage_2_methods.json    # Metodologia: métodos, variáveis, período
│   └── stage_3_results.json    # Resultados: instrumentos, efeitos, conclusões
│
├── keywords/                   # Estratégias de busca por base
│   ├── econpapers.txt
│   ├── google_scholar.txt
│   ├── capes.txt
│   └── scopus.txt
│
├── src/
│   ├── __init__.py
│   ├── models.py               # BibRecord + PaperRecord dataclasses
│   ├── config.py               # Carregamento YAML + validação
│   │
│   ├── searchers/              # Fase 1: Busca e coleta
│   │   ├── __init__.py
│   │   ├── base.py             # BaseSearcher ABC
│   │   ├── econpapers.py       # Busca automática via HTTP
│   │   ├── google_scholar.py   # Gera query + instruções manuais
│   │   ├── capes.py            # Gera query + instruções manuais
│   │   └── scopus.py           # API ou manual (opcional)
│   │
│   ├── dedup/                  # Deduplicação entre bases
│   │   ├── __init__.py
│   │   └── deduplicator.py     # DOI exato + fuzzy title
│   │
│   ├── extractors/             # Fase 2: Extração de texto
│   │   ├── __init__.py
│   │   └── pdf_extractor.py    # Extração de texto de PDFs (pdfplumber)
│   │
│   ├── analyzers/              # Fase 2: Análise LLM
│   │   ├── __init__.py
│   │   ├── base.py             # BaseAnalyzer ABC
│   │   └── gemini_analyzer.py  # Chamadas Gemini + parsing de respostas
│   │
│   ├── exporters/              # Exportação de resultados
│   │   ├── __init__.py
│   │   ├── excel_exporter.py   # Exportação Excel (openpyxl)
│   │   ├── csv_exporter.py     # Exportação CSV
│   │   └── ris_exporter.py     # Exportação RIS (Zotero/Mendeley)
│   │
│   └── utils/
│       ├── __init__.py
│       └── logger.py           # Logging estruturado
│
└── tests/                      # (futuro)
```

### Princípios de Design (inspirados no slr-disasters)

1. **Duas dataclasses centrais** — `BibRecord` (metadados bibliográficos) + `PaperRecord` (análise LLM)
2. **BaseSearcher ABC** — interface comum para todas as bases (`build_query`, `search`, `import_from_file`)
3. **Deduplicação em 2 fases** — DOI exato + fuzzy title (rapidfuzz)
4. **Configuração YAML** com suporte a `${ENV_VARS}` para chaves API
5. **CLI via argparse** — `--dry-run`, `--databases`, `--stage`, `--import-*`
6. **Separação de responsabilidades** — cada módulo < 300 linhas
7. **Logging dual** — arquivo (DEBUG) + console (INFO)
8. **Saída timestamped** — `output/YYYYMMDD_HHMMSS/`
9. **Degradação graceful** — bases sem API geram query + instruções manuais

---

## Etapas de Construção

### Etapa 0 — Busca e Coleta de Artigos

Esta etapa implementa a **Fase 1** do pipeline: identificar artigos relevantes em
múltiplas bases acadêmicas, baixar PDFs quando possível, e deduplicar resultados.

#### 0A — Modelo de dados bibliográfico (`BibRecord`)

**Arquivo:** `src/models.py`

```python
@dataclass
class BibRecord:
    # Identidade
    source_db: str              # "econpapers", "google_scholar", "capes", "scopus"
    source_id: str              # ID na base de origem
    doi: Optional[str]

    # Metadados bibliográficos
    title: str
    authors: List[str]
    year: Optional[int]
    journal: Optional[str]
    volume: Optional[str]
    pages: Optional[str]

    # Conteúdo
    abstract: Optional[str]
    keywords: List[str]
    url: Optional[str]
    pdf_url: Optional[str]
    language: Optional[str]

    # Classificação temática
    matched_instruments: List[str]  # FNE, FNO, FCO, FDNE, incentivos fiscais...
    matched_keywords: List[str]     # Keywords que deram match na busca

    # Deduplicação
    is_duplicate: bool = False
    duplicate_of: Optional[str] = None

    def completeness_score(self) -> int:
        """Pontuação para escolher qual duplicata manter."""
```

**Critérios de conclusão:**
- [ ] `BibRecord` instancia com campos mínimos (title, source_db)
- [ ] `completeness_score()` prioriza registros com DOI + abstract

---

#### 0B — Searchers (busca por base)

**Arquivos:** `src/searchers/base.py`, `src/searchers/econpapers.py`, etc.

**Interface comum (`BaseSearcher`):**
```python
class BaseSearcher(ABC):
    @abstractmethod
    def build_query(self) -> str:
        """Constrói a query de busca na sintaxe da base."""

    @abstractmethod
    def search(self) -> int:
        """Executa busca, retorna número de resultados."""

    @abstractmethod
    def fetch_records(self) -> List[BibRecord]:
        """Recupera registros e normaliza para BibRecord."""

    def import_from_file(self, filepath: Path) -> List[BibRecord]:
        """Importa resultados exportados manualmente (RIS/CSV)."""

    def save_query_instructions(self, output_dir: Path) -> None:
        """Salva query formatada + instruções de busca manual."""
```

**Estratégia por base:**

| Base | Modo | Implementação |
|------|------|---------------|
| **EconPapers/RePEc** | Automático | HTTP requests + BeautifulSoup. Reescrever a partir do `econpapers_extractor.py` original, melhorando parsing e rate limiting |
| **Google Scholar** | Semi-automático | Gerar query booleana + instruções para usar Publish or Perish ou Zotero Connector. Importar via RIS/CSV |
| **CAPES Periódicos** | Semi-automático | Gerar query booleana formatada para o portal. Instruções de busca + exportação. Importar via RIS/CSV |
| **Scopus** | Opcional | Se houver acesso via CAPES proxy: API (pybliometrics) ou manual. Importar via CSV/RIS |

**Keywords (migrar do original):**
- Manter a estrutura de 3 blocos: instrumentos AND organizações AND (geografia)
- Adaptar sintaxe por base (EconPapers, Scopus, Google Scholar, CAPES)
- Versões em português e inglês

**Critérios de conclusão:**
- [ ] EconPapers: `search()` retorna resultados reais
- [ ] Google Scholar: `save_query_instructions()` gera arquivo com query + passos
- [ ] CAPES: `save_query_instructions()` gera arquivo com query + URL
- [ ] `import_from_file()` lê RIS e CSV para todas as bases

---

#### 0C — Deduplicação

**Arquivo:** `src/dedup/deduplicator.py`

**Algoritmo (2 fases, igual ao slr-disasters):**

1. **Fase 1 — DOI exato:** normalizar DOI (lowercase, strip prefixes), agrupar, manter o
   mais completo (`completeness_score`)
2. **Fase 2 — Fuzzy title:** normalizar títulos (unidecode, lowercase, remover stopwords),
   comparar com `rapidfuzz.fuzz.token_sort_ratio`, threshold configurável (padrão 90%).
   Verificação: match só se mesmo ano E (mesmo primeiro autor OU mesmo periódico)

**Saídas:**
- `unique_records`: lista deduplicada
- `duplicate_records`: removidos (trilha de auditoria)
- Contadores: duplicatas por DOI vs. por título

**Critérios de conclusão:**
- [ ] DOI duplicados removidos corretamente
- [ ] Fuzzy matching identifica variações de título
- [ ] Registro mais completo é mantido como keeper
- [ ] CSV de auditoria com duplicatas removidas

---

#### 0D — Download de PDFs

**Arquivo:** `src/searchers/base.py` (método compartilhado) ou `src/utils/downloader.py`

**Responsabilidades:**
- Baixar PDFs a partir de `BibRecord.pdf_url`
- Rate limiting (2s entre downloads)
- Nomeação: `{source_db}_{source_id}.pdf` ou `{primeiro_autor}_{ano}.pdf`
- Verificar integridade (arquivo > 10KB, header é `%PDF`)
- Registrar falhas sem interromper o batch

**Critérios de conclusão:**
- [ ] PDFs baixados em `data/papers/`
- [ ] Falhas de download registradas no log sem parar o processo
- [ ] Arquivos corrompidos detectados e descartados

---

### Etapa 1 — Fundação (config + modelos completos)

**Arquivos:** `src/models.py`, `src/config.py`, `config.example.yaml`

**`src/models.py` — PaperRecord (para análise LLM):**
```python
@dataclass
class PaperRecord:
    # Vínculo com BibRecord
    bib: BibRecord              # Referência aos metadados bibliográficos
    file_hash: str              # SHA-256 do PDF

    # Conteúdo extraído do PDF
    text_length: int
    text_preview: str           # Primeiros 500 chars

    # Análise LLM (3 estágios)
    stage_1: Optional[Dict]     # Triagem
    stage_2: Optional[Dict]     # Metodologia
    stage_3: Optional[Dict]     # Resultados

    # Classificação derivada da análise
    is_empirical: Optional[bool]
    pndr_instrument: Optional[str]  # FNE, FNO, FCO, FDNE, etc.
    econometric_method: Optional[str]
    time_period: Optional[str]
    geographic_scope: Optional[str]

    # Metadados de processamento
    analyzed_at: Optional[str]
    model_used: Optional[str]
    processing_errors: List[str]
```

**`config.example.yaml` (atualizado com busca):**
```yaml
# --- Busca ---
search:
  databases: ["econpapers", "google_scholar", "capes"]
  keywords_dir: "keywords"
  date_range:
    start: 2000
    end: 2025
  max_results_per_db: 1000

# --- Deduplicação ---
dedup:
  fuzzy_threshold: 90
  title_normalization: true

# --- LLM ---
llm:
  provider: gemini
  model: gemini-2.0-flash
  api_key: "${GEMINI_API_KEY}"
  temperature: 0.1
  max_tokens_input: 100000
  rate_limit_seconds: 4

# --- Caminhos ---
paths:
  papers_dir: "../data/papers"
  questionnaires_dir: "questionnaires"

# --- Saída ---
output:
  directory: "../data/processed"
  formats: ["excel", "csv", "json"]
  timestamp: true

# --- Logging ---
logging:
  level: INFO
  file_level: DEBUG
```

**Critérios de conclusão:**
- [ ] `BibRecord` e `PaperRecord` instanciam sem erros
- [ ] `load_config("config.yaml")` retorna objeto tipado com seções search + dedup + llm
- [ ] Validação falha com mensagem clara se `GEMINI_API_KEY` não definida

---

### Etapa 2 — Extrator de PDF

**Arquivo:** `src/extractors/pdf_extractor.py`

**Responsabilidades:**
- Extrair texto de PDF via `pdfplumber`
- Limitar a `max_tokens_input` caracteres (configurável)
- Normalizar texto (remover hifenização, espaços múltiplos)
- Calcular hash SHA-256 do arquivo
- Retornar `PaperRecord` parcialmente preenchido (vinculado ao `BibRecord`)

**Interface:**
```python
class PdfExtractor:
    def extract(self, pdf_path: Path, bib: BibRecord) -> PaperRecord
    def extract_batch(self, directory: Path, records: List[BibRecord]) -> List[PaperRecord]
```

**Migração do original:**
- `llm_analyzer.py:load_papers_from_directory()` → refatorar
- `file_utils.py:get_file_hash()` → simplificar
- **Remover:** conversão DOC/DOCX (assumir PDFs)

**Critérios de conclusão:**
- [ ] Extrai texto de PDF real sem erro
- [ ] Trunca corretamente em `max_tokens_input`
- [ ] Hash é determinístico (mesmo arquivo → mesmo hash)

---

### Etapa 3 — Analisador LLM (Triagem — Stage 1)

**Arquivos:** `src/analyzers/base.py`, `src/analyzers/gemini_analyzer.py`

**`base.py` — Interface:**
```python
class BaseAnalyzer(ABC):
    @abstractmethod
    def analyze(self, paper: PaperRecord, questionnaire: Dict) -> Dict
```

**`gemini_analyzer.py`:**
- Chamada à API Gemini via SDK `google.generativeai`
- Rate limiting configurável (padrão: 4s entre chamadas)
- Retry com backoff exponencial (max 3 tentativas)
- Parsing de resposta: extração de pares pergunta-resposta
- Tratamento de erros: registrar em `PaperRecord.processing_errors`

**Migração do original:**
- `llm_analyzer.py:call_gemini_api_simple()` → refatorar
- `llm_analyzer.py:parse_simple_response()` → refatorar
- `llm_analyzer.py:analyze_paper()` → simplificar
- **Remover:** chamadas HTTP diretas (usar apenas SDK)

**Critérios de conclusão:**
- [ ] Analisa 1 paper com questionário stage_1
- [ ] Resposta parseada em dicionário estruturado
- [ ] Rate limiting funciona (>= 4s entre chamadas)
- [ ] Falha de API não interrompe o batch

---

### Etapa 4 — Analisador LLM (Stages 2 e 3)

**Arquivo:** `src/analyzers/gemini_analyzer.py` (extensão)

**Adicionar:**
- `analyze_stage()` — aplica questionário específico da etapa
- `analyze_pipeline()` — sequência Stage 1 → filtra empíricos → Stages 2+3
- Filtro: apenas papers com `is_empirical == True` passam para Stage 2

**Migração do original:**
- `llm_analyzer.py:analyze_stage()` → refatorar
- `llm_analyzer.py:filter_scientific_studies()` → simplificar
- `questionario_etapas.json` → dividir em 3 arquivos separados

**Critérios de conclusão:**
- [ ] Pipeline Stage 1→2→3 executa sem erros
- [ ] Papers não-empíricos são filtrados corretamente
- [ ] Resultados de cada etapa salvos no `PaperRecord`

---

### Etapa 5 — Exportadores

**Arquivos:** `src/exporters/excel_exporter.py`, `src/exporters/csv_exporter.py`, `src/exporters/ris_exporter.py`

**Excel (openpyxl):**
- Sheet "Resultados": uma linha por paper, colunas = campos do BibRecord + PaperRecord
- Sheet "Resumo": contagens por instrumento PNDR, método econométrico, período
- Formatação: cabeçalho colorido, largura automática, freeze panes

**CSV:**
- UTF-8-BOM + ponto-e-vírgula (padrão brasileiro)
- Mesmo esquema do Excel

**RIS:**
- Formato padrão para importação em Zotero/Mendeley
- Mapeamento BibRecord → campos RIS (via `rispy`)

**JSON:**
- Dump direto via `dataclasses.asdict()`

**Critérios de conclusão:**
- [ ] Excel abre no Windows sem caracteres quebrados
- [ ] CSV importa no R/pandas sem problemas de encoding
- [ ] RIS importa no Zotero corretamente
- [ ] JSON roundtrip: salvar + carregar preserva todos os campos

---

### Etapa 6 — Orquestrador (main.py)

**Arquivo:** `scripts/main.py`

**CLI (argparse) — atualizado com fase de busca:**
```
usage: main.py [-h] [--config CONFIG] COMMAND [options]

Pipeline de revisão sistemática sobre PNDR

commands:
  search      Buscar artigos nas bases acadêmicas
  analyze     Analisar PDFs coletados via LLM
  export      Exportar resultados
  full        Executar pipeline completo

search options:
  --databases DB [DB ...]     Bases para buscar (default: todas do config)
  --import-econpapers FILE    Importar resultados EconPapers (RIS/CSV)
  --import-scholar FILE       Importar resultados Google Scholar (RIS/CSV)
  --import-capes FILE         Importar resultados CAPES (RIS/CSV)
  --import-scopus FILE        Importar resultados Scopus (RIS/CSV)
  --skip-dedup                Pular deduplicação
  --skip-download             Não baixar PDFs
  --dry-run                   Mostrar queries sem executar

analyze options:
  --stage {1,2,3,all}         Etapa da análise (default: all)
  --max-papers N              Limitar número de papers
  --input-dir DIR             Diretório com PDFs (override config)

common options:
  --config CONFIG             Arquivo de configuração YAML
  --output-dir DIR            Diretório de saída (override config)
  --verbose                   Logging DEBUG no console
```

**Pipeline completo (`full`):**
```
1.  Carregar config.yaml
2.  Configurar logging + criar diretório timestamped
3.  FASE 1 — BUSCA
    3a. Para cada base configurada: build_query + search/save_instructions
    3b. Importar resultados manuais (se --import-* fornecidos)
    3c. Deduplicar (DOI + fuzzy title)
    3d. Baixar PDFs disponíveis
    3e. Exportar lista bibliográfica (CSV + RIS)
4.  FASE 2 — ANÁLISE
    4a. Extrair texto dos PDFs (PdfExtractor)
    4b. Stage 1: triagem (é estudo empírico sobre PNDR?)
    4c. Filtrar empíricos
    4d. Stage 2: metodologia
    4e. Stage 3: resultados
5.  Exportar resultados finais (Excel + CSV + JSON)
6.  Imprimir resumo (estatísticas PRISMA-like)
```

**Critérios de conclusão:**
- [ ] `python main.py search --dry-run` mostra queries de todas as bases
- [ ] `python main.py search --databases econpapers` busca e exporta resultados
- [ ] `python main.py search --import-scholar results.ris` importa e deduplica
- [ ] `python main.py analyze --stage 1 --max-papers 3` analisa 3 papers
- [ ] `python main.py full` executa pipeline completo
- [ ] Saída organizada em `output/YYYYMMDD_HHMMSS/`

---

### Etapa 7 — Migração de Questionários e Dados

**Ações:**
1. Converter `questionario_etapas.json` em 3 arquivos separados
2. Migrar keywords dos 4 arquivos `.txt` originais, adaptando por base
3. Copiar PDFs já coletados para `data/papers/`
4. Validar que o pipeline reproduz resultados comparáveis ao original

**Critérios de conclusão:**
- [ ] 3 arquivos JSON em `questionnaires/`
- [ ] Keywords adaptados em `keywords/`
- [ ] Pipeline executa com os dados migrados
- [ ] Resultados coerentes com análise original (spot-check de 5 papers)

---

### Etapa 8 — Citation Analysis (futuro)

O subsistema de análise de citações cruzadas (`citation_analysis_project/`) será
avaliado separadamente. Possibilidades:
- Integrar como módulo opcional em `pndr_survey`
- Manter como ferramenta standalone
- Decisão adiada até Etapas 0-7 concluídas

---

### Etapa 9 — Redação do Artigo LaTeX (futuro)

Migração gradual do conteúdo dos capítulos da tese para `latex/main.tex`:
- Adaptar linguagem de capítulo de tese para artigo independente
- Remover referências cruzadas entre capítulos
- Atualizar tabelas e figuras com resultados do novo pipeline
- Incluir diagrama PRISMA atualizado

---

## Dependências do Projeto

```
# requirements.txt

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

**Removidas em relação ao original:**
- `python-docx`, `reportlab` (sem conversão DOC→PDF)
- `selenium` (substituído por HTTP para EconPapers, manual para o resto)
- `Levenshtein`, `jellyfish` (substituídos por `rapidfuzz`)
- `websocket-client` (não usado)

---

## Cronograma Sugerido

| Etapa | Descrição | Prioridade |
|-------|-----------|------------|
| 0A | BibRecord + modelo bibliográfico | Imediata |
| 0B | Searchers (EconPapers automático + manuais) | Imediata |
| 0C | Deduplicação (DOI + fuzzy) | Imediata |
| 0D | Download de PDFs | Imediata |
| 1 | Config + PaperRecord | Imediata |
| 2 | Extrator de PDF | Alta |
| 3 | Analisador LLM (Stage 1) | Alta |
| 4 | Analisador LLM (Stages 2-3) | Alta |
| 5 | Exportadores (Excel/CSV/RIS/JSON) | Alta |
| 6 | Orquestrador (main.py) | Alta |
| 7 | Migração questionários + keywords + dados | Média |
| 8 | Citation analysis | Baixa (futuro) |
| 9 | Artigo LaTeX | Baixa (futuro) |
