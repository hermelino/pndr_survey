"""Pipeline de triagem pré-LLM com rastreabilidade PRISMA.

Steps:
  3. Filtro de tipo documental + idioma
  3b. Verificação de disponibilidade de PDF (flagging, não exclusão)

Step opcional (opt-in via --title-filter):
  4. Filtro de relevância por título (keywords PNDR)

A relevância temática é avaliada pelo LLM (Stage 1) ao invés de
keywords no título, evitando falsos negativos por títulos truncados.
"""

from __future__ import annotations

import logging
from typing import Dict, List, Set, Tuple

from unidecode import unidecode

from src.config import ScreeningConfig
from src.models import BibRecord, ScreeningStatus

logger = logging.getLogger("pndr_survey")


# =========================================================================
# Step 3 — Tipo documental + Idioma
# =========================================================================


def filter_doctype_language(
    records: List[BibRecord],
    config: ScreeningConfig,
) -> Tuple[List[BibRecord], List[BibRecord]]:
    """Filtra por tipo documental e idioma.

    Records com tipo ou idioma desconhecido (None) passam (benefício da dúvida).
    Apenas records com valores explicitamente inelegíveis são excluídos.

    Returns:
        Tupla (passed, excluded).
    """
    excluded_types: Set[str] = {t.lower().strip() for t in config.excluded_doctypes}
    eligible_langs: Set[str] = {l.lower().strip() for l in config.eligible_languages}

    passed: List[BibRecord] = []
    excluded: List[BibRecord] = []

    for rec in records:
        # Tipo: excluir apenas se conhecido E inelegível
        pub_type = (rec.publication_type or "").lower().strip()
        if pub_type and pub_type in excluded_types:
            rec.screening_status = ScreeningStatus.EXCLUDED_DOCTYPE
            rec.exclusion_reason = f"tipo: {rec.publication_type}"
            excluded.append(rec)
            continue

        # Idioma: excluir apenas se conhecido E não PT/EN
        lang = (rec.language or "").lower().strip()
        if lang and lang not in eligible_langs:
            rec.screening_status = ScreeningStatus.EXCLUDED_LANGUAGE
            rec.exclusion_reason = f"idioma: {rec.language}"
            excluded.append(rec)
            continue

        passed.append(rec)

    n_doctype = sum(
        1 for r in excluded
        if r.screening_status == ScreeningStatus.EXCLUDED_DOCTYPE
    )
    n_language = sum(
        1 for r in excluded
        if r.screening_status == ScreeningStatus.EXCLUDED_LANGUAGE
    )
    logger.info(
        "Step 3 (tipo+idioma): %d passaram, %d excluídos "
        "(tipo=%d, idioma=%d)",
        len(passed), len(excluded), n_doctype, n_language,
    )
    return passed, excluded


# =========================================================================
# Step 4 — Relevância por título
# =========================================================================


def filter_title_relevance(
    records: List[BibRecord],
    keywords: List[str],
) -> Tuple[List[BibRecord], List[BibRecord]]:
    """Filtra por relevância temática via keywords no título.

    Um record passa se seu título normalizado contém pelo menos
    uma das keywords PNDR.

    Returns:
        Tupla (passed, excluded).
    """
    normalized_kws = [unidecode(kw).lower() for kw in keywords]

    passed: List[BibRecord] = []
    excluded: List[BibRecord] = []

    for rec in records:
        title_norm = unidecode(rec.title).lower() if rec.title else ""
        if _title_matches(title_norm, normalized_kws):
            passed.append(rec)
        else:
            rec.screening_status = ScreeningStatus.EXCLUDED_RELEVANCE
            rec.exclusion_reason = f"título sem termos PNDR: {rec.title[:80]}"
            excluded.append(rec)

    logger.info(
        "Step 4 (relevância título): %d passaram, %d excluídos",
        len(passed), len(excluded),
    )
    return passed, excluded


def _title_matches(normalized_title: str, normalized_keywords: List[str]) -> bool:
    """Verifica se o título contém pelo menos uma keyword PNDR."""
    return any(kw in normalized_title for kw in normalized_keywords)


# =========================================================================
# Step 4b — Disponibilidade de PDF
# =========================================================================


def check_pdf_availability(
    records: List[BibRecord],
) -> Tuple[List[BibRecord], List[BibRecord]]:
    """Verifica disponibilidade de PDF.

    Records sem PDF são marcados como AWAITING_PDF (pendência,
    não exclusão definitiva). Permanecem no pipeline para
    tentativa manual de recuperação.

    Returns:
        Tupla (with_pdf, without_pdf).
    """
    with_pdf: List[BibRecord] = []
    without_pdf: List[BibRecord] = []

    for rec in records:
        if rec.pdf_url:
            with_pdf.append(rec)
        else:
            rec.screening_status = ScreeningStatus.AWAITING_PDF
            without_pdf.append(rec)

    logger.info(
        "Step 4b (PDF): %d com PDF, %d aguardando PDF",
        len(with_pdf), len(without_pdf),
    )
    return with_pdf, without_pdf


# =========================================================================
# Pipeline completo (steps 3→3b, opcionalmente 4)
# =========================================================================


def run_screening(
    records: List[BibRecord],
    config: ScreeningConfig,
    *,
    include_title_filter: bool = False,
) -> Dict[str, List[BibRecord]]:
    """Executa pipeline de triagem pré-LLM.

    Pipeline padrão: step 3 (tipo+idioma) → step 3b (PDF).
    A relevância temática é delegada ao LLM (Stage 1), que lê o
    texto completo e evita falsos negativos por títulos truncados.

    Com include_title_filter=True, adiciona step 4 (keywords no título)
    entre os steps 3 e 3b.

    Returns:
        Dict com chaves:
          "passed": passaram em tudo e têm PDF
          "awaiting_pdf": passaram nos filtros mas sem PDF
          "excluded_doctype": excluídos no step 3 (tipo)
          "excluded_language": excluídos no step 3 (idioma)
          "excluded_relevance": excluídos no step 4 (título, se ativo)
    """
    logger.info("Iniciando triagem de %d registros", len(records))

    # Step 3
    after_doctype, excluded_dl = filter_doctype_language(records, config)

    # Step 4 (opcional)
    excluded_rel: List[BibRecord] = []
    if include_title_filter:
        after_filter, excluded_rel = filter_title_relevance(
            after_doctype, config.relevance_keywords,
        )
    else:
        after_filter = after_doctype
        logger.info(
            "Step 4 (relevância título): desativado — "
            "relevância será avaliada pelo LLM"
        )

    # Step 3b
    with_pdf, without_pdf = check_pdf_availability(after_filter)

    # Marcar sobreviventes como incluídos (provisório, pode mudar no LLM)
    for rec in with_pdf:
        if rec.screening_status == ScreeningStatus.PENDING:
            rec.screening_status = ScreeningStatus.INCLUDED

    result = {
        "passed": with_pdf,
        "awaiting_pdf": without_pdf,
        "excluded_doctype": [
            r for r in excluded_dl
            if r.screening_status == ScreeningStatus.EXCLUDED_DOCTYPE
        ],
        "excluded_language": [
            r for r in excluded_dl
            if r.screening_status == ScreeningStatus.EXCLUDED_LANGUAGE
        ],
        "excluded_relevance": excluded_rel,
    }

    logger.info(
        "Triagem concluída: %d passaram, %d aguardando PDF, %d excluídos",
        len(result["passed"]),
        len(result["awaiting_pdf"]),
        len(result["excluded_doctype"])
        + len(result["excluded_language"])
        + len(result["excluded_relevance"]),
    )
    return result
