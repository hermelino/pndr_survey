#!/usr/bin/env python3
"""
Índice de Citação para Revisão Sistemática da PNDR.

Para cada artigo (publicado ou não) do ano X:
  IC(A) = citações recebidas de artigos publicados em X+1..2025
          / total de artigos publicados em X+1..2025

"Publicado" = artigo publicado em periódico (fonte scopus, scielo, capes-periódico).
"""

import json
import os
import re
import unicodedata
from collections import defaultdict
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────
BASE = Path(r"C:\OneDrive\github\pndr_survey")
REF_DIR = BASE / "data" / "3-ref-bib" / "refs_por_estudo"
BIB_FILE = BASE / "data" / "1-records" / "processed" / "bib_screened.json"
OUTPUT = BASE / "data" / "3-ref-bib" / "citation_index_results.json"
REPORT = BASE / "data" / "3-ref-bib" / "citation_index_report.txt"


# ── Helpers ────────────────────────────────────────────────────────────────
def normalize(text: str) -> str:
    """Strip accents, lowercase, collapse whitespace."""
    if not text:
        return ""
    text = unicodedata.normalize("NFD", text)
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", text.lower().strip())


def extract_lastnames(author_str: str) -> list[str]:
    """Extract plausible last names from an author string."""
    if not author_str:
        return []
    s = normalize(author_str)
    # remove connectors
    s = re.sub(r"\b(and|e|da|de|do|dos|das|jr|junior)\b", " ", s)
    # split on punctuation/separators
    parts = re.split(r"[,;/&\.\(\)\[\]]+", s)
    names = []
    for p in parts:
        tokens = p.split()
        for t in tokens:
            t = t.strip()
            if len(t) >= 3 and t.isalpha():
                names.append(t)
    return names


def is_published(study: dict) -> bool:
    """
    Determina se o estudo é 'publicado em periódico'.

    - scopus → publicado (periódicos indexados)
    - scielo → publicado (periódicos indexados)
    - capes  → publicado (periódicos CAPES — todos têm journal)
    - econpapers → depende: TDs e WPs são não-publicados,
                   artigos em periódico são publicados
    - anpec → NÃO publicado (apresentações em congresso)
    """
    key = study.get("key", "")

    # Manual overrides for econpapers entries with known status
    PUBLISHED_KEYS = {
        # Publicados em periódico (verificado manualmente)
        "econpapers-2014-viana-goncalves-linhares",  # Revista de la CEPAL
        "econpapers-2015-oliveira-arriel-rodrigues",  # Economia & Região
        "econpapers-2017-oliveira-resende-oliveira",  # Plan. e Políticas Públicas
        "econpapers-2024-ribeiro",                    # Economia Aplicada
    }
    UNPUBLISHED_KEYS = {
        # Textos para Discussão / Working Papers (verificado)
        "econpapers-2007-silva-resende-neto",     # IPEA TD 1259
        "econpapers-2011-resende",                # IPEA TD 1777
        "econpapers-2014-goncalves-soares-linhares",  # WP ANPEC
        "econpapers-2014-resende",                # IPEA TD 1918
        "econpapers-2015-oliveira-terra-resende",  # IPEA TD
        "econpapers-2015-resende-silva-filho",     # IPEA TD 2145
    }

    if key in PUBLISHED_KEYS:
        return True
    if key in UNPUBLISHED_KEYS:
        return False

    src = study.get("source", "")

    if src == "scopus":
        return True
    if src == "scielo":
        return True
    if src == "capes":
        return True   # CAPES Periódicos: todos têm journal
    if src == "anpec":
        return False   # apresentações em congresso
    return False


def _classify_label(result: dict) -> str:
    """Return a human-readable classification label consistent with is_published()."""
    src = result.get("source", "")
    if result.get("is_published"):
        pub_type = result.get("publication_type", "")
        return pub_type if pub_type else f"periódico ({src})"
    # Unpublished: use source-based label
    labels = {
        "anpec": "apresentação congresso",
        "econpapers": "texto p/ discussão",
    }
    return labels.get(src, f"não-publicado ({src})")


