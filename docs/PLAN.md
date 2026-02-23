# Plano de Construção — pndr_survey

## Visão Geral

Reimplementação limpa do sistema `survey_extraction_system` (projeto "tese") como pipeline
autônomo para análise de artigos via LLM. O projeto `slr-disasters-birth-outcomes` serve
como referência de arquitetura.

---

## Diagnóstico do Sistema Original

| Aspecto | Estado Atual | Problema |
|---------|-------------|----------|
| `llm_analyzer.py` | 1.361 linhas, monolítico | Mistura extração de PDF, chamadas API, parsing, exportação |
| Exportação | 3+ conversores JSON→Excel redundantes | Duplicação de código |
| Configuração | `settings.yaml` + `.env` com API key exposta | Inseguro, não portável |
| Extractors | ANPEC/CAPES/EconPapers — incompletos, deprecated | Não fazem parte do pipeline real |
| Citation analysis | Subsistema isolado (430 citações, 3 algoritmos) | Útil mas separado do pipeline principal |
| Testes | Apenas scripts manuais na raiz | Sem cobertura automatizada |
| Questionários | `questionario.json` + `questionario_etapas.json` | Bem feitos, migrar diretamente |

**Código essencial a migrar:** ~2.500 linhas (de ~15.000 totais)

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
├── src/
│   ├── __init__.py
│   ├── models.py               # PaperRecord dataclass
│   ├── config.py               # Carregamento YAML + validação
│   │
│   ├── extractors/
│   │   ├── __init__.py
│   │   └── pdf_extractor.py    # Extração de texto de PDFs (pdfplumber)
│   │
│   ├── analyzers/
│   │   ├── __init__.py
│   │   ├── base.py             # BaseAnalyzer ABC
│   │   └── gemini_analyzer.py  # Chamadas Gemini + parsing de respostas
│   │
│   ├── exporters/
│   │   ├── __init__.py
│   │   ├── excel_exporter.py   # Exportação Excel (openpyxl)
│   │   └── csv_exporter.py     # Exportação CSV
│   │
│   └── utils/
│       ├── __init__.py
│       └── logger.py           # Logging estruturado
│
└── tests/                      # (futuro)
```

### Princípios de Design (inspirados no slr-disasters)

1. **Dataclass central** (`PaperRecord`) — esquema único normalizado
2. **Configuração YAML** com suporte a `${ENV_VARS}` para chaves API
3. **CLI via argparse** — `--dry-run`, `--stage`, `--input-dir`, `--output-dir`
4. **Separação de responsabilidades** — cada módulo < 300 linhas
5. **Logging dual** — arquivo (DEBUG) + console (INFO)
6. **Saída timestamped** — `output/YYYYMMDD_HHMMSS/`

---

## Etapas de Construção

### Etapa 1 — Fundação (config + modelo de dados)

**Arquivos:** `src/models.py`, `src/config.py`, `config.example.yaml`

**`src/models.py` — PaperRecord:**
```python
@dataclass
class PaperRecord:
    # Identidade
    filename: str
    file_hash: str              # SHA-256 do PDF

    # Metadados bibliográficos
    title: str
    authors: List[str]
    year: Optional[int]
    journal: Optional[str]
    doi: Optional[str]

    # Conteúdo extraído
    text_length: int            # Caracteres extraídos do PDF
    text_preview: str           # Primeiros 500 chars

    # Análise LLM
    stage_1: Optional[Dict]     # Triagem
    stage_2: Optional[Dict]     # Metodologia
    stage_3: Optional[Dict]     # Resultados

    # Classificação
    is_empirical: Optional[bool]    # Determinado na Etapa 1
    pndr_instrument: Optional[str]  # FNE, FNO, FCO, FDNE, etc.

    # Metadados de processamento
    analyzed_at: Optional[str]
    model_used: Optional[str]
    processing_errors: List[str]
```

**`src/config.py`:**
- Carregar YAML com resolução de `${ENV_VARS}`
- Dataclasses: `LLMConfig`, `PathsConfig`, `OutputConfig`
- Validação: chave API obrigatória, diretório de papers deve existir

**`config.example.yaml`:**
```yaml
llm:
  provider: gemini
  model: gemini-2.0-flash
  api_key: "${GEMINI_API_KEY}"
  temperature: 0.1
  max_tokens_input: 100000
  rate_limit_seconds: 4

paths:
  papers_dir: "../data/papers"
  questionnaires_dir: "questionnaires"

output:
  directory: "../data/processed"
  formats: ["excel", "csv", "json"]
  timestamp: true

logging:
  level: INFO
  file_level: DEBUG
```

**Critérios de conclusão:**
- [ ] `PaperRecord` instancia sem erros
- [ ] `load_config("config.yaml")` retorna objeto tipado
- [ ] Validação falha com mensagem clara se `GEMINI_API_KEY` não definida

---

### Etapa 2 — Extrator de PDF

**Arquivo:** `src/extractors/pdf_extractor.py`

**Responsabilidades:**
- Extrair texto de PDF via `pdfplumber`
- Limitar a `max_tokens_input` caracteres (configurável)
- Normalizar texto (remover hifenização, espaços múltiplos)
- Calcular hash SHA-256 do arquivo
- Retornar `PaperRecord` parcialmente preenchido

**Migração do original:**
- `llm_analyzer.py:load_papers_from_directory()` → refatorar
- `file_utils.py:get_file_hash()` → simplificar
- **Remover:** conversão DOC/DOCX (assumir que todos os papers já são PDF)

**Interface:**
```python
class PdfExtractor:
    def extract(self, pdf_path: Path) -> PaperRecord
    def extract_batch(self, directory: Path) -> List[PaperRecord]
