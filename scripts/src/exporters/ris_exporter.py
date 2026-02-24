"""Exportação de registros bibliográficos para formato RIS (Zotero/Mendeley)."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import List

from src.models import BibRecord, PaperRecord

logger = logging.getLogger("pndr_survey")

# Mapeamento publication_type → RIS TY
_RIS_TYPE_MAP = {
    "article": "JOUR",
    "artigo publicado": "JOUR",
    "working_paper": "RPRT",
    "texto para discussão": "RPRT",
    "book_chapter": "CHAP",
    "tese": "THES",
    "dissertação": "THES",
    "monografia": "THES",
    "apresentação em congresso": "CPAPER",
}


def export_ris(
    papers: List[PaperRecord],
    output_path: str | Path,
) -> Path:
    """Exporta BibRecords para arquivo RIS.

    Formato padrão para importação em Zotero, Mendeley, EndNote.

    Args:
        papers: Lista de PaperRecords (usa apenas o .bib).
        output_path: Caminho do arquivo .ris de saída.

    Returns:
        Path do arquivo criado.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    entries = []
    for paper in papers:
        entry = _bib_to_ris(paper.bib)
        entries.append(entry)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(entries))

    logger.info("RIS exportado: %s (%d registros)", output_path, len(entries))
    return output_path


def _bib_to_ris(bib: BibRecord) -> str:
    """Converte um BibRecord em entrada RIS."""
    lines = []

    # Tipo
    ris_type = _RIS_TYPE_MAP.get(
        (bib.publication_type or "").lower(), "GEN"
    )
    lines.append(f"TY  - {ris_type}")

    # Título
    if bib.title:
        lines.append(f"TI  - {bib.title}")

    # Autores
    for author in bib.authors:
        lines.append(f"AU  - {author}")

    # Ano
    if bib.year:
        lines.append(f"PY  - {bib.year}")

    # Periódico
    if bib.journal:
        lines.append(f"JO  - {bib.journal}")

    # Volume, issue, pages
    if bib.volume:
        lines.append(f"VL  - {bib.volume}")
    if bib.issue:
        lines.append(f"IS  - {bib.issue}")
    if bib.pages:
        lines.append(f"SP  - {bib.pages}")

    # DOI
    if bib.doi:
        lines.append(f"DO  - {bib.doi}")

    # Abstract
    if bib.abstract:
        lines.append(f"AB  - {bib.abstract}")

    # Keywords
    for kw in bib.keywords:
        lines.append(f"KW  - {kw}")

    # URL
    if bib.url:
        lines.append(f"UR  - {bib.url}")

    # Idioma
    if bib.language:
        lines.append(f"LA  - {bib.language}")

    # Base de origem (nota)
    lines.append(f"N1  - Source: {bib.source_db} ({bib.source_id})")

    # Fim do registro
    lines.append("ER  - ")
    lines.append("")

    return "\n".join(lines)
