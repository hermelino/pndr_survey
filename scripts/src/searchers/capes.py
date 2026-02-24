"""Buscador semi-automático para Portal de Periódicos CAPES.

Gera query formatada e instruções para busca manual.
Importa resultados via RIS ou CSV exportados do portal.
"""

from __future__ import annotations

import logging
from typing import List

from src.models import BibRecord
from src.searchers.base import BaseSearcher

logger = logging.getLogger("pndr_survey")

CAPES_URL = "https://www.periodicos.capes.gov.br/"


class CapesSearcher(BaseSearcher):
    """Busca semi-automática no Portal de Periódicos CAPES."""

    name = "capes"

    def build_query(self) -> str:
        """Retorna query booleana para o Portal CAPES."""
        return self.keywords

    def search(self) -> int:
        """Portal CAPES não suporta busca automática (CDN protection).

        Returns:
            0 (sempre — resultados vêm via importação).
        """
        logger.info(
            "Portal CAPES requer busca manual. "
            "Use save_query_instructions() para gerar o arquivo de instruções."
        )
        return 0

    def fetch_records(self) -> List[BibRecord]:
        """Retorna registros importados."""
        return self.records

    def _build_instructions(self, query: str) -> str:
        """Gera instruções detalhadas para busca no Portal CAPES."""
        return (
            "=" * 70 + "\n"
            "BUSCA NO PORTAL DE PERIÓDICOS CAPES\n"
            "=" * 70 + "\n\n"
            f"Query:\n{query}\n\n"
            "--- Instruções ---\n\n"
            "IMPORTANTE: Acesso requer rede institucional ou proxy CAFe.\n\n"
            f"1. Acesse {CAPES_URL}\n"
            "2. Faça login via CAFe (se necessário)\n"
            "3. Na busca avançada, cole a query acima\n"
            "4. Aplique filtros:\n"
            "   - Tipo: Artigos revisados por pares\n"
            "   - Idioma: Português, Inglês, Espanhol\n"
            "   - Período: conforme configuração do projeto\n"
            "5. Selecione todos os resultados\n"
            "6. Exporte como RIS (preferível) ou CSV\n"
            "7. Importe com:\n"
            "   python main.py search --import-capes <arquivo.ris>\n\n"
            "--- Dicas ---\n\n"
            "- O portal pode limitar exportação a 500 registros por vez\n"
            "- Se houver mais resultados, exporte em lotes e importe múltiplos arquivos\n"
            "- Formato RIS preserva mais metadados que CSV\n"
        )
