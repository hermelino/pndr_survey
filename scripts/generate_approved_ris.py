"""Filtra approved_papers.ris para manter apenas estudos aprovados.

Lê o RIS existente, compara com 2-2-papers.json e remove entradas
de estudos rejeitados. Preserva a formatação original do RIS.

Uso: python generate_approved_ris.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

PAPERS_JSON = DATA_DIR / "2-papers" / "2-2-papers.json"
RIS_PATH = DATA_DIR / "2-papers" / "approved_papers.ris"


def get_approved_pdfs() -> set[str]:
    """Retorna set de arquivo_pdf dos estudos aprovados."""
    with open(PAPERS_JSON, "r", encoding="utf-8") as f:
        papers = json.load(f)
    return {p["arquivo_pdf"] for p in papers if p["triagem"] == "APROVADO"}


def parse_ris_entries(ris_path: Path) -> list[dict[str, object]]:
    """Parse RIS em lista de entradas com linhas originais e nome do PDF."""
    entries: list[dict[str, object]] = []
    current_lines: list[str] = []
    current_pdf: str | None = None

    with open(ris_path, "r", encoding="utf-8") as f:
        for line in f:
            stripped = line.rstrip("\n")
            if stripped.startswith("TY  - "):
                current_lines = [stripped]
                current_pdf = None
            elif stripped.startswith("ER  - "):
                current_lines.append(stripped)
                entries.append({"lines": current_lines, "pdf": current_pdf})
                current_lines = []
            elif stripped.strip():
                current_lines.append(stripped)
                if stripped.startswith("N1  - PDF: "):
                    current_pdf = stripped.replace("N1  - PDF: ", "").strip()

    return entries


def main() -> None:
    approved = get_approved_pdfs()
    print(f"Estudos aprovados em 2-2-papers.json: {len(approved)}")

    entries = parse_ris_entries(RIS_PATH)
    print(f"Entradas no RIS atual: {len(entries)}")

    filtered = [e for e in entries if e["pdf"] in approved]
    print(f"Entradas apos filtro: {len(filtered)}")

    # Reportar removidos
    removed = [e for e in entries if e["pdf"] not in approved]
    if removed:
        print(f"\nRemovidos ({len(removed)}):")
        for e in removed:
            print(f"  - {e['pdf']}")

    # Reportar aprovados ausentes do RIS
    ris_pdfs = {e["pdf"] for e in entries if e["pdf"]}
    missing = approved - ris_pdfs
    if missing:
        print(f"\nAprovados ausentes do RIS ({len(missing)}):")
        for pdf in sorted(missing):
            print(f"  - {pdf}")

    # Validar
    if len(filtered) != len(approved):
        print(
            f"\nATENCAO: {len(filtered)} entradas no RIS != "
            f"{len(approved)} aprovados no JSON"
        )
        if missing:
            print("Estudos ausentes precisam ser adicionados manualmente ao RIS.")
            sys.exit(1)

    # Escrever
    with open(RIS_PATH, "w", encoding="utf-8") as f:
        for entry in filtered:
            f.write("\n".join(entry["lines"]))  # type: ignore[arg-type]
            f.write("\n\n")

    print(f"\nRIS atualizado: {RIS_PATH} ({len(filtered)} entradas)")


if __name__ == "__main__":
    main()