# ── Load studies ───────────────────────────────────────────────────────────
def load_studies():
    """Load all 54 studies from ref JSON files + bib_screened metadata."""
    # Load bib_screened for publication_type lookup
    with open(BIB_FILE, "r", encoding="utf-8") as f:
        bib_records = json.load(f)

    # Index bib by (source_db, year, normalized first author lastname)
    bib_index = {}
    for rec in bib_records:
        src = rec.get("source_db", "")
        yr = rec.get("year")
        authors = rec.get("authors", "")
        lastnames = extract_lastnames(authors)
        key_name = lastnames[0] if lastnames else ""
        bib_index[(src, yr, key_name)] = rec

    studies = {}
    json_files = sorted(f for f in os.listdir(REF_DIR) if f.endswith(".json"))

    for fname in json_files:
        key = fname.replace("_refs.json", "")
        with open(REF_DIR / fname, "r", encoding="utf-8") as f:
            data = json.load(f)

        meta = data.get("meta", {})
        parts = key.split("-")
        source = parts[0]
        year = int(parts[1])
        author_part = "-".join(parts[2:])
        author_lastnames = [normalize(a) for a in author_part.split("-") if len(a) >= 3]

        # Try to match to bib_screened
        bib_match = None
        for bk, bv in bib_index.items():
            if bk[1] == year:
                bib_names = extract_lastnames(bv.get("authors", ""))
                if any(n in bib_names for n in author_lastnames):
                    if bk[0] == source or bk[0] == "":
                        bib_match = bv
                        break
        if bib_match is None:
            # Broader match: just year + author
            for bk, bv in bib_index.items():
                if bk[1] == year:
                    bib_names = extract_lastnames(bv.get("authors", ""))
                    if any(n in bib_names for n in author_lastnames):
                        bib_match = bv
                        break

        pub_type = ""
        title_full = meta.get("titulo_estudo", "")
        bib_title = ""
        if bib_match:
            pub_type = bib_match.get("publication_type", "")
            bib_title = bib_match.get("title", "")
            if not title_full:
                title_full = bib_title

        study = {
            "key": key,
            "year": year,
            "source": source,
            "authors_from_filename": author_lastnames,
            "title": title_full,
            "bib_title": bib_title,
            "publication_type": pub_type,
            "estudo_num": meta.get("estudo_num", ""),
            "pdf": meta.get("pdf", ""),
            "total_refs": data.get("total_referencias", 0),
            "references": data.get("referencias", []),
        }
        study["is_published"] = is_published(study)

        studies[key] = study

    return studies


# ── Cross-citation matching ───────────────────────────────────────────────
def match_reference_to_study(ref: dict, target_study: dict) -> float:
    """
    Score how well a reference matches a target study.
    Returns 0 (no match) to 1 (strong match).
    """
    ref_raw = normalize(ref.get("raw", ""))
    ref_ano = ref.get("ano", "")
    ref_autor = normalize(ref.get("autor", ""))
    ref_titulo = normalize(ref.get("titulo", ""))

    target_year = target_study["year"]
    target_names = target_study["authors_from_filename"]
    target_title = normalize(target_study["title"])

    # Year check: ref year must be within ±2 of target year
    # (accounts for working paper year vs publication year)
    year_matched = False
    if ref_ano:
        try:
            ref_year = int(ref_ano)
            if abs(ref_year - target_year) > 2:
                return 0.0
            if abs(ref_year - target_year) <= 1:
                year_matched = True
        except ValueError:
            pass
    else:
        # No year in reference → require stronger name/title match
        # Try to find a 4-digit year in the raw text near the target year
        years_in_raw = re.findall(r"\b(19\d{2}|20[0-2]\d)\b", ref_raw)
        if years_in_raw:
            closest = min(years_in_raw, key=lambda y: abs(int(y) - target_year))
            if abs(int(closest) - target_year) > 2:
                return 0.0
            if abs(int(closest) - target_year) <= 1:
                year_matched = True

    # Author name matching
    names_matched = 0
    total_target_names = len(target_names)
    if total_target_names == 0:
        return 0.0

    for tname in target_names:
        if tname in ref_raw or tname in ref_autor:
            names_matched += 1

    if names_matched == 0:
        return 0.0

    name_score = names_matched / total_target_names

    # Title matching (bonus)
    title_score = 0.0
    if target_title and len(target_title) > 10:
        # Check if significant title words appear in the reference
        title_words = [w for w in target_title.split() if len(w) >= 5]
        if title_words:
            title_matches = sum(1 for w in title_words if w in ref_raw)
            title_score = title_matches / len(title_words)

    # Combined score
    score = name_score * 0.7 + title_score * 0.3

    # Require at least 2 author names matched for multi-author papers
    if total_target_names >= 2 and names_matched < 2:
        score *= 0.5

    # For single-author targets (e.g. "resende"), require year match
    # AND significant title overlap to avoid false positives
    if total_target_names == 1:
        if not year_matched:
            return 0.0
        # Single common name → need title evidence or exact context
        if title_score < 0.15:
            score *= 0.3  # heavily penalize without title support

    # Penalize if year was not matched at all
    if not year_matched:
        score *= 0.6

    # Strong match: all authors + year matches exactly
    if names_matched == total_target_names and year_matched:
        if total_target_names >= 2:
            score = max(score, 0.9)
        elif title_score >= 0.15:
            score = max(score, 0.9)

    return score


