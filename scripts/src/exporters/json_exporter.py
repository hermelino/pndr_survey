"""Exportação de resultados para JSON."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import List

from src.exporters.common import flatten_all
from src.models import PaperRecord

logger = logging.getLogger("pndr_survey")


def export_json(
    papers: List[PaperRecord],
    output_path: str | Path,
    *,
    indent: int = 2,
) -> Path:
    """Exporta PaperRecords para arquivo JSON.

    Args:
        papers: Lista de PaperRecords.
        output_path: Caminho do arquivo .json de saída.
        indent: Indentação do JSON (padrão 2).

    Returns:
        Path do arquivo criado.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    rows = flatten_all(papers)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=indent)

    logger.info("JSON exportado: %s (%d registros)", output_path, len(rows))
    return output_path
