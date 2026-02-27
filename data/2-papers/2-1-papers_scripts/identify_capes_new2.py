#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
identify_capes_new2.py
Reads the first page of each newly downloaded PDF and prints identification info:
filename, file size, number of pages, and first ~500 characters of page-1 text.
"""

import os
import pdfplumber

FOLDER = os.path.dirname(os.path.abspath(__file__))

FILES = [
    "icsalomao,+9966-30978-1-CE.pdf",
    "monicafrigeri,+Artigo+04.pdf",
    "monicafrigeri,+Artigo+03.pdf",
    "11879-Texto do artigo-62153-1-10-20220322.pdf",
    "1-s2.0-S175778022300077X-main.pdf",
    "31498-Texto del artículo-50453-2-10-20200326.pdf",
    "andrea_hespanha,+e64s_jmphc.v11iSup.851_e64s.pdf",
    "moalves,+12.artigo.pdf",
    "art12.pdf",
    "3903-18934-2-PB.pdf",
    "revistas,+v19+n3+553-562.pdf",
    "pri2602,+08_OK_A+Lei+de+Incentivo+Fiscal+no+BRASIL.pdf",
    "monicafrigeri,+Artigo+03 (1).pdf",
    "rbeur_202515_7775pt.pdf",
    "artigoRenPDF525.pdf",
    "monicafrigeri,+ferrari.pdf",
]

SEPARATOR = "=" * 80

for i, fname in enumerate(FILES, start=1):
    path = os.path.join(FOLDER, fname)
    print(f"\n{SEPARATOR}")
    print(f"[{i:02d}] {fname}")

    if not os.path.isfile(path):
        print("     *** FILE NOT FOUND ***")
        continue

    size_bytes = os.path.getsize(path)
    if size_bytes < 1024:
        size_str = f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        size_str = f"{size_bytes / 1024:.1f} KB"
    else:
        size_str = f"{size_bytes / (1024 * 1024):.2f} MB"

    try:
        with pdfplumber.open(path) as pdf:
            n_pages = len(pdf.pages)
            page1_text = pdf.pages[0].extract_text() or ""
    except Exception as exc:
        print(f"     Size: {size_str}")
        print(f"     *** ERROR reading PDF: {exc} ***")
        continue

    snippet = page1_text[:500].strip()

    print(f"     Size: {size_str}  |  Pages: {n_pages}")
    print(f"     --- First 500 chars of page 1 ---")
    print(snippet)

print(f"\n{SEPARATOR}")
print("Done.")
