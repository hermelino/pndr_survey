"""Gera tabela LaTeX do índice de citação cruzada (IC).

Lê citation_index_results.json, bibtex_key_map.json e references.bib
para produzir latex/tabela_ic.tex com estudos publicados e não publicados.

Uso: python generate_ic_table.py
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
IC_PATH = BASE_DIR / "data" / "3-ref-bib" / "citation_index_results.json"
KEY_MAP_PATH = BASE_DIR / "latex" / "bibtex_key_map.json"
BIB_PATH = BASE_DIR / "latex" / "references.bib"
OUTPUT_PATH = BASE_DIR / "latex" / "tabela_ic.tex"


def load_json(path: Path) -> list | dict:
    """Carrega arquivo JSON."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def parse_bib_journals(bib_path: Path) -> dict[str, str]:
    """Extrai nomes de periódicos do .bib indexados por chave BibTeX."""
    journals: dict[str, str] = {}
    current_key: str | None = None

    with open(bib_path, "r", encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()

            # Detectar início de entrada: @article{Key2024,
            if stripped.startswith("@") and "{" in stripped:
                current_key = stripped.split("{", 1)[1].rstrip(",").strip()

            # Detectar campo journal
            elif current_key:
                match = re.match(
                    r"journal\s*=\s*\{(.+)\}", stripped, re.IGNORECASE
                )
                if match:
                    journals[current_key] = match.group(1)

    return journals


def format_ic(value: float, n_after: int) -> str:
    """Formata IC para LaTeX: valor com vírgula decimal ou -- se N=0."""
    if n_after == 0:
        return "--"
    if value == 0:
        return "0{,}00"
    return f"{value:.2f}".replace(".", "{,}")


def generate_table(
    ic_data: list[dict],
    key_map: dict[str, str],
    journals: dict[str, str],
) -> str:
    """Gera string LaTeX da tabela IC com publicados e não publicados."""
    published = [e for e in ic_data if e.get("is_published", False)]
    unpublished = [e for e in ic_data if not e.get("is_published", True)]

    # Ordenar por IC_published descendente, desempate por chave
    published.sort(key=lambda x: (-x.get("IC_published", 0), x.get("key", "")))
    unpublished.sort(key=lambda x: (-x.get("IC_published", 0), x.get("key", "")))

    missing_keys: list[str] = []

    lines = [
        r"\begin{table}[htb]",
        r"\centering",
        r"\footnotesize",
        r"\caption{Resultados do Índice de Citação Cruzada (IC)}",
        r"\label{tab:ic-resultados}",
        r"\begin{tabular}{lp{6cm}r}",
        r"\toprule",
        r"\multicolumn{3}{l}{\textbf{Estudos publicados em periódicos}} \\",
        r"\midrule",
        r"Estudo & Periódico & IC \\",
        r"\midrule",
    ]

    # --- Publicados ---
    for entry in published:
        pdf_key = entry["key"]
        bib_key = key_map.get(pdf_key)

        if bib_key:
            estudo = rf"\citeonline{{{bib_key}}}"
            journal = journals.get(bib_key, "")
        else:
            missing_keys.append(pdf_key)
            estudo = pdf_key
            journal = ""

        n_after = entry.get("n_published_after", 0)
        ic_val = entry.get("IC_published", 0)
        ic_str = format_ic(ic_val, n_after)

        lines.append(f"{estudo} & {journal} & {ic_str} \\\\")

    # --- Separador e cabeçalho dos não publicados ---
    lines.extend([
        r"\midrule",
        r"\multicolumn{3}{l}{\textbf{Estudos não publicados}} \\",
        r"\midrule",
        r"\multicolumn{2}{l}{Artigo} & IC \\",
        r"\midrule",
    ])

    # --- Não publicados ---
    for entry in unpublished:
        pdf_key = entry["key"]
        bib_key = key_map.get(pdf_key)

        if bib_key:
            estudo = rf"\citeonline{{{bib_key}}}"
        else:
            missing_keys.append(pdf_key)
            estudo = pdf_key

        n_after = entry.get("n_published_after", 0)
        ic_val = entry.get("IC_published", 0)
        ic_str = format_ic(ic_val, n_after)

        lines.append(rf"\multicolumn{{2}}{{l}}{{{estudo}}} & {ic_str} \\")

    lines.extend([
        r"\bottomrule",
        r"\end{tabular}",
        r"\nota{-- = IC não calculável ($N=0$, sem publicações posteriores).}",
        r"\fonte{Elaboração própria.}",
        r"\end{table}",
    ])

    if missing_keys:
        print(f"AVISO: {len(missing_keys)} estudos sem chave BibTeX:")
        for k in missing_keys:
            print(f"  - {k}")

    return "\n".join(lines)


def main() -> None:
    for path, desc in [
        (IC_PATH, "citation_index_results.json"),
        (KEY_MAP_PATH, "bibtex_key_map.json"),
        (BIB_PATH, "references.bib"),
    ]:
        if not path.exists():
            print(f"ERRO: {desc} não encontrado: {path}", file=sys.stderr)
            sys.exit(1)

    ic_data = load_json(IC_PATH)
    key_map = load_json(KEY_MAP_PATH)
    journals = parse_bib_journals(BIB_PATH)

    print(f"Estudos no IC: {len(ic_data)}")
    print(f"Chaves no mapeamento: {len(key_map)}")
    print(f"Periódicos encontrados no .bib: {len(journals)}")

    published_count = sum(1 for e in ic_data if e.get("is_published", False))
    unpublished_count = sum(1 for e in ic_data if not e.get("is_published", True))
    print(f"Estudos publicados: {published_count}")
    print(f"Estudos não publicados: {unpublished_count}")

    table = generate_table(ic_data, key_map, journals)
    OUTPUT_PATH.write_text(table, encoding="utf-8")
    print(f"\nTabela gerada: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
