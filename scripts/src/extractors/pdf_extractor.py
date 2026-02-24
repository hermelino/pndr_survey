"""Extração de texto de PDFs via pdfplumber.

Responsabilidades:
  - Extrair texto de cada página do PDF
  - Normalizar texto (hifenização, espaços múltiplos)
  - Truncar em max_chars caracteres
  - Calcular hash SHA-256 do arquivo
  - Retornar PaperRecord parcialmente preenchido
"""

from __future__ import annotations

import hashlib
import logging
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pdfplumber

from src.models import BibRecord, PaperRecord

logger = logging.getLogger("pndr_survey")

# Tamanho mínimo de texto extraído para considerar o PDF legível
MIN_TEXT_LENGTH = 100


class PdfExtractor:
    """Extrai texto de PDFs e cria PaperRecords."""

    def __init__(self, *, max_chars: int = 100_000):
        """
        Args:
            max_chars: Limite de caracteres do texto extraído.
                       Corresponde ao max_tokens_input do config LLM.
        """
        self.max_chars = max_chars

    def extract(self, pdf_path: Path, bib: BibRecord) -> PaperRecord:
        """Extrai texto de um PDF e retorna PaperRecord vinculado ao BibRecord.

        Args:
            pdf_path: Caminho para o arquivo PDF.
            bib: BibRecord com metadados bibliográficos.

        Returns:
            PaperRecord com text_length, text_preview, file_hash preenchidos.
            Em caso de erro, processing_errors conterá a descrição.
        """
        record = PaperRecord(bib=bib, pdf_path=str(pdf_path))
        errors: List[str] = []

        # Hash SHA-256
        file_hash = _compute_hash(pdf_path)
        if file_hash:
            record.file_hash = file_hash
        else:
            errors.append(f"Falha ao calcular hash: {pdf_path.name}")

        # Extração de texto
        text = _extract_text(pdf_path)
        if text is None:
            errors.append(f"Falha ao extrair texto: {pdf_path.name}")
            record.processing_errors = errors
            return record

        text = _normalize_text(text)

        if len(text) < MIN_TEXT_LENGTH:
            errors.append(
                f"Texto muito curto ({len(text)} chars): {pdf_path.name}"
            )

        # Truncar se necessário
        if len(text) > self.max_chars:
            text = text[:self.max_chars]
            logger.debug(
                "Texto truncado em %d chars: %s", self.max_chars, pdf_path.name
            )

        record.text_length = len(text)
        record.text_preview = text[:500]
        record.processing_errors = errors

        # Guardar texto completo como atributo auxiliar (não persistido)
        record._extracted_text = text

        return record

    def extract_batch(
        self,
        pdf_dir: Path,
        records: List[BibRecord],
    ) -> Tuple[List[PaperRecord], Dict[str, str]]:
        """Extrai texto de PDFs em lote, vinculando a BibRecords.

        Tenta associar cada PDF a um BibRecord pelo nome do arquivo.
        PDFs sem BibRecord correspondente são processados com BibRecord mínimo.

        Args:
            pdf_dir: Diretório contendo os PDFs.
            records: Lista de BibRecords (usados para vincular por nome).

        Returns:
            Tupla (paper_records, erros) onde erros é {filename: mensagem}.
        """
        pdf_dir = Path(pdf_dir)
        pdf_files = sorted(pdf_dir.glob("*.pdf"))

        if not pdf_files:
            logger.warning("Nenhum PDF encontrado em %s", pdf_dir)
            return [], {}

        # Índice de BibRecords por possíveis nomes de arquivo
        bib_index = _build_bib_index(records)

        results: List[PaperRecord] = []
        errors: Dict[str, str] = {}

        logger.info(
            "Extraindo texto de %d PDFs em %s", len(pdf_files), pdf_dir
        )

        for i, pdf_path in enumerate(pdf_files):
            bib = bib_index.get(pdf_path.stem) or bib_index.get(pdf_path.name)

            if bib is None:
                # Criar BibRecord mínimo para PDFs sem correspondência
                bib = BibRecord(
                    source_db="manual",
                    source_id=pdf_path.stem,
                    title=pdf_path.stem,
                )
                logger.debug(
                    "PDF sem BibRecord correspondente: %s", pdf_path.name
                )

            paper = self.extract(pdf_path, bib)

            if paper.processing_errors:
                errors[pdf_path.name] = "; ".join(paper.processing_errors)

            results.append(paper)

            if (i + 1) % 10 == 0:
                logger.info(
                    "Progresso: %d/%d PDFs extraídos", i + 1, len(pdf_files)
                )

        ok = sum(1 for r in results if r.text_length >= MIN_TEXT_LENGTH)
        fail = len(results) - ok
        logger.info(
            "Extração concluída: %d ok, %d com problemas de %d PDFs",
            ok, fail, len(pdf_files),
        )

        return results, errors