```

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
- **Remover:** chamadas HTTP diretas (usar apenas SDK), cache manual

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

**Arquivos:** `src/exporters/excel_exporter.py`, `src/exporters/csv_exporter.py`

**Excel (openpyxl):**
- Sheet "Resultados": uma linha por paper, colunas = campos do PaperRecord
- Sheet "Resumo": contagens por instrumento PNDR, método econométrico, período
- Formatação: cabeçalho colorido, largura automática, freeze panes

**CSV:**
- UTF-8-BOM + ponto-e-vírgula (padrão brasileiro)
- Mesmo esquema do Excel

**JSON:**
- Dump direto de `List[PaperRecord]` via `dataclasses.asdict()`

**Migração do original:**
- `excel_converter.py` → reescrever do zero, mais simples
- **Remover:** flatten de dicts aninhados (usar schema plano desde o início)

**Critérios de conclusão:**
- [ ] Excel abre no Windows sem caracteres quebrados
- [ ] CSV importa no R/pandas sem problemas de encoding
- [ ] JSON roundtrip: salvar + carregar preserva todos os campos

---

### Etapa 6 — Orquestrador (main.py)

**Arquivo:** `scripts/main.py`

**CLI (argparse):**
```
usage: main.py [-h] [--config CONFIG] [--stage {1,2,3,all}]
               [--input-dir DIR] [--output-dir DIR]
               [--dry-run] [--verbose] [--max-papers N]

Análise automatizada de artigos sobre PNDR via LLM

options:
  --config CONFIG       Arquivo de configuração YAML (default: config.yaml)
  --stage {1,2,3,all}   Etapa da análise (default: all)
  --input-dir DIR       Diretório com PDFs (override config)
  --output-dir DIR      Diretório de saída (override config)
  --dry-run             Listar papers sem analisar
  --verbose             Logging DEBUG no console
  --max-papers N        Limitar número de papers (para testes)
```

**Pipeline:**
```
1. Carregar config.yaml
2. Configurar logging
3. Criar diretório de saída timestamped
4. Extrair texto dos PDFs (PdfExtractor)
5. Se --stage=1 ou all:  analisar Stage 1 (triagem)
6. Se --stage=2 ou all:  filtrar empíricos → analisar Stage 2
7. Se --stage=3 ou all:  analisar Stage 3
8. Exportar resultados (Excel + CSV + JSON)
9. Imprimir resumo
```

**Critérios de conclusão:**
- [ ] `python main.py --dry-run` lista papers sem chamar API
- [ ] `python main.py --stage 1 --max-papers 3` analisa 3 papers
- [ ] `python main.py` executa pipeline completo
- [ ] Saída organizada em `output/YYYYMMDD_HHMMSS/`

---

### Etapa 7 — Migração de Questionários e Dados

**Ações:**
1. Converter `questionario_etapas.json` em 3 arquivos separados
2. Copiar PDFs relevantes para `data/papers/`
3. Validar que o pipeline reproduz resultados comparáveis ao original

**Critérios de conclusão:**
- [ ] 3 arquivos JSON em `questionnaires/`
- [ ] Pipeline executa com os questionários migrados
- [ ] Resultados coerentes com análise original (spot-check de 5 papers)

---

### Etapa 8 — Citation Analysis (futuro)

O subsistema de análise de citações cruzadas (`citation_analysis_project/`) será
avaliado separadamente. Possibilidades:
- Integrar como módulo opcional em `pndr_survey`
- Manter como ferramenta standalone
- Decisão adiada até Etapas 1-7 concluídas

---

### Etapa 9 — Redação do Artigo LaTeX (futuro)

Migração gradual do conteúdo dos capítulos da tese para `latex/main.tex`:
- Adaptar linguagem de capítulo de tese para artigo independente
- Remover referências cruzadas entre capítulos
- Atualizar tabelas e figuras com resultados do novo pipeline

---

## Dependências do Projeto

```
# requirements.txt
pdfplumber>=0.11
google-generativeai>=0.8
pandas>=2.0
openpyxl>=3.1
pyyaml>=6.0
```

**Removidas em relação ao original:**
- `python-docx`, `reportlab` (sem conversão DOC→PDF)
- `requests` (usar SDK em vez de HTTP direto)
- `Levenshtein`, `jellyfish` (citation analysis adiado)
- `BeautifulSoup4`, `lxml` (sem web scraping)
- `websocket-client` (não usado)

---

## Cronograma Sugerido

| Etapa | Descrição | Prioridade |
|-------|-----------|------------|
| 1 | Config + modelo de dados | Imediata |
| 2 | Extrator de PDF | Imediata |
| 3 | Analisador LLM (Stage 1) | Imediata |
| 4 | Analisador LLM (Stages 2-3) | Alta |
| 5 | Exportadores | Alta |
| 6 | Orquestrador (main.py) | Alta |
| 7 | Migração questionários + dados | Média |
| 8 | Citation analysis | Baixa (futuro) |
| 9 | Artigo LaTeX | Baixa (futuro) |
