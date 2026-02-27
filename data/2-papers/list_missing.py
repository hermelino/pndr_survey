#!/usr/bin/env python3
"""List papers not yet downloaded (Baixado != 'Sim'), grouped by Base."""

import openpyxl
import subprocess
import sys
from collections import OrderedDict
from pathlib import Path

XLSX = Path(r"c:\OneDrive\github\pndr_survey\data\2-papers\all_papers.xlsx")
SHEET = "Registros"

# Desired base ordering (canonical display names)
BASE_ORDER = ["Scopus", "SciELO", "CAPES", "EconPapers", "ANPEC"]

# Map lowercase -> canonical name for case-insensitive grouping
BASE_MAP = {b.lower(): b for b in BASE_ORDER}


def truncate(text, maxlen):
    if not text:
        return ""
    s = str(text).strip()
    return s[:maxlen] + "..." if len(s) > maxlen else s


def safe_copy(src: Path, dst: Path):
    """Copy a file that may be locked by another process (e.g. Excel on Windows)."""
    try:
        dst.write_bytes(src.read_bytes())
    except PermissionError:
        if sys.platform == "win32":
            subprocess.run(
                ["powershell", "-Command",
                 f"Copy-Item '{src}' '{dst}' -Force"],
                check=True,
            )
        else:
            raise


def main():
    # Copy to temp file to avoid PermissionError when Excel has the file open
    tmp = XLSX.with_name("_tmp_all_papers.xlsx")
    safe_copy(XLSX, tmp)

    try:
        wb = openpyxl.load_workbook(str(tmp), read_only=True, data_only=True)
    except Exception:
        tmp.unlink(missing_ok=True)
        raise

    ws = wb[SHEET]

    # Collect missing records grouped by base (canonical name)
    groups: dict[str, list] = OrderedDict((b, []) for b in BASE_ORDER)

    for row_idx, row in enumerate(ws.iter_rows(min_row=2, values_only=False), start=2):
        # Columns: A=0 Base, B=1 URL, C=2 Baixado, D=3 Arquivo PDF,
        #          E=4 ID, F=5 Titulo, G=6 Autores, H=7 Ano,
        #          I=8 Periodico, J=9 DOI, K=10 Resumo, L=11 Tipo,
        #          M=12 Palavras-chave, N=13 Obs
        vals = [c.value for c in row]
        if len(vals) < 10:
            continue

        base_raw = str(vals[0] or "").strip()
        url = str(vals[1] or "").strip()
        baixado = str(vals[2] or "").strip()
        titulo = vals[5]
        autores = vals[6]
        ano = vals[7]
        doi_raw = str(vals[9] or "").strip()

        if baixado == "Sim":
            continue

        # Resolve canonical base name (case-insensitive)
        base = BASE_MAP.get(base_raw.lower(), base_raw)

        doi_url = f"https://doi.org/{doi_raw}" if doi_raw else ""

        record = {
            "row": row_idx,
            "base": base,
            "ano": ano if ano else "",
            "autores": truncate(autores, 50),
            "titulo": truncate(titulo, 80),
            "url": url,
            "doi_url": doi_url,
        }

        if base in groups:
            groups[base].append(record)
        else:
            groups[base] = [record]

    wb.close()
    tmp.unlink(missing_ok=True)

    # Print
    total = 0
    for base, records in groups.items():
        if not records:
            continue
        count = len(records)
        total += count
        print(f"\n{'=' * 90}")
        print(f"  {base}  ({count} missing)")
        print(f"{'=' * 90}")
        for r in records:
            print(f"\n  Row {r['row']}  |  {r['ano']}  |  {r['autores']}")
            print(f"  {r['titulo']}")
            if r["url"]:
                print(f"  URL: {r['url']}")
            if r["doi_url"]:
                print(f"  DOI: {r['doi_url']}")

    # Summary
    print(f"\n{'=' * 90}")
    print(f"  SUMMARY -- Missing papers by base")
    print(f"{'=' * 90}")
    for base, records in groups.items():
        if records:
            print(f"  {base:<15} {len(records):>4}")
    print(f"  {'TOTAL':<15} {total:>4}")
    print()


if __name__ == "__main__":
    main()