def build_cross_citations(studies: dict) -> dict:
    """
    For each study, find which other studies it cites.
    Returns dict: citing_key -> list of (cited_key, score).
    """
    cross_citations = {}
    study_keys = list(studies.keys())

    for citing_key, citing_study in studies.items():
        citations = []
        for ref in citing_study["references"]:
            best_match = None
            best_score = 0.0

            for target_key in study_keys:
                if target_key == citing_key:
                    continue
                # Chronological constraint: citing study must be from
                # the same year or later than the cited study
                if citing_study["year"] < studies[target_key]["year"]:
                    continue
                score = match_reference_to_study(ref, studies[target_key])
                if score > best_score and score >= 0.4:
                    best_score = score
                    best_match = target_key

            if best_match:
                citations.append({
                    "cited_study": best_match,
                    "score": round(best_score, 3),
                    "ref_raw": ref.get("raw", "")[:120],
                })

        # Deduplicate: keep highest-scoring match per cited study
        seen = {}
        for c in citations:
            ck = c["cited_study"]
            if ck not in seen or c["score"] > seen[ck]["score"]:
                seen[ck] = c
        cross_citations[citing_key] = list(seen.values())

    return cross_citations


# ── Citation Index computation ─────────────────────────────────────────────
def compute_citation_index(studies: dict, cross_citations: dict):
    """
    Para cada artigo A do ano X:
    IC(A) = citações de artigos publicados em [X+1, 2025] / total publicados em [X+1, 2025]
    """
    # Build reverse map: cited_key -> list of citing studies
    cited_by = defaultdict(list)
    for citing_key, cites in cross_citations.items():
        for c in cites:
            cited_by[c["cited_study"]].append({
                "citing_study": citing_key,
                "score": c["score"],
            })

    results = []
    for key, study in studies.items():
        year_x = study["year"]

        # Published articles from X+1 to 2025 in dataset
        published_after = [
            k for k, s in studies.items()
            if s["is_published"] and s["year"] > year_x and s["year"] <= 2025
        ]
        n_published_after = len(published_after)

        # All articles from X+1 to 2025 (for alternative index)
        all_after = [
            k for k, s in studies.items()
            if s["year"] > year_x and s["year"] <= 2025
        ]
        n_all_after = len(all_after)

        # Citations received from published articles in X+1..2025
        cit_from_published = [
            cb for cb in cited_by.get(key, [])
            if studies[cb["citing_study"]]["is_published"]
            and studies[cb["citing_study"]]["year"] > year_x
            and studies[cb["citing_study"]]["year"] <= 2025
        ]

        # Citations received from ALL articles in X+1..2025
        cit_from_all = [
            cb for cb in cited_by.get(key, [])
            if studies[cb["citing_study"]]["year"] > year_x
            and studies[cb["citing_study"]]["year"] <= 2025
        ]

        ic_published = (
            len(cit_from_published) / n_published_after
            if n_published_after > 0
            else 0.0
        )
        ic_all = (
            len(cit_from_all) / n_all_after
            if n_all_after > 0
            else 0.0
        )

        results.append({
            "key": key,
            "year": year_x,
            "source": study["source"],
            "publication_type": study["publication_type"],
            "is_published": study["is_published"],
            "title": study["title"][:100],
            "authors": "-".join(study["authors_from_filename"]),
            "total_refs": study["total_refs"],
            "citations_received_from_published": len(cit_from_published),
            "citations_received_from_all": len(cit_from_all),
            "n_published_after": n_published_after,
            "n_all_after": n_all_after,
            "IC_published": round(ic_published, 4),
            "IC_all": round(ic_all, 4),
            "cited_by_published": [
                cb["citing_study"] for cb in cit_from_published
            ],
            "cited_by_all": [cb["citing_study"] for cb in cit_from_all],
            "cites_in_dataset": [
                c["cited_study"] for c in cross_citations.get(key, [])
            ],
        })

    results.sort(key=lambda r: r["IC_published"], reverse=True)
    return results


