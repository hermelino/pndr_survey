"""Importação de registros bibliográficos de arquivos RIS, CSV e Excel.

A extração de artigos é feita manualmente em cada base (EconPapers,
CAPES, Scopus, ANPEC). Este módulo importa os arquivos exportados
e os normaliza em BibRecords.
"""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import List, Optional

from src.models import BibRecord

logger = logging.getLogger("pndr_survey")


# =============================================================================
# Dispatcher
# =============================================================================


def import_from_file(filepath: str | Path, source_db: str) -> List[BibRecord]:
    """Importa registros de arquivo RIS, CSV ou Excel.

    Args:
        filepath: Caminho para o arquivo exportado.
        source_db: Nome da base de origem (econpapers, capes, scopus, anpec).

    Returns:
        Lista de BibRecords importados.
    """
    filepath = Path(filepath)
    suffix = filepath.suffix.lower()

    if suffix == ".ris":
        return import_ris(filepath, source_db)
    if suffix == ".csv":
        return import_csv(filepath, source_db)
    if suffix in (".xlsx", ".xls"):
        return import_excel(filepath, source_db)

    raise ValueError(f"Formato não suportado: {suffix}. Use .ris, .csv ou .xlsx")


# =============================================================================
# Importadores
# =============================================================================


def import_ris(filepath: Path, source_db: str) -> List[BibRecord]:
    """Importa registros de arquivo RIS."""
    import rispy

    for encoding in ("utf-8-sig", "utf-8", "latin-1", "cp1252"):
        try:
            with open(filepath, encoding=encoding) as f:
                entries = rispy.load(f)
            break
        except (UnicodeDecodeError, Exception):
            continue
    else:
        raise ValueError(f"Não foi possível ler {filepath} com nenhum encoding")

    records: List[BibRecord] = []
    for entry in entries:
        urls = entry.get("urls", [])
        first_url = urls[0] if urls else None
        ris_type = entry.get("type_of_reference", "")
        pub_type = _ris_type_to_publication_type(ris_type)

        bib = BibRecord(
            source_db=source_db,
            source_id=entry.get("accession_number", entry.get("doi", "")),
            doi=entry.get("doi"),
            title=entry.get("title", entry.get("primary_title", "")),
            authors=entry.get("authors", entry.get("first_authors", [])),
            year=_extract_year(entry.get("year", entry.get("publication_year"))),
            journal=entry.get("journal_name", entry.get("secondary_title")),
            volume=entry.get("volume"),
            issue=entry.get("number"),
            pages=_build_pages(entry.get("start_page"), entry.get("end_page")),
            abstract=entry.get("abstract", entry.get("notes_abstract")),
            keywords=entry.get("keywords", []),
            url=first_url,
            language=entry.get("language"),
            publication_type=pub_type,
        )
        records.append(bib)

    logger.info("Importados %d registros de %s (RIS)", len(records), filepath.name)
    return records


def import_csv(filepath: Path, source_db: str) -> List[BibRecord]:
    """Importa registros de arquivo CSV."""
    import pandas as pd

    for encoding in ("utf-8-sig", "utf-8", "latin-1", "cp1252"):
        try:
            for sep in (",", ";"):
                try:
                    df = pd.read_csv(filepath, encoding=encoding, sep=sep)
                    if len(df.columns) > 1:
                        break
                except Exception:
                    continue
            else:
                continue
            break
        except UnicodeDecodeError:
            continue
    else:
        raise ValueError(f"Não foi possível ler {filepath} com nenhum encoding")

    records: List[BibRecord] = []
    for _, row in df.iterrows():
        bib = BibRecord(
            source_db=source_db,
            source_id=str(row.get("DOI", row.get("doi", row.get("ID", "")))),
            doi=_safe_str(row.get("DOI", row.get("doi"))),
            title=_safe_str(row.get("Title", row.get("title", ""))) or "",
            authors=_parse_authors_str(
                _safe_str(row.get("Authors", row.get("authors", row.get("Author", ""))))
            ),
            year=_extract_year(row.get("Year", row.get("year", row.get("PY")))),
            journal=_safe_str(row.get("Journal", row.get("journal", row.get("Source title")))),
            abstract=_safe_str(row.get("Abstract", row.get("abstract"))),
            url=_safe_str(row.get("URL", row.get("url"))),
        )
        records.append(bib)

    logger.info("Importados %d registros de %s (CSV)", len(records), filepath.name)
    return records


