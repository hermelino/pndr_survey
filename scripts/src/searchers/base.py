"""Interface base para buscadores de artigos em bases acadêmicas.

Cada base (EconPapers, Google Scholar, CAPES, Scopus) implementa
esta interface, permitindo orquestração uniforme pelo main.py.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional

from src.models import BibRecord


logger = logging.getLogger("pndr_survey")


class BaseSearcher(ABC):
    """Interface base para todos os buscadores."""

    name: str = "base"
    records: List[BibRecord]
    total_results: int

    def __init__(self, keywords: str, *, max_results: int = 1000):
        self.keywords = keywords
        self.max_results = max_results
        self.records = []
        self.total_results = 0

    @abstractmethod
    def build_query(self) -> str:
        """Constrói a query de busca na sintaxe da base.

        Returns:
            String com a query formatada para a base específica.
        """

    @abstractmethod
    def search(self) -> int:
        """Executa a busca e retorna o número de resultados encontrados.

        Para bases automáticas: faz a requisição HTTP.
        Para bases manuais: retorna 0 (resultados vêm via import_from_file).

        Returns:
            Número de resultados encontrados.
        """

    @abstractmethod
    def fetch_records(self) -> List[BibRecord]:
        """Recupera registros e normaliza para BibRecord.

        Returns:
            Lista de BibRecords normalizados.
        """

    def import_from_file(self, filepath: str | Path) -> List[BibRecord]:
        """Importa resultados exportados manualmente (RIS ou CSV).

        Implementação padrão tenta detectar o formato pelo sufixo.
        Subclasses podem sobrescrever para parsing específico.

        Args:
            filepath: Caminho para arquivo RIS ou CSV exportado.

        Returns:
            Lista de BibRecords importados.
        """
        filepath = Path(filepath)
        suffix = filepath.suffix.lower()
        if suffix == ".ris":
            return self._import_ris(filepath)
        if suffix == ".csv":
            return self._import_csv(filepath)
        raise ValueError(f"Formato não suportado: {suffix}. Use .ris ou .csv")

    def save_query_instructions(self, output_dir: Path) -> Path:
        """Salva query formatada + instruções de busca manual.

        Útil para bases sem API (Google Scholar, CAPES).

        Args:
            output_dir: Diretório onde salvar o arquivo de instruções.

        Returns:
            Caminho do arquivo de instruções criado.
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        filepath = output_dir / f"query_{self.name}.txt"

        query = self.build_query()
        instructions = self._build_instructions(query)

        filepath.write_text(instructions, encoding="utf-8")
        logger.info(f"Instruções de busca salvas em: {filepath}")
        return filepath

    def _build_instructions(self, query: str) -> str:
        """Gera texto com instruções de busca manual. Subclasses sobrescrevem."""
        return (
            f"=== Busca em {self.name} ===\n\n"
            f"Query:\n{query}\n\n"
            f"Instruções:\n"
            f"1. Acesse a base e cole a query acima\n"
            f"2. Exporte os resultados em formato RIS ou CSV\n"
            f"3. Importe com: python main.py search --import-{self.name} <arquivo>\n"
        )

    def _import_ris(self, filepath: Path) -> List[BibRecord]:
        """Importa registros de arquivo RIS."""
        import rispy

        records = []
        # Tentar múltiplos encodings
        for encoding in ("utf-8-sig", "utf-8", "latin-1", "cp1252"):
            try:
                with open(filepath, encoding=encoding) as f:
                    entries = rispy.load(f)
                break
            except (UnicodeDecodeError, Exception):
                continue
        else:
            raise ValueError(f"Não foi possível ler {filepath} com nenhum encoding")

        for entry in entries:
            # rispy usa 'urls' (lista), não 'url'
            urls = entry.get("urls", [])
            first_url = urls[0] if urls else None

            # Tipo do registro RIS (TY tag)
            ris_type = entry.get("type_of_reference", "")
            pub_type = _ris_type_to_publication_type(ris_type)

            bib = BibRecord(
                source_db=self.name,
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

        logger.info(f"Importados {len(records)} registros de {filepath.name} (RIS)")
        self.records.extend(records)
        return records

    def _import_csv(self, filepath: Path) -> List[BibRecord]:
        """Importa registros de arquivo CSV."""
        import pandas as pd

        for encoding in ("utf-8-sig", "utf-8", "latin-1", "cp1252"):
            try:
                # Tentar vírgula e ponto-e-vírgula
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

        records = []
        for _, row in df.iterrows():
            bib = BibRecord(
                source_db=self.name,
                source_id=str(row.get("DOI", row.get("doi", row.get("ID", "")))),
                doi=_safe_str(row.get("DOI", row.get("doi"))),
                title=_safe_str(row.get("Title", row.get("title", ""))),
                authors=_parse_authors_str(
                    _safe_str(row.get("Authors", row.get("authors", row.get("Author", ""))))
                ),
                year=_extract_year(row.get("Year", row.get("year", row.get("PY")))),
                journal=_safe_str(row.get("Journal", row.get("journal", row.get("Source title")))),
                abstract=_safe_str(row.get("Abstract", row.get("abstract"))),
                url=_safe_str(row.get("URL", row.get("url"))),
            )
            records.append(bib)

        logger.info(f"Importados {len(records)} registros de {filepath.name} (CSV)")
        self.records.extend(records)
        return records


# --- Utilitários compartilhados ---


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
    import re
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
    import re
    # Separar por ";", " and ", "&"
    parts = re.split(r"\s*;\s*|\s+and\s+|\s*&\s*", value)
    return [p.strip() for p in parts if p.strip()]
