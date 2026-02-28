"""
One-time script: mark TD/WP and duplicate entries as duplicates in bib_records.json,
bib_screened.json, and duplicates_removed.csv.

Identifies 8 records that represent the same work as their published counterparts:
- 3 TDs (IPEA working papers)
- 2 congress presentations (ANPEC)
- 1 SciELO duplicate (same publication as Scopus, no DOI)
- 2 EconPapers mirrors (same published article, no PDF)
"""

import json
import csv
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

BASE = Path(__file__).resolve().parent.parent / "data"
BIB_RECORDS = BASE / "1-records" / "processed" / "bib_records.json"
BIB_SCREENED = BASE / "1-records" / "processed" / "bib_screened.json"
DUPLICATES_CSV = BASE / "1-records" / "processed" / "duplicates_removed.csv"

# Each entry: (url_substring, source_db, duplicate_of_doi, reason, label)
DUPLICATES_TO_MARK = [
    {
        "url_contains": "RePEc:ipe:ipetds:2133",
        "source_db": "econpapers",
        "duplicate_of": "10.1590/0103-6351/3397",
        "reason": "TD IPEA 2133 — publicado como scopus-2018-oliveira-terra-resende",
        "label": "econpapers-2015-oliveira-terra-resende (TD)",
    },
    {
        "url_contains": "RePEc:anp:en2015:172",
        "source_db": "econpapers",
        "duplicate_of": "10.1590/0103-6351/3397",
        "reason": "Congresso ANPEC 2015 — publicado como scopus-2018-oliveira-terra-resende",
        "label": "anpec-2015-oliveira-terra-resende (congresso)",
    },
    {
        "url_contains": "RePEc:nov:artigo:v:28:y:2018:i:3",
        "source_db": "econpapers",
        "duplicate_of": "10.1590/0103-6351/3397",
        "reason": "Mirror EconPapers de scopus-2018-oliveira-terra-resende (Nova Economia)",
        "label": "econpapers-2018-oliveira-terra-resende (mirror)",
    },
    {
        "url_contains": "RePEc:ipe:ipetds:2145",
        "source_db": "econpapers",
        "duplicate_of": "10.1007/s10037-018-0123-5",
        "reason": "TD IPEA 2145 — publicado como scopus-2018-resende-silva-filho",
        "label": "econpapers-2015-resende-silva-filho (TD)",
    },
    {
        "url_contains": "RePEc:spr:jahrfr:v:38:y:2018:i:2",
        "source_db": "econpapers",
        "duplicate_of": "10.1007/s10037-018-0123-5",
        "reason": "Mirror EconPapers de scopus-2018-resende-silva-filho (Jahrbuch)",
        "label": "econpapers-2018-resende-silva-filho (mirror)",
    },
    {
        "url_contains": "RePEc:ipe:ipetds:1259",
        "source_db": "econpapers",
        "duplicate_of": "10.1590/s0101-41612009000100004",
        "reason": "TD IPEA 1259 — publicado como scopus-2009-silva-resende-neto",
        "label": "econpapers-2007-silva-resende-neto (TD)",
    },
    {
        "url_contains": "encontro2006/artigos/A06A132",
        "source_db": "anpec",
        "duplicate_of": "10.1590/s0101-41612009000100004",
        "reason": "Congresso ANPEC 2006 — publicado como scopus-2009-silva-resende-neto",
        "label": "anpec-2006-silva-resende-neto (congresso)",
    },
    {
        "url_contains": "S0101-41612009000100004",
        "source_db": "scielo",
        "duplicate_of": "10.1590/s0101-41612009000100004",
        "reason": "Mesma publicacao que scopus-2009-silva-resende-neto (sem DOI)",
        "label": "scielo-2009-silva-resende-neto (duplicata pub.)",
    },
]


def find_record(records: list[dict], spec: dict) -> int | None:
    """Find record index matching spec's url_contains and source_db."""
    for i, rec in enumerate(records):
        if rec["source_db"] != spec["source_db"]:
            continue
        url = rec.get("url", "") or ""
        pdf_url = rec.get("pdf_url", "") or ""
        source_id = rec.get("source_id", "") or ""
        if (
            spec["url_contains"] in url
            or spec["url_contains"] in pdf_url
            or spec["url_contains"] in source_id
        ):
            return i
    return None


