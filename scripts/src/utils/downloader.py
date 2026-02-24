"""Download de PDFs com rate limiting e validação de integridade."""

from __future__ import annotations

import hashlib
import logging
import re
import time
from pathlib import Path
from typing import List, Optional, Tuple

import requests

from src.models import BibRecord

logger = logging.getLogger("pndr_survey")

RATE_LIMIT = 2.0  # segundos entre downloads
MIN_PDF_SIZE = 10_240  # 10 KB — abaixo disso provavelmente não é PDF válido
PDF_HEADER = b"%PDF"


def download_pdfs(
    records: List[BibRecord],
    output_dir: str | Path,
    *,
    rate_limit: float = RATE_LIMIT,
    verify_ssl: bool = True,
) -> Tuple[int, int]:
    """Baixa PDFs para os registros que têm pdf_url.

    Args:
        records: Lista de BibRecords (modifica pdf_url in-place se download falhar).
        output_dir: Diretório de destino para os PDFs.
        rate_limit: Segundos entre downloads.
        verify_ssl: Se True, verifica certificados SSL.

    Returns:
        Tupla (downloads_ok, downloads_falha).
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    candidates = [r for r in records if r.pdf_url and not r.is_duplicate]
    if not candidates:
        logger.info("Nenhum registro com pdf_url para download.")
        return 0, 0

    logger.info(f"Iniciando download de {len(candidates)} PDFs para {output_path}")

    session = requests.Session()
    session.headers.update({
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 Chrome/120.0 Safari/537.36"
        )
    })

    ok = 0
    fail = 0

    for i, record in enumerate(candidates):
        filename = _build_filename(record)
        filepath = output_path / filename

        if filepath.exists() and filepath.stat().st_size >= MIN_PDF_SIZE:
            logger.debug(f"Já existe: {filename}")
            ok += 1
            continue

        try:
            resp = session.get(record.pdf_url, timeout=60, verify=verify_ssl)
            resp.raise_for_status()

            # Validar conteúdo
            if not resp.content[:4].startswith(PDF_HEADER):
                logger.warning(f"Não é PDF válido: {record.pdf_url}")
                fail += 1
                continue

            if len(resp.content) < MIN_PDF_SIZE:
                logger.warning(f"PDF muito pequeno ({len(resp.content)} bytes): {record.pdf_url}")
                fail += 1
                continue

            filepath.write_bytes(resp.content)
            ok += 1
            logger.debug(f"OK: {filename} ({len(resp.content):,} bytes)")

        except requests.RequestException as e:
            logger.warning(f"Falha no download: {record.pdf_url} — {e}")
            fail += 1

        if (i + 1) % 10 == 0:
            logger.info(f"Progresso: {i + 1}/{len(candidates)} ({ok} ok, {fail} falhas)")

        time.sleep(rate_limit)

    logger.info(f"Downloads concluídos: {ok} ok, {fail} falhas de {len(candidates)} tentativas")
    return ok, fail


def _build_filename(record: BibRecord) -> str:
    """Gera nome de arquivo seguro a partir do BibRecord.

    Formato: {source_db}_{primeiro_autor}_{ano}.pdf
    """
    parts = []
    parts.append(record.source_db)

    if record.first_author:
        surname = record.first_author.split(",")[0].split()[-1]
        surname = _sanitize(surname)
        parts.append(surname)

    parts.append(str(record.year or "nd"))
    base = "_".join(parts)

    # Se já existe um arquivo com mesmo nome, adicionar hash curto
    if record.doi:
        short_hash = hashlib.md5(record.doi.encode()).hexdigest()[:6]
        base = f"{base}_{short_hash}"
    elif record.source_id:
        short_hash = hashlib.md5(record.source_id.encode()).hexdigest()[:6]
        base = f"{base}_{short_hash}"

    return f"{base}.pdf"


def _sanitize(text: str) -> str:
    """Remove caracteres não-alfanuméricos de um texto para uso em nomes de arquivo."""
    text = re.sub(r"[^\w]", "", text)
    return text[:30]
