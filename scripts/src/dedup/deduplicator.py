"""Deduplicação de registros bibliográficos por DOI e similaridade de título.

Duas fases:
  1. Match exato por DOI normalizado
  2. Match fuzzy por título (token_sort_ratio) + verificação de ano e autor/periódico

Baseado na implementação do slr-disasters-birth-outcomes, adaptado para PNDR.
"""

from __future__ import annotations

import logging
import re
from typing import Dict, List, Set, Tuple

from rapidfuzz import fuzz
from unidecode import unidecode

from src.models import BibRecord, SOURCE_PRIORITY

logger = logging.getLogger("pndr_survey")

# Stopwords para normalização de título (PT + EN + ES)
STOPWORDS: Set[str] = {
    # English
    "the", "a", "an", "of", "in", "on", "at", "to", "for", "and", "or",
    "with", "by", "from", "as", "is", "was", "are", "were", "been",
    # Português
    "o", "os", "um", "uma", "uns", "umas", "de", "do", "da",
    "dos", "das", "em", "no", "na", "nos", "nas", "por", "para", "com",
    "que", "se", "ao", "aos",
    # Espanhol
    "el", "la", "los", "las", "un", "una", "unos", "unas", "del", "en",
    "con", "que",
}


def normalize_doi(doi: str) -> str:
    """Normaliza DOI: lowercase, remove prefixos comuns."""
    doi = doi.strip().lower()
    for prefix in ("https://doi.org/", "http://doi.org/", "doi:", "doi.org/"):
        if doi.startswith(prefix):
            doi = doi[len(prefix):]
    return doi


def normalize_title(title: str) -> str:
    """Normaliza título para comparação fuzzy.

    Remove acentos, pontuação, stopwords. Retorna palavras em lowercase.
    """
    text = unidecode(title).lower()
    text = re.sub(r"[^\w\s]", " ", text)
    words = [w for w in text.split() if w not in STOPWORDS]
    return " ".join(words)


def _choose_keeper(records: List[BibRecord]) -> BibRecord:
    """Escolhe o registro a manter: maior completude, depois prioridade da base."""
    return max(
        records,
        key=lambda r: (
            r.completeness_score(),
            -SOURCE_PRIORITY.get(r.source_db, 99),
        ),
    )


def deduplicate(
    records: List[BibRecord],
    *,
    fuzzy_threshold: int = 90,
) -> Tuple[List[BibRecord], List[BibRecord]]:
    """Deduplica registros em duas fases.

    Fase 1: Match exato por DOI normalizado.
    Fase 2: Match fuzzy por título (token_sort_ratio >= threshold)
            + verificação: mesmo ano E (mesmo primeiro autor OU mesmo periódico).

    Args:
        records: Lista de BibRecords de todas as bases.
        fuzzy_threshold: Limiar para token_sort_ratio (0-100, padrão 90).

    Returns:
        Tupla (registros_únicos, registros_duplicados).
        Registros duplicados têm is_duplicate=True e duplicate_of preenchido.
    """
    if not records:
        return [], []

    # === Fase 1: DOI exato ===
    doi_groups: Dict[str, List[int]] = {}
    for i, rec in enumerate(records):
        if rec.doi:
            ndoi = normalize_doi(rec.doi)
            if ndoi:
                doi_groups.setdefault(ndoi, []).append(i)

    duplicates_doi: Set[int] = set()
    for indices in doi_groups.values():
        if len(indices) > 1:
            group = [records[i] for i in indices]
            keeper = _choose_keeper(group)
            for i in indices:
                if records[i] is not keeper:
                    records[i].is_duplicate = True
                    records[i].duplicate_of = keeper.source_id
                    duplicates_doi.add(i)

    logger.info("Fase 1 (DOI): %d duplicatas identificadas", len(duplicates_doi))

    # === Fase 2: Fuzzy por título ===
    remaining_indices = [
        i for i in range(len(records)) if i not in duplicates_doi
    ]

    # Pré-computar títulos normalizados
    normalized: Dict[int, dict] = {}
    for i in remaining_indices:
        rec = records[i]
        normalized[i] = {
            "title": normalize_title(rec.title),
            "year": rec.year,
            "first_author": rec.first_author.lower() if rec.first_author else "",
            "journal": rec.journal.lower() if rec.journal else "",
        }

    duplicates_fuzzy: Set[int] = set()

    for idx, i in enumerate(remaining_indices):
        if i in duplicates_fuzzy:
            continue

        ni = normalized[i]
        if not ni["title"]:
            continue

        cluster = [i]

        for j in remaining_indices[idx + 1:]:
            if j in duplicates_fuzzy:
                continue

            nj = normalized[j]
            if not nj["title"]:
                continue

            # Filtro rápido: se ambos têm ano e são diferentes, pular
            if ni["year"] and nj["year"] and ni["year"] != nj["year"]:
                continue

            # Similaridade de título
            score = fuzz.token_sort_ratio(ni["title"], nj["title"])
            if score < fuzzy_threshold:
                continue

            # Verificação: mesmo primeiro autor OU mesmo periódico
            author_match = (
                ni["first_author"]
                and nj["first_author"]
                and fuzz.ratio(ni["first_author"], nj["first_author"]) >= 80
            )
            journal_match = (
                ni["journal"]
                and nj["journal"]
                and fuzz.ratio(ni["journal"], nj["journal"]) >= 80
            )

            if not author_match and not journal_match:
                continue

            cluster.append(j)

        if len(cluster) > 1:
            group = [records[ci] for ci in cluster]
            keeper = _choose_keeper(group)
            for ci in cluster:
                if records[ci] is not keeper:
                    records[ci].is_duplicate = True
                    records[ci].duplicate_of = keeper.source_id
                    duplicates_fuzzy.add(ci)

    logger.info("Fase 2 (fuzzy): %d duplicatas identificadas", len(duplicates_fuzzy))

    all_dup = duplicates_doi | duplicates_fuzzy
    unique = [records[i] for i in range(len(records)) if i not in all_dup]
    duplicates = [records[i] for i in sorted(all_dup)]

    logger.info(
        "Deduplicação concluída: %d únicos, %d duplicatas (DOI=%d, fuzzy=%d)",
        len(unique), len(duplicates), len(duplicates_doi), len(duplicates_fuzzy),
    )

    return unique, duplicates