def mark_duplicates_in_json(json_path: Path, specs: list[dict]) -> list[dict]:
    """Load JSON, mark records as duplicates, save, return matched records info."""
    with open(json_path, "r", encoding="utf-8") as f:
        records = json.load(f)

    total_before = len(records)
    dups_before = sum(1 for r in records if r.get("is_duplicate"))
    matched = []

    for spec in specs:
        idx = find_record(records, spec)
        if idx is None:
            logger.warning("NOT FOUND in %s: %s", json_path.name, spec["label"])
            continue

        rec = records[idx]
        if rec.get("is_duplicate"):
            logger.info("ALREADY DUPLICATE in %s: [%d] %s", json_path.name, idx, spec["label"])
            continue

        rec["is_duplicate"] = True
        rec["duplicate_of"] = spec["duplicate_of"]
        rec["screening_status"] = "excluded_duplicate"

        matched.append({
            "index": idx,
            "label": spec["label"],
            "title": rec["title"][:80],
            "source_db": rec["source_db"],
            "year": rec.get("year"),
            "authors": rec.get("authors", "")[:60],
            "journal": rec.get("journal", ""),
            "doi": rec.get("doi", ""),
            "url": rec.get("url", ""),
            "duplicate_of": spec["duplicate_of"],
            "reason": spec["reason"],
        })
        logger.info("MARKED in %s: [%d] %s", json_path.name, idx, spec["label"])

    dups_after = sum(1 for r in records if r.get("is_duplicate"))
    total_after = len(records)

    assert total_after == total_before, f"Record count changed: {total_before} -> {total_after}"
    logger.info(
        "%s: %d records total, duplicates %d -> %d (+%d)",
        json_path.name, total_after, dups_before, dups_after, dups_after - dups_before,
    )

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)

    return matched


def append_to_csv(csv_path: Path, matched: list[dict]) -> None:
    """Append new duplicate entries to duplicates_removed.csv."""
    with open(csv_path, "a", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, delimiter=";")
        for m in matched:
            writer.writerow([
                "manual_td_wp",       # fase
                m["source_db"],       # source_db
                m["title"],           # title
                m["authors"],         # authors
                str(m["year"] or ""), # year
                m["journal"],         # journal
                m["doi"],             # doi
                m["url"],             # url
                m["duplicate_of"],    # duplicate_of
                m["reason"],          # motivo
            ])
    logger.info("Appended %d entries to %s", len(matched), csv_path.name)


def validate_kept_versions(json_path: Path) -> None:
    """Verify the 3 kept published versions exist and are not duplicates."""
    with open(json_path, "r", encoding="utf-8") as f:
        records = json.load(f)

    kept_dois = [
        "10.1590/0103-6351/3397",
        "10.1007/s10037-018-0123-5",
        "10.1590/s0101-41612009000100004",
    ]
    for doi in kept_dois:
        found = [r for r in records if r.get("doi") == doi and r["source_db"] == "scopus"]
        assert len(found) == 1, f"Expected 1 scopus record with DOI {doi}, found {len(found)}"
        assert not found[0]["is_duplicate"], f"Kept version {doi} is marked as duplicate!"
        logger.info("VALIDATED kept: scopus DOI %s (not duplicate)", doi)


def main() -> None:
    logger.info("=== Marking TD/WP duplicates ===")
    logger.info("Processing bib_records.json...")
    matched_bib = mark_duplicates_in_json(BIB_RECORDS, DUPLICATES_TO_MARK)

    logger.info("Processing bib_screened.json...")
    matched_screened = mark_duplicates_in_json(BIB_SCREENED, DUPLICATES_TO_MARK)

    logger.info("Appending to duplicates_removed.csv...")
    append_to_csv(DUPLICATES_CSV, matched_bib)

    logger.info("Validating kept versions...")
    validate_kept_versions(BIB_RECORDS)

    logger.info("=== Summary ===")
    logger.info("bib_records.json: %d records marked", len(matched_bib))
    logger.info("bib_screened.json: %d records marked", len(matched_screened))
    logger.info("duplicates_removed.csv: %d entries appended", len(matched_bib))

    for m in matched_bib:
        logger.info("  - [%d] %s -> dup of %s", m["index"], m["label"], m["duplicate_of"])


if __name__ == "__main__":
    main()