# ── Report ─────────────────────────────────────────────────────────────────
def generate_report(studies, results, cross_citations):
    lines = []
    lines.append("=" * 90)
    lines.append("ÍNDICE DE CITAÇÃO PARA REVISÃO SISTEMÁTICA DA PNDR")
    lines.append("=" * 90)
    lines.append("")

    # Summary
    n_pub = sum(1 for s in studies.values() if s["is_published"])
    n_unpub = sum(1 for s in studies.values() if not s["is_published"])
    total_cross = sum(len(v) for v in cross_citations.values())
    lines.append(f"Total de estudos:              {len(studies)}")
    lines.append(f"  Publicados (periódico):      {n_pub}")
    lines.append(f"  Não publicados (TD/conf.):   {n_unpub}")
    lines.append(f"Total de citações cruzadas:    {total_cross}")
    lines.append("")

    # Year distribution
    from collections import Counter
    year_counts = Counter(s["year"] for s in studies.values())
    lines.append("Distribuição por ano:")
    for yr in sorted(year_counts):
        n_p = sum(1 for s in studies.values() if s["year"] == yr and s["is_published"])
        n_u = sum(1 for s in studies.values() if s["year"] == yr and not s["is_published"])
        lines.append(f"  {yr}: {year_counts[yr]:2d} estudos ({n_p} pub, {n_u} não-pub)")
    lines.append("")

    # Formula
    lines.append("FÓRMULA:")
    lines.append("  IC(A) = citações de artigos publicados em [X+1, 2025]")
    lines.append("          / total de artigos publicados em [X+1, 2025]")
    lines.append("")
    lines.append("  onde X = ano do artigo A")
    lines.append("  'Publicado' = artigo em periódico (scopus, scielo, capes-periódico)")
    lines.append("")

    # Results table
    lines.append("-" * 90)
    lines.append(f"{'Rank':>4} {'Estudo':<45} {'Ano':>4} {'Pub?':>4} "
                 f"{'Cit':>3} {'N':>3} {'IC':>6} {'Tipo':<20}")
    lines.append("-" * 90)

    for i, r in enumerate(results, 1):
        pub_flag = "Sim" if r["is_published"] else "Não"
        short_key = r["key"][:43]
        pub_type = _classify_label(r)[:18]
        lines.append(
            f"{i:4d} {short_key:<45} {r['year']:>4} {pub_flag:>4} "
            f"{r['citations_received_from_published']:>3} "
            f"{r['n_published_after']:>3} "
            f"{r['IC_published']:>6.4f} {pub_type:<20}"
        )

    lines.append("-" * 90)
    lines.append("")

    # Highlight unpublished articles with high IC
    lines.append("=" * 90)
    lines.append("ARTIGOS NÃO-PUBLICADOS COM IC > 0 (candidatos à inclusão)")
    lines.append("=" * 90)
    unpub_with_cit = [r for r in results if not r["is_published"] and r["IC_published"] > 0]
    if unpub_with_cit:
        for r in unpub_with_cit:
            lines.append(f"\n  {r['key']}")
            lines.append(f"    Ano: {r['year']}, IC: {r['IC_published']:.4f}")
            lines.append(f"    Título: {r['title']}")
            lines.append(f"    Citado por (publicados):")
            for cb in r["cited_by_published"]:
                lines.append(f"      - {cb}")
    else:
        lines.append("  Nenhum artigo não-publicado recebeu citação de artigos publicados.")

    lines.append("")

    # Highlight unpublished articles with IC = 0 (not cited by published)
    lines.append("=" * 90)
    lines.append("ARTIGOS NÃO-PUBLICADOS COM IC = 0 (não citados por publicados)")
    lines.append("=" * 90)
    unpub_zero = sorted(
        [r for r in results if not r["is_published"] and r["IC_published"] == 0],
        key=lambda r: (r["year"], r["key"]),
    )
    if unpub_zero:
        lines.append("")
        lines.append(f"{'Estudo':<45} {'Ano':>4} {'Tipo':<25} {'Cit. total':>10}")
        lines.append("-" * 90)
        for r in unpub_zero:
            pub_type = _classify_label(r)[:23]
            cit_all = r["citations_received_from_all"]
            lines.append(
                f"{r['key']:<45} {r['year']:>4} {pub_type:<25} {cit_all:>10}"
            )
        lines.append("-" * 90)
        lines.append(f"Total: {len(unpub_zero)} artigos não-publicados sem citação de publicados")
    else:
        lines.append("  Todos os artigos não-publicados receberam ao menos uma citação de publicados.")
    lines.append("")

    # Detail: cross-citations per study
    lines.append("=" * 90)
    lines.append("DETALHE: CITAÇÕES CRUZADAS POR ESTUDO")
    lines.append("=" * 90)
    for r in results:
        if r["citations_received_from_all"] > 0 or len(r["cites_in_dataset"]) > 0:
            lines.append(f"\n  {r['key']} ({r['year']}, {'PUB' if r['is_published'] else 'NÃO-PUB'})")
            if r["cited_by_all"]:
                lines.append(f"    Citado por ({len(r['cited_by_all'])}):")
                for cb in r["cited_by_all"]:
                    pub = "pub" if studies[cb]["is_published"] else "np"
                    lines.append(f"      ← {cb} ({studies[cb]['year']}, {pub})")
            if r["cites_in_dataset"]:
                lines.append(f"    Cita ({len(r['cites_in_dataset'])}):")
                for ct in r["cites_in_dataset"]:
                    pub = "pub" if studies[ct]["is_published"] else "np"
                    lines.append(f"      → {ct} ({studies[ct]['year']}, {pub})")

    return "\n".join(lines)


