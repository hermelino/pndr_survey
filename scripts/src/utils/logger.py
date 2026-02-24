"""Logging estruturado com dual output (console + arquivo).

Uso:
    from src.utils.logger import setup_logging

    logger = setup_logging(output_dir="output/20260223_120000")
    logger.info("Pipeline iniciado")
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional


def setup_logging(
    *,
    console_level: str = "INFO",
    file_level: str = "DEBUG",
    output_dir: Optional[str | Path] = None,
    log_filename: str = "pipeline.log",
) -> logging.Logger:
    """Configura logger com handlers para console e arquivo.

    Args:
        console_level: Nível de log no console ("INFO" ou "DEBUG").
        file_level: Nível de log no arquivo (sempre "DEBUG" recomendado).
        output_dir: Diretório para salvar o arquivo de log. Se None, só console.
        log_filename: Nome do arquivo de log.

    Returns:
        Logger configurado com nome "pndr_survey".
    """
    logger = logging.getLogger("pndr_survey")
    logger.setLevel(logging.DEBUG)

    # Limpar handlers anteriores (evita duplicação em re-chamadas)
    logger.handlers.clear()

    # --- Console handler ---
    console = logging.StreamHandler()
    console.setLevel(getattr(logging, console_level.upper(), logging.INFO))
    console.setFormatter(logging.Formatter(
        "%(levelname)-8s %(message)s"
    ))
    logger.addHandler(console)

    # --- File handler ---
    if output_dir is not None:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(
            output_path / log_filename,
            encoding="utf-8",
        )
        file_handler.setLevel(getattr(logging, file_level.upper(), logging.DEBUG))
        file_handler.setFormatter(logging.Formatter(
            "%(asctime)s %(levelname)-8s [%(name)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        ))
        logger.addHandler(file_handler)

    return logger


def get_logger() -> logging.Logger:
    """Retorna o logger do projeto (deve ser configurado antes com setup_logging)."""
    return logging.getLogger("pndr_survey")