def import_excel(filepath: Path, source_db: str = "anpec") -> List[BibRecord]:
    """Importa registros de planilha Excel (formato Google Search scraper).

    Espera colunas: Link, Title, Snippet (case-insensitive).
    """
    import pandas as pd

    if not filepath.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {filepath}")

    df = pd.read_excel(filepath)
    logger.info(
        "Lendo %d linhas de %s (colunas: %s)",
        len(df), filepath.name, list(df.columns),
    )

    # Normalizar nomes de colunas (case-insensitive)
    col_map = {c.lower().strip(): c for c in df.columns}
    link_col = col_map.get("link", col_map.get("url", col_map.get("links")))
    title_col = col_map.get("title", col_map.get("titulo", col_map.get("título")))
    snippet_col = col_map.get(
        "snippet", col_map.get("description", col_map.get("abstract", col_map.get("trecho")))
    )

    if link_col is None:
        raise ValueError(
            f"Coluna 'Link' ou 'URL' não encontrada em {filepath.name}. "
            f"Colunas disponíveis: {list(df.columns)}"
        )

    # Limpar e filtrar URLs
    df = df.dropna(subset=[link_col]).copy()
    df[link_col] = df[link_col].str.strip()
    valid_mask = df[link_col].str.match(r"^https?://", na=False)
    n_invalid = (~valid_mask).sum()
    if n_invalid:
        logger.warning("Removidas %d URLs inválidas", n_invalid)
    df = df[valid_mask]

    # Remover duplicatas por URL
    n_before = len(df)
    df = df.drop_duplicates(subset=[link_col])
    n_dupes = n_before - len(df)
    if n_dupes:
        logger.info("Removidas %d URLs duplicadas", n_dupes)

    records: List[BibRecord] = []
    for _, row in df.iterrows():
        url = row[link_col]
        title = _safe_str(row.get(title_col)) if title_col else None
        snippet = _safe_str(row.get(snippet_col)) if snippet_col else None
        file_type = _detect_file_type(url)

        bib = BibRecord(
            source_db=source_db,
            source_id=url,
            title=_clean_google_title(title) or "",
            abstract=snippet,
            url=url,
            pdf_url=url if file_type == "pdf" else None,
            year=_extract_year_from_url(url),
            publication_type="apresentação em congresso",
        )
        records.append(bib)

    logger.info(
        "Importados %d registros de %s (%d PDFs, %d DOCX, %d outros)",
        len(records),
        filepath.name,
        sum(1 for r in records if r.pdf_url),
        sum(1 for r in records if _detect_file_type(r.url or "") == "docx"),
        sum(1 for r in records if _detect_file_type(r.url or "") == "other"),
    )
    return records


# =============================================================================
# Utilitários
# =============================================================================


def _ris_type_to_publication_type(ris_type: str) -> Optional[str]:
    """Converte tipo RIS (TY) para publication_type legível."""
    mapping = {
        "JOUR": "artigo publicado",
        "RPRT": "texto para discussão",
        "THES": "tese",
        "CHAP": "capítulo de livro",
        "CPAPER": "apresentação em congresso",
        "CONF": "apresentação em congresso",
        "BOOK": "livro",
        "GEN": None,
    }
    return mapping.get(ris_type)


def _extract_year(value: Optional[str | int | float]) -> Optional[int]:
    """Extrai ano (int) de diversos formatos."""
    if value is None or (isinstance(value, float) and str(value) == "nan"):
        return None
    match = re.search(r"(19|20)\d{2}", str(value))
    return int(match.group()) if match else None


def _build_pages(start: Optional[str], end: Optional[str]) -> Optional[str]:
    """Concatena páginas no formato 'start-end'."""
    if start and end:
        return f"{start}-{end}"
    return start or end


def _safe_str(value) -> Optional[str]:
    """Converte para string, tratando NaN do pandas."""
    if value is None:
        return None
    s = str(value)
    if s in ("nan", "None", ""):
        return None
    return s.strip()


def _parse_authors_str(value: Optional[str]) -> List[str]:
    """Separa string de autores em lista."""
    if not value:
        return []
    parts = re.split(r"\s*;\s*|\s+and\s+|\s*&\s*", value)
    return [p.strip() for p in parts if p.strip()]


def _detect_file_type(url: str) -> str:
    """Detecta tipo de arquivo pela extensão na URL."""
    url_lower = url.lower()
    if url_lower.endswith(".pdf") or ".pdf?" in url_lower:
        return "pdf"
    if url_lower.endswith((".doc", ".docx")) or ".docx?" in url_lower:
        return "docx"
    return "other"


def _extract_year_from_url(url: str) -> Optional[int]:
    """Tenta extrair ano de URLs ANPEC (ex: /encontro/2018/ ou /anais2020/)."""
    match = re.search(r"(?:encontro|anais|papers)[/_]?(20[012]\d|199\d)", url)
    if match:
        return int(match.group(1))
    return _extract_year(url)


def _clean_google_title(title: Optional[str]) -> Optional[str]:
    """Remove sufixos comuns de títulos do Google (ex: '- ANPEC', ' | PDF')."""
    if not title:
        return None
    title = re.sub(r"\s*[-|]\s*(ANPEC|PDF|Anpec|anpec).*$", "", title)
    title = re.sub(r"\s*\[(PDF|DOC|DOCX)\]\s*$", "", title, flags=re.IGNORECASE)
    return title.strip() or None
