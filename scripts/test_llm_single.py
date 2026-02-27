"""Teste rápido: extrai texto de 1 PDF e envia ao Gemini para triagem (Stage 1)."""

import json
import logging
import sys
from pathlib import Path

# Adicionar scripts/ ao sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.config import load_config
from src.models import BibRecord
from src.extractors.pdf_extractor import PdfExtractor
from src.analyzers.gemini_analyzer import GeminiAnalyzer
from src.analyzers.base import load_questionnaire

# --- Logging ---
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("pndr_survey")

# --- Config ---
config = load_config(Path(__file__).resolve().parent / "config.yaml")

# --- Escolher 1 PDF de teste ---
pdf_dir = Path(__file__).resolve().parent.parent / "data" / "2-papers" / "2-2-papers-pdfs"
pdfs = sorted(pdf_dir.glob("*.pdf"))

if not pdfs:
    print("Nenhum PDF encontrado em", pdf_dir)
    sys.exit(1)

# Pegar o primeiro PDF
test_pdf = pdfs[0]
print(f"\n{'='*70}")
print(f"PDF de teste: {test_pdf.name}")
print(f"{'='*70}\n")

# --- Etapa 1: Extrair texto ---
print("[1/3] Extraindo texto do PDF...")
extractor = PdfExtractor(max_chars=config.llm.max_tokens_input)
bib = BibRecord(source_db="manual", source_id=test_pdf.stem, title=test_pdf.stem)
paper = extractor.extract(test_pdf, bib)

print(f"  Texto extraído: {paper.text_length} caracteres")
print(f"  Hash: {paper.file_hash[:16]}...")
print(f"  Preview: {paper.text_preview[:200]}...")
if paper.processing_errors:
    print(f"  ERROS: {paper.processing_errors}")

# --- Etapa 2: Carregar questionário Stage 1 ---
print("\n[2/3] Carregando questionário Stage 1...")
q_path = Path(__file__).resolve().parent / "questionnaires" / "stage_1_screening.json"
questionnaire = load_questionnaire(q_path)
print(f"  Questionário: {questionnaire['metadata']['name']} v{questionnaire['metadata']['version']}")
print(f"  Perguntas: {len(questionnaire['questions'])}")

# --- Etapa 3: Enviar ao Gemini ---
print(f"\n[3/3] Enviando ao Gemini ({config.llm.model})...")
analyzer = GeminiAnalyzer(
    api_key=config.llm.api_key,
    model=config.llm.model,
    temperature=config.llm.temperature,
    max_tokens_input=config.llm.max_tokens_input,
    rate_limit_seconds=config.llm.rate_limit_seconds,
)

try:
    result = analyzer.analyze(paper, questionnaire)
    paper.stage_1 = result

    print(f"\n{'='*70}")
    print("RESULTADO DA ANÁLISE (Stage 1 - Triagem)")
    print(f"{'='*70}")
    for qid, answer in result.items():
        print(f"  {qid}: {answer}")

    print(f"\n--- JSON ---")
    print(json.dumps(result, indent=2, ensure_ascii=False))

except Exception as e:
    print(f"\nERRO na análise: {e}")
    import traceback
    traceback.print_exc()
