"""Buscador semi-automático para Google Scholar.

Gera query formatada e instruções para busca manual.
Importa resultados via RIS (Zotero Connector) ou CSV (Publish or Perish).
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import List

from src.models import BibRecord
from src.searchers.base import BaseSearcher

logger = logging.getLogger("pndr_survey")


class GoogleScholarSearcher(BaseSearcher):
    """Busca semi-automática no Google Scholar."""

    name = "google_scholar"

    def build_query(self) -> str:
        """Retorna query booleana para Google Scholar."""
        return self.keywords

    def search(self) -> int:
        """Google Scholar não suporta busca automática.

        Use save_query_instructions() para gerar instruções manuais e
        import_from_file() para importar os resultados exportados.

        Returns:
            0 (sempre — resultados vêm via importação).
        """
        logger.info(
            "Google Scholar requer busca manual. "
            "Use save_query_instructions() para gerar o arquivo de instruções."
        )
        return 0

    def fetch_records(self) -> List[BibRecord]:
        """Retorna registros importados."""
        return self.records

    def _build_instructions(self, query: str) -> str:
        """Gera instruções detalhadas para busca no Google Scholar."""
        scholar_url = "https://scholar.google.com.br/"

        return (
            "=" * 70 + "\n"
            "BUSCA NO GOOGLE SCHOLAR\n"
            "=" * 70 + "\n\n"
            f"Query:\n{query}\n\n"
            "--- Opção 1: Publish or Perish (recomendado) ---\n\n"
            "1. Abra o Publish or Perish (https://harzing.com/resources/publish-or-perish)\n"
            "2. Selecione 'Google Scholar'\n"
            "3. Cole a query no campo de busca\n"
            "4. Execute a busca\n"
            "5. Exporte como CSV ou RIS\n"
            "6. Importe com:\n"
            "   python main.py search --import-scholar <arquivo.csv>\n\n"
            "--- Opção 2: Zotero Connector ---\n\n"
            f"1. Acesse {scholar_url}\n"
            "2. Cole a query no campo de busca\n"
            "3. Use o Zotero Connector para salvar os resultados\n"
            "4. No Zotero, exporte a coleção como RIS\n"
            "5. Importe com:\n"
            "   python main.py search --import-scholar <arquivo.ris>\n\n"
            "--- Opção 3: Busca manual ---\n\n"
            f"1. Acesse {scholar_url}\n"
            "2. Cole a query no campo de busca\n"
            "3. Para cada página de resultados, copie os dados manualmente\n"
            "   (não recomendado para mais de 20 resultados)\n"
        )
