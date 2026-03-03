# =============================================================================
# pndr_survey — Makefile de Reprodutibilidade
# =============================================================================
# Pipeline completo para regenerar todos os outputs do zero.
# Requer: Python 3.12+, R, PDFs em data/2-papers/2-2-papers-pdfs/
#
# Quick start:
#   make setup      # Instalar dependências
#   make all        # Pipeline completo (import → analyze → tables → figures → pdf)
#   make clean      # Limpar outputs gerados
#
# Etapas individuais:
#   make import     # Importar registros das 5 bases
#   make screen     # Triagem pré-LLM
#   make analyze    # Análise LLM (requer GEMINI_API_KEY e PDFs)
#   make merge      # Mesclar registros + LLM
#   make citations  # Matching de citações + índice
#   make references # Gerar RIS + BibTeX aprovados
#   make tables     # Gerar tabelas LaTeX
#   make figures    # Gerar figuras (mapas, gráficos)
#   make latex      # Compilar PDF do artigo
# =============================================================================

# --- Variáveis ---
PYTHON := python
PIP := pip
SCRIPTS_DIR := scripts
DATA_DIR := data
LATEX_DIR := latex
FIGURES_DIR := figures

# Arquivos de entrada (versionados)
SCOPUS_RIS := $(DATA_DIR)/1-records/1-1-records-scopus/scopus_20260225.ris
SCIELO_RIS := $(DATA_DIR)/1-records/1-2-records-scielo/scielo_20260226.ris
CAPES_RIS := $(DATA_DIR)/1-records/1-3-records-capes/capes_20260224.ris
ECONPAPERS_RIS := $(DATA_DIR)/1-records/1-4-records-econpapers/econpapers_20260224.ris
ANPEC_XLSX := $(DATA_DIR)/1-records/1-5-records-anpec/anpec_20260225.xlsx

# Outputs intermediários (gerados, não versionados)
BIB_RECORDS := $(DATA_DIR)/1-records/processed/bib_records.json
BIB_SCREENED := $(DATA_DIR)/1-records/processed/bib_screened.json
PAPERS_JSON := $(DATA_DIR)/2-papers/2-2-papers.json
CITATION_INDEX := $(DATA_DIR)/3-ref-bib/citation_index_results.json

# Outputs finais LaTeX
APPROVED_RIS := $(DATA_DIR)/3-ref-bib/approved_studies.ris
REFERENCES_BIB := $(LATEX_DIR)/references.bib
TABELA_IC := $(LATEX_DIR)/tabela_ic.tex
ARTICLE_PDF := $(LATEX_DIR)/main.pdf

# --- Phony targets ---
.PHONY: all setup import screen analyze merge citations references tables figures latex clean help

# --- Default target ---
all: setup import screen merge citations references tables figures latex
	@echo ""
	@echo "=========================================="
	@echo "Pipeline completo executado com sucesso!"
	@echo "=========================================="
	@echo ""
	@echo "Outputs gerados:"
	@echo "  - Artigo PDF: $(ARTICLE_PDF)"
	@echo "  - Registros processados: $(BIB_RECORDS)"
	@echo "  - JSON enriquecido: $(PAPERS_JSON)"
	@echo "  - Índice de citação: $(CITATION_INDEX)"
	@echo ""

# --- Setup ---
setup:
	@echo "==> Instalando dependências..."
	cd $(SCRIPTS_DIR) && $(PIP) install -r requirements.txt
	@echo ""
	@echo "==> Verificando config.yaml..."
	@if not exist "$(SCRIPTS_DIR)\config.yaml" ( \
		echo "[AVISO] config.yaml não encontrado. Copiando de config.example.yaml..." && \
		copy "$(SCRIPTS_DIR)\config.example.yaml" "$(SCRIPTS_DIR)\config.yaml" && \
		echo "" && \
		echo "ATENÇÃO: Edite scripts/config.yaml antes de prosseguir:" && \
		echo "  1. Defina GEMINI_API_KEY no ambiente ou no arquivo" && \
		echo "  2. Configure paths de dados externos (external_data_dir, external_shapefiles_dir)" && \
		echo "" \
	)
	@echo "==> Setup concluído!"

