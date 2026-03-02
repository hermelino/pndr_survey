"""Gera tabela LaTeX do índice de citação cruzada (IC) para estudos não publicados.

Lê citation_index_results.json e bibtex_key_map.json para produzir
latex/tabela_ic.tex com \citeonline{} na coluna Estudo.

Uso: python generate_ic_table.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
IC_PATH = BASE_DIR / "data" / "3-ref-bib" / "citation_index_results.json"
KEY_MAP_PATH = BASE_DIR / "latex" / "bibtex_key_map.json"
OUTPUT_PATH = BASE_DIR / "latex" / "tabela_ic.tex"


def load_json(path: Path) -> list | dict:
    """Carrega arquivo JSON."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def format_ic(value: float, n_after: int) -> str:
    """Formata IC para LaTeX: valor com vírgula decimal ou --- se N=0."""
    if n_after == 0:
        return "--"
    if value == 0:
        return "0{,}00"
    formatted = f"{value:.2f}".replace(".", "{,}")
    return formatted


def get_max_published_ic(ic_data: list[dict], key_map: dict[str, str]) -> tuple[str, float] | None:
    """Retorna (citeonline, IC) do estudo publicado com maior IC, ou None."""
    published = [
        e for e in ic_data
        if e.get("is_published") and e.get("n_published_after", 0) > 0
    ]
    if not published:
        return None
    best = max(published, key=lambda x: x.get("IC_published", 0))
    bib_key = key_map.get(best["key"], best["key"])
    return bib_key, best["IC_published"]


def generate_table(ic_data: list[dict], key_map: dict[str, str]) -> str:
    """Gera string LaTeX da tabela IC para estudos não publicados."""
    # Filtrar apenas não publicados
    unpublished = [e for e in ic_data if not e.get("is_published", True)]

    # Ordenar: IC descendente, depois por chave
    unpublished.sort(
        key=lambda x: (-x.get("IC_published", 0), x.get("key", ""))
    )

    lines = [
        r"\begin{table}[htb]",
        r"\centering",
        r"\small",
        r"\caption{Índice de Citação Cruzada (IC) dos artigos não publicados}",
        r"\label{tab:ic-nao-publicados}",
        r"\begin{tabular}{lr}",
        r"\toprule",
        r"Artigo & IC \\",
        r"\midrule",
    ]

    missing_keys: list[str] = []

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

        lines.append(f"{estudo} & {ic_str} \\\\")

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
    for path, desc in [(IC_PATH, "citation_index_results.json"), (KEY_MAP_PATH, "bibtex_key_map.json")]:
        if not path.exists():
            print(f"ERRO: {desc} não encontrado: {path}", file=sys.stderr)
            sys.exit(1)

    ic_data = load_json(IC_PATH)
    key_map = load_json(KEY_MAP_PATH)

    print(f"Estudos no IC: {len(ic_data)}")
    print(f"Chaves no mapeamento: {len(key_map)}")

    unpublished_count = sum(1 for e in ic_data if not e.get("is_published", True))
    print(f"Estudos não publicados: {unpublished_count}")

    table = generate_table(ic_data, key_map)
    OUTPUT_PATH.write_text(table, encoding="utf-8")
    print(f"\nTabela gerada: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