# --- Funções auxiliares ---


def _compute_hash(filepath: Path) -> Optional[str]:
    """Calcula SHA-256 do arquivo em chunks de 8KB."""
    try:
        sha256 = hashlib.sha256()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256.update(chunk)
        return sha256.hexdigest()
    except OSError as e:
        logger.warning("Erro ao ler %s para hash: %s", filepath, e)
        return None


def _extract_text(pdf_path: Path) -> Optional[str]:
    """Extrai texto de todas as páginas do PDF via pdfplumber."""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            pages: List[str] = []
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    pages.append(page_text)

            if not pages:
                logger.warning("Nenhum texto extraído de %s", pdf_path.name)
                return ""

            return "\n\n".join(pages)

    except Exception as e:
        logger.warning("Erro ao extrair texto de %s: %s", pdf_path.name, e)
        return None


def _normalize_text(text: str) -> str:
    """Normaliza texto extraído de PDF.

    - Remove hifenização de quebra de linha (pala-\\nvra → palavra)
    - Colapsa espaços múltiplos
    - Remove linhas em branco consecutivas
    """
    # Hifenização: palavra- \n continuação → palavra continuação
    text = re.sub(r"(\w)-\s*\n\s*(\w)", r"\1\2", text)

    # Espaços múltiplos → espaço único
    text = re.sub(r"[ \t]+", " ", text)

    # Linhas em branco consecutivas → uma só
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def _build_bib_index(records: List[BibRecord]) -> Dict[str, BibRecord]:
    """Constrói índice de BibRecords por possíveis nomes de arquivo PDF.

    Gera variações do nome que o downloader pode ter usado:
    - {source_db}_{surname}_{year}_{hash}.pdf
    - citation_key
    """
    index: Dict[str, BibRecord] = {}

    for rec in records:
        # Por citation_key (sobrenome_ano)
        key = rec.citation_key
        if key and key != "unknown_nd":
            index[key] = rec

        # Por source_id (pode ser usado como stem)
        if rec.source_id:
            index[rec.source_id] = rec

        # Por DOI hash (usado pelo downloader)
        if rec.doi:
            doi_hash = hashlib.md5(rec.doi.encode()).hexdigest()[:6]
            surname = ""
            if rec.first_author:
                surname = re.sub(r"[^\w]", "", rec.first_author.split(",")[0].split()[-1])[:30]
            stem = f"{rec.source_db}_{surname}_{rec.year or 'nd'}_{doi_hash}"
            index[stem] = rec

        # Por source_id hash
        if rec.source_id and not rec.doi:
            sid_hash = hashlib.md5(rec.source_id.encode()).hexdigest()[:6]
            surname = ""
            if rec.first_author:
                surname = re.sub(r"[^\w]", "", rec.first_author.split(",")[0].split()[-1])[:30]
            stem = f"{rec.source_db}_{surname}_{rec.year or 'nd'}_{sid_hash}"
            index[stem] = rec

    return index