# --- Importação de registros ---
import: $(BIB_RECORDS)

$(BIB_RECORDS): $(SCOPUS_RIS) $(SCIELO_RIS) $(CAPES_RIS) $(ECONPAPERS_RIS) $(ANPEC_XLSX)
	@echo "==> Importando registros das 5 bases..."
	cd $(SCRIPTS_DIR) && $(PYTHON) main.py search --verbose \
		--import-scopus "../$(SCOPUS_RIS)" \
		--import-scielo "../$(SCIELO_RIS)" \
		--import-capes "../$(CAPES_RIS)" \
		--import-econpapers "../$(ECONPAPERS_RIS)" \
		--import-anpec "../$(ANPEC_XLSX)"
	@echo "==> Importação concluída: $(BIB_RECORDS)"

# --- Triagem pré-LLM ---
screen: $(BIB_SCREENED)

$(BIB_SCREENED): $(BIB_RECORDS)
	@echo "==> Executando triagem pré-LLM (PRISMA)..."
	cd $(SCRIPTS_DIR) && $(PYTHON) main.py screen --verbose --input-json "../$(BIB_RECORDS)"
	@echo "==> Triagem concluída: $(BIB_SCREENED)"

# --- Análise LLM ---
analyze:
	@echo "==> Executando análise LLM (3 estágios)..."
	@echo "[ATENÇÃO] Requer:"
	@echo "  1. GEMINI_API_KEY configurada"
	@echo "  2. PDFs em data/2-papers/2-2-papers-pdfs/ (119 arquivos)"
	@echo ""
	cd $(SCRIPTS_DIR) && $(PYTHON) run_llm_all_papers.py
	@echo "==> Análise LLM concluída"

# --- Mesclagem registros + LLM ---
merge: $(PAPERS_JSON)

$(PAPERS_JSON):
	@echo "==> Mesclando registros + classificação LLM..."
	cd $(SCRIPTS_DIR) && $(PYTHON) merge_papers_to_json.py
	@echo "==> JSON enriquecido gerado: $(PAPERS_JSON)"

# --- Citações ---
citations: $(CITATION_INDEX)

$(CITATION_INDEX):
	@echo "==> Executando matching de citações entre estudos..."
	cd $(SCRIPTS_DIR) && $(PYTHON) match_refs_to_studies.py
	@echo ""
	@echo "==> Calculando índice de citação..."
	cd $(SCRIPTS_DIR) && $(PYTHON) citation_index.py
	@echo "==> Índice de citação gerado: $(CITATION_INDEX)"

# --- Referências aprovadas ---
references: $(APPROVED_RIS) $(REFERENCES_BIB) $(TABELA_IC)

$(APPROVED_RIS):
	@echo "==> Gerando RIS de estudos aprovados..."
	cd $(SCRIPTS_DIR) && $(PYTHON) generate_approved_ris.py
	@echo "==> RIS aprovado: $(APPROVED_RIS)"

$(REFERENCES_BIB): $(APPROVED_RIS)
	@echo "==> Convertendo RIS → BibTeX..."
	cd $(SCRIPTS_DIR) && $(PYTHON) generate_bibtex.py
	@echo "==> BibTeX gerado: $(REFERENCES_BIB)"

$(TABELA_IC): $(CITATION_INDEX)
	@echo "==> Gerando tabela de índice de citação..."
	cd $(SCRIPTS_DIR) && $(PYTHON) generate_ic_table.py
	@echo "==> Tabela IC gerada: $(TABELA_IC)"

# --- Tabelas LaTeX ---
tables: $(TABELA_IC)
	@echo "==> Gerando todas as tabelas LaTeX..."
	cd $(SCRIPTS_DIR) && $(PYTHON) generate_latex_tables.py
	@echo "==> Tabelas geradas em latex/tabelas/"

# --- Figuras ---
figures:
	@echo "==> Gerando figuras (mapas PIB, tipologia, gráfico ICF)..."
	cd $(SCRIPTS_DIR) && $(PYTHON) generate_figures.py --verbose
	@echo "==> Figuras geradas em $(FIGURES_DIR)/"

# --- Compilação LaTeX ---
latex: $(ARTICLE_PDF)

