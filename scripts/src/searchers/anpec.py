"""Buscador semi-automático para ANPEC (Encontro Nacional de Economia).

A ANPEC não possui API ou repositório indexado. Os artigos são encontrados
via Google Search com filtro por domínio (site:anpec.org.br) e exportados
em planilha Excel usando ferramentas de scraping (ex: Google Search Results
Scraper). Este módulo importa essas planilhas e converte em BibRecords.

Fluxo:
    1. build_query() / save_query_instructions() — gera query Google
    2. Usuário faz a busca e exporta resultados para Excel
    3. import_from_file(planilha.xlsx) — lê e converte em BibRecords
    4. Download de PDFs pelo downloader padrão do pipeline
"""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import List, Optional

from src.models import BibRecord
from src.searchers.base import BaseSearcher, _extract_year, _safe_str

logger = logging.getLogger("pndr_survey")

ANPEC_DOMAIN = "anpec.org.br"


class ANPECSearcher(BaseSearcher):
    """Busca semi-automática para artigos da ANPEC via Google Search."""

    name = "anpec"

    def build_query(self) -> str:
        """Retorna query para Google Search com filtro site:anpec.org.br."""
        return f"site:{ANPEC_DOMAIN} {self.keywords}"

    def search(self) -> int:
        """ANPEC não suporta busca automática (não possui API).

        Returns:
            0 (sempre — resultados vêm via importação de Excel).
        """
        logger.info(
            "ANPEC requer busca manual via Google Search. "
            "Use save_query_instructions() para gerar o arquivo de instruções."
        )
        return 0

    def fetch_records(self) -> List[BibRecord]:
        """Retorna registros importados."""
        return self.records

    def import_from_file(self, filepath: str | Path) -> List[BibRecord]:
        """Importa resultados de Excel (.xlsx), RIS ou CSV.

        Para Excel, espera colunas exportadas por Google Search scrapers:
        - Link: URL do artigo
        - Title: título exibido no Google
        - Snippet: trecho/resumo exibido no Google
        - Source (opcional): fonte

        Args:
            filepath: Caminho para arquivo .xlsx, .ris ou .csv.

        Returns:
            Lista de BibRecords importados.
        """
        filepath = Path(filepath)
        suffix = filepath.suffix.lower()

        if suffix in (".xlsx", ".xls"):
            return self._import_excel(filepath)

        # Delegar RIS/CSV para a classe base
        return super().import_from_file(filepath)

    def _import_excel(self, filepath: Path) -> List[BibRecord]:
        """Importa registros de planilha Excel com URLs do Google Search."""
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
        snippet_col = col_map.get("snippet", col_map.get("description", col_map.get("abstract", col_map.get("trecho"))))

        if link_col is None:
            raise ValueError(
                f"Coluna 'Link' ou 'URL' não encontrada em {filepath.name}. "
                f"Colunas disponíveis: {list(df.columns)}"
            )

        # Limpar URLs
        df = df.dropna(subset=[link_col]).copy()
        df[link_col] = df[link_col].str.strip()

        # Filtrar apenas URLs válidas
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

            # Classificar tipo de arquivo pela URL
            file_type = _detect_file_type(url)

            bib = BibRecord(
                source_db=self.name,
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
        self.records.extend(records)
        return records

    def _build_instructions(self, query: str) -> str:
        """Gera instruções para busca de artigos ANPEC via Google."""
        return (
            "=" * 70 + "\n"
            "BUSCA ANPEC (via Google Search)\n"
            "=" * 70 + "\n\n"
            f"Query:\n{query}\n\n"
            "--- Instruções ---\n\n"
            "A ANPEC não possui repositório indexado. A busca é feita via\n"
            "Google Search com filtro de domínio.\n\n"
            "Opção A — Google Search Results Scraper (recomendado):\n"
            "  1. Use uma ferramenta de scraping do Google (ex: Apify, SerpAPI)\n"
            "  2. Cole a query acima como termo de busca\n"
            f"  3. Adicione filtro: filetype:pdf site:{ANPEC_DOMAIN}\n"
            "  4. Exporte resultados como Excel (.xlsx)\n"
            "     O arquivo deve ter colunas: Link, Title, Snippet\n"
            "  5. Repita com filetype:docx se necessário\n"
            "  6. Importe com:\n"
            "     python main.py search --import-anpec <arquivo.xlsx>\n\n"
            "Opção B — Busca manual:\n"
            "  1. Acesse https://www.google.com/\n"
            f"  2. Busque: {query}\n"
            "  3. Adicione filtro filetype:pdf para PDFs\n"
            "  4. Copie as URLs dos resultados relevantes\n"
            "  5. Crie um CSV com coluna 'Link' e 'Title'\n"
            "  6. Importe com:\n"
            "     python main.py search --import-anpec <arquivo.csv>\n\n"
            "--- Dicas ---\n\n"
            f"- A ANPEC hospeda artigos em {ANPEC_DOMAIN}/encontro/\n"
            "- Artigos de encontros recentes (2015+) estão geralmente em PDF\n"
            "- Artigos mais antigos podem estar em DOC/DOCX\n"
            "- Use filetype:pdf e filetype:docx em buscas separadas\n"
        )


# --- Utilitários ---


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
    # Remover sufixos tipo " - ANPEC", " | Anpec", " [PDF]", " - PDF"
    title = re.sub(r"\s*[-|]\s*(ANPEC|PDF|Anpec|anpec).*$", "", title)
    title = re.sub(r"\s*\[(PDF|DOC|DOCX)\]\s*$", "", title, flags=re.IGNORECASE)
    return title.strip() or None
