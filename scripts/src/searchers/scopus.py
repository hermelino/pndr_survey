"""Buscador semi-automático para Scopus.

Gera query formatada na sintaxe Scopus (TITLE-ABS-KEY) e instruções
para busca manual via proxy CAPES. Importa resultados via CSV ou RIS.
"""

from __future__ import annotations

import logging
import re
from typing import List

from src.models import BibRecord
from src.searchers.base import BaseSearcher

logger = logging.getLogger("pndr_survey")


class ScopusSearcher(BaseSearcher):
    """Busca semi-automática no Scopus."""

    name = "scopus"

    def build_query(self) -> str:
        """Converte keywords para a sintaxe Scopus (TITLE-ABS-KEY).

        Transforma a query genérica em blocos TITLE-ABS-KEY().
        """
        # Envolver cada bloco entre parênteses em TITLE-ABS-KEY()
        query = self.keywords
        # Substituir blocos entre parênteses por TITLE-ABS-KEY(bloco)
        blocks = re.findall(r"\(([^)]+)\)", query)
        scopus_query = " AND ".join(f'TITLE-ABS-KEY({block})' for block in blocks)
        return scopus_query or f"TITLE-ABS-KEY({query})"

    def search(self) -> int:
        """Scopus requer API key ou busca manual via proxy CAPES.

        Returns:
            0 (sempre — resultados vêm via importação).
        """
        logger.info(
            "Scopus requer busca manual ou API key. "
            "Use save_query_instructions() para gerar o arquivo de instruções."
        )
        return 0

    def fetch_records(self) -> List[BibRecord]:
        """Retorna registros importados."""
        return self.records

    def _build_instructions(self, query: str) -> str:
        """Gera instruções detalhadas para busca no Scopus."""
        return (
            "=" * 70 + "\n"
            "BUSCA NO SCOPUS\n"
            "=" * 70 + "\n\n"
            f"Query (sintaxe Scopus):\n{query}\n\n"
            "--- Via Proxy CAPES ---\n\n"
            "1. Acesse Scopus via proxy CAPES:\n"
            "   https://www-scopus-com.ez##.periodicos.capes.gov.br/\n"
            "   (substitua ## pelo número da sua instituição)\n"
            "2. Vá em 'Advanced Search'\n"
            "3. Cole a query acima\n"
            "4. Execute a busca\n"
            "5. Selecione todos os resultados\n"
            "6. Exporte como CSV (com todos os campos) ou RIS\n"
            "7. Importe com:\n"
            "   python main.py search --import-scopus <arquivo.csv>\n\n"
            "--- Dicas ---\n\n"
            "- Scopus limita exportação a 2.000 registros por vez\n"
            "- CSV do Scopus usa vírgula como separador\n"
            "- O campo 'Source title' corresponde ao periódico\n"
        )