$(ARTICLE_PDF):
	@echo "==> Compilando artigo LaTeX..."
	cd $(LATEX_DIR) && pdflatex -interaction=nonstopmode main.tex
	cd $(LATEX_DIR) && bibtex main
	cd $(LATEX_DIR) && pdflatex -interaction=nonstopmode main.tex
	cd $(LATEX_DIR) && pdflatex -interaction=nonstopmode main.tex
	@echo "==> Artigo compilado: $(ARTICLE_PDF)"

# --- Limpeza ---
clean:
	@echo "==> Limpando outputs gerados..."
	# Dados processados
	-del /Q "$(DATA_DIR)\1-records\processed\*.json" 2>nul
	-del /Q "$(DATA_DIR)\1-records\processed\*.csv" 2>nul
	-del /Q "$(DATA_DIR)\1-records\processed\*.xlsx" 2>nul
	# Papers
	-del /Q "$(DATA_DIR)\2-papers\*.json" 2>nul
	-del /Q "$(DATA_DIR)\2-papers\*.xlsx" 2>nul
	-del /Q "$(DATA_DIR)\2-papers\_llm_checkpoint.json" 2>nul
	# Referências
	-del /Q "$(DATA_DIR)\3-ref-bib\*.json" 2>nul
	-del /Q "$(DATA_DIR)\3-ref-bib\*.txt" 2>nul
	-del /Q "$(DATA_DIR)\3-ref-bib\*.ris" 2>nul
	-rmdir /S /Q "$(DATA_DIR)\3-ref-bib\refs_por_estudo" 2>nul
	# LaTeX outputs
	-del /Q "$(LATEX_DIR)\*.aux" 2>nul
	-del /Q "$(LATEX_DIR)\*.bbl" 2>nul
	-del /Q "$(LATEX_DIR)\*.blg" 2>nul
	-del /Q "$(LATEX_DIR)\*.log" 2>nul
	-del /Q "$(LATEX_DIR)\*.out" 2>nul
	-del /Q "$(LATEX_DIR)\*.toc" 2>nul
	-del /Q "$(LATEX_DIR)\*.pdf" 2>nul
	-del /Q "$(LATEX_DIR)\references.bib" 2>nul
	-del /Q "$(LATEX_DIR)\tabela_ic.tex" 2>nul
	# Figuras (opcional - comente se quiser manter)
	# -del /Q "$(FIGURES_DIR)\*.png" 2>nul
	@echo "==> Limpeza concluída!"

# --- Validação ---
validate:
	@echo "==> Validando dependências..."
	@echo ""
	@echo "Python:"
	@$(PYTHON) --version
	@echo ""
	@echo "R:"
	@Rscript --version
	@echo ""
	@echo "PDFs:"
	@dir /B "$(DATA_DIR)\2-papers\2-2-papers-pdfs\*.pdf" 2>nul | find /C ".pdf"
	@echo ""
	@echo "Figuras (dependências externas):"
	cd $(SCRIPTS_DIR) && $(PYTHON) generate_figures.py --validate

# --- Help ---
help:
	@echo "pndr_survey — Pipeline de Reprodutibilidade"
	@echo ""
	@echo "Targets disponíveis:"
	@echo "  make setup       Instalar dependências"
	@echo "  make import      Importar registros das 5 bases"
	@echo "  make screen      Triagem pré-LLM"
	@echo "  make analyze     Análise LLM (requer GEMINI_API_KEY e PDFs)"
	@echo "  make merge       Mesclar registros + LLM"
	@echo "  make citations   Matching de citações + índice"
	@echo "  make references  Gerar RIS + BibTeX aprovados"
	@echo "  make tables      Gerar tabelas LaTeX"
	@echo "  make figures     Gerar figuras (mapas, gráficos)"
	@echo "  make latex       Compilar PDF do artigo"
	@echo "  make all         Pipeline completo (padrão)"
	@echo "  make clean       Limpar outputs gerados"
	@echo "  make validate    Validar dependências (Python, R, PDFs)"
	@echo "  make help        Mostrar esta mensagem"
	@echo ""
	@echo "Documentação completa: REPRODUCING.md"
