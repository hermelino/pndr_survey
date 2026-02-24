"""Exportação de resultados para CSV (UTF-8-BOM, ponto-e-vírgula)."""

from __future__ import annotations

import csv
import logging
from pathlib import Path
from typing import List

from src.exporters.common import flatten_all
from src.models import PaperRecord

logger = logging.getLogger("pndr_survey")


def export_csv(
    papers: List[PaperRecord],
    output_path: str | Path,
    *,
    delimiter: str = ";",
    encoding: str = "utf-8-sig",
) -> Path:
    """Exporta PaperRecords para arquivo CSV.

    Padrão brasileiro: UTF-8-BOM + ponto-e-vírgula como separador
    (abre corretamente no Excel PT-BR).

    Args:
        papers: Lista de PaperRecords.
        output_path: Caminho do arquivo .csv de saída.
        delimiter: Separador de campos (padrão ";").
        encoding: Encoding do arquivo (padrão "utf-8-sig" = UTF-8 com BOM).

    Returns:
        Path do arquivo criado.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    rows = flatten_all(papers)
    if not rows:
        logger.warning("Nenhum registro para exportar.")
        return output_path

    headers = list(rows[0].keys())

    with open(output_path, "w", newline="", encoding=encoding) as f:
        writer = csv.DictWriter(f, fieldnames=headers, delimiter=delimiter)
        writer.writeheader()
        writer.writerows(rows)

    logger.info("CSV exportado: %s (%d registros)", output_path, len(rows))
    return output_path
