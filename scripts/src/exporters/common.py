"""Lógica compartilhada de exportação: flatten PaperRecord → linha tabular."""

from __future__ import annotations

from typing import Any, Dict, List

from src.models import BibRecord, PaperRecord


def flatten_record(paper: PaperRecord) -> Dict[str, Any]:
    """Converte PaperRecord + BibRecord em dicionário plano para exportação.

    Campos do BibRecord vêm primeiro, seguidos dos campos de análise.
    """
    bib = paper.bib
    row: Dict[str, Any] = {
        # Identidade
        "source_db": bib.source_db,
        "source_id": bib.source_id,
        "doi": bib.doi or "",
        # Bibliográficos
        "title": bib.title,
        "authors": "; ".join(bib.authors),
        "year": bib.year,
        "journal": bib.journal or "",
        "volume": bib.volume or "",
        "issue": bib.issue or "",
        "pages": bib.pages or "",
        # Conteúdo
        "abstract": bib.abstract or "",
        "keywords": "; ".join(bib.keywords),
        "url": bib.url or "",
        "pdf_url": bib.pdf_url or "",
        "language": bib.language or "",
        "publication_type": bib.publication_type or "",
        # Classificação
        "matched_instruments": "; ".join(bib.matched_instruments),
        # Deduplicação
        "is_duplicate": bib.is_duplicate,
        "duplicate_of": bib.duplicate_of or "",
        # PDF
        "pdf_path": paper.pdf_path or "",
        "file_hash": paper.file_hash or "",
        "text_length": paper.text_length,
        # Análise
        "is_empirical": paper.is_empirical,
        "pndr_instrument": paper.pndr_instrument or "",
        "econometric_method": paper.econometric_method or "",
        "time_period": paper.time_period or "",
        "geographic_scope": paper.geographic_scope or "",
        # Metadados de processamento
        "model_used": paper.model_used or "",
        "processing_errors": "; ".join(paper.processing_errors),
    }

    # Stage 1-3: expandir respostas como colunas prefixadas
    for stage_num in (1, 2, 3):
        stage_data = getattr(paper, f"stage_{stage_num}", None)
        if stage_data and isinstance(stage_data, dict):
            for key, value in stage_data.items():
                row[f"s{stage_num}_{key}"] = value
        # Se não tem dados do stage, não adicionar colunas vazias
        # (elas serão preenchidas como "" pelo DataFrame)

    return row


def flatten_all(papers: List[PaperRecord]) -> List[Dict[str, Any]]:
    """Converte lista de PaperRecords em lista de dicionários planos."""
    return [flatten_record(p) for p in papers]
