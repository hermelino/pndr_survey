"""Gera tabela LaTeX do índice de citação cruzada (IC).

Lê citation_index_results.json, bibtex_key_map.json e references.bib
para produzir latex/tabela_ic.tex com estudos publicados e não publicados
em formato paisagem com painéis lado a lado.

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

# Correções de nomes de periódicos (bib → exibição)
JOURNAL_CORRECTIONS: dict[str, str] = {
    "Estudos Economicos": "Estudos Econômicos",
    "CEPAL REVIEW": "CEPAL Review",
}

# Abreviações para periódicos que não cabem em uma linha
JOURNAL_ABBREVIATIONS: dict[str, str] = {
    "Revista Brasileira de Estudos Regionais e Urbanos": "Rev. Bras. Est. Reg. Urbanos",
    "Revista Brasileira de Gestão e Desenvolvimento Regional": "Rev. Bras. Gest. Desenv. Reg.",
    "Revista Brasileira de Gestao e Desenvolvimento Regional": "Rev. Bras. Gest. Desenv. Reg.",
}


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


def normalize_journal(name: str) -> str:
    """Aplica correções e abreviações ao nome do periódico."""
    name = JOURNAL_CORRECTIONS.get(name, name)
    name = JOURNAL_ABBREVIATIONS.get(name, name)
    return name


def format_ic(value: float, n_after: int) -> str:
    """Formata IC para LaTeX: valor com vírgula decimal ou -- se N=0."""
    if n_after == 0:
        return r"\textbf{--}"
    if value == 0:
        return "0{,}00"
    return f"{value:.2f}".replace(".", "{,}")


def generate_table(
    ic_data: list[dict],
    key_map: dict[str, str],
    journals: dict[str, str],
) -> str:
    """Gera string LaTeX da tabela IC em paisagem com painéis lado a lado."""
    published = [e for e in ic_data if e.get("is_published", False)]
    unpublished = [e for e in ic_data if not e.get("is_published", True)]

    # Ordenar publicados: IC não calculável (N=0) por último, depois IC desc
    published.sort(key=lambda x: (
        x.get("n_published_after", 0) == 0,
        -x.get("IC_published", 0),
        x.get("key", ""),
    ))
    unpublished.sort(key=lambda x: (-x.get("IC_published", 0), x.get("key", "")))

    missing_keys: list[str] = []

    # --- Construir linhas dos publicados ---
    pub_rows: list[tuple[str, str, str]] = []
    for entry in published:
        pdf_key = entry["key"]
        bib_key = key_map.get(pdf_key)

        if bib_key:
            estudo = rf"\citeonline{{{bib_key}}}"
            journal = normalize_journal(journals.get(bib_key, ""))
        else:
            missing_keys.append(pdf_key)
            estudo = pdf_key
            journal = ""

        n_after = entry.get("n_published_after", 0)
        ic_val = entry.get("IC_published", 0)
        ic_str = format_ic(ic_val, n_after)

        pub_rows.append((estudo, journal, ic_str))

    # --- Construir linhas dos não publicados ---
    unpub_rows: list[tuple[str, str]] = []
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

        unpub_rows.append((estudo, ic_str))

    # --- Montar tabela paisagem com painéis lado a lado ---
    max_rows = max(len(pub_rows), len(unpub_rows))

    lines = [
        r"\afterpage{\clearpage%",
        r"\begin{landscape}%",
        r"\begin{table}[htbp]",
        r"\centering",
        r"\caption{Resultados do Índice de Citação Cruzada (IC)}",
        r"\label{tab:ic-resultados}",
        r"\footnotesize",
        r"\renewcommand{\arraystretch}{1.2}",
        r"\begin{tabular}{llr@{\hskip 1em}lr}",
        r"\toprule",
        r"\multicolumn{3}{l}{Estudos publicados em periódicos}"
        r" & \multicolumn{2}{l}{Estudos não publicados} \\",
        r"\cmidrule(lr){1-3} \cmidrule(lr){4-5}",
        r"Estudo & Periódico & IC & Estudo & IC \\",
        r"\midrule",
    ]

    for i in range(max_rows):
        if i < len(pub_rows):
            left = f"{pub_rows[i][0]} & {pub_rows[i][1]} & {pub_rows[i][2]}"
        else:
            left = " & & "

        if i < len(unpub_rows):
            right = f"{unpub_rows[i][0]} & {unpub_rows[i][1]}"
        else:
            right = " & "

        lines.append(f"{left} & {right} \\\\")

    lines.extend([
        r"\bottomrule",
        r"\multicolumn{5}{l}{\footnotesize Nota: ``--'' = IC não"
        r" calculável ($N=0$). Fonte: Elaborada pelos autores.} \\",
        r"\end{tabular}",
        r"\end{table}",
        r"\end{landscape}}",
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