# ── Main ───────────────────────────────────────────────────────────────────
def main():
    print("Carregando estudos...")
    studies = load_studies()
    print(f"  {len(studies)} estudos carregados")

    n_pub = sum(1 for s in studies.values() if s["is_published"])
    print(f"  {n_pub} publicados, {len(studies) - n_pub} não-publicados")

    print("\nDetectando citações cruzadas...")
    cross_citations = build_cross_citations(studies)
    total_cross = sum(len(v) for v in cross_citations.values())
    print(f"  {total_cross} citações cruzadas detectadas")

    print("\nCalculando índice de citação...")
    results = compute_citation_index(studies, cross_citations)

    print("\nGerando relatório...")
    report = generate_report(studies, results, cross_citations)

    # Save results
    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    with open(REPORT, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"\nResultados salvos em:")
    print(f"  {OUTPUT}")
    print(f"  {REPORT}")

    # Print summary
    print("\n" + "=" * 70)
    print("TOP 15 por IC (citações de publicados / total publicados depois):")
    print("=" * 70)
    print(f"{'#':>3} {'Estudo':<42} {'Ano':>4} {'Pub':>3} {'Cit':>3} {'N':>3} {'IC':>6}")
    print("-" * 70)
    for i, r in enumerate(results[:15], 1):
        p = "S" if r["is_published"] else "N"
        print(
            f"{i:3d} {r['key'][:40]:<42} {r['year']:>4} {p:>3} "
            f"{r['citations_received_from_published']:>3} "
            f"{r['n_published_after']:>3} "
            f"{r['IC_published']:>6.4f}"
        )


if __name__ == "__main__":
    main()
