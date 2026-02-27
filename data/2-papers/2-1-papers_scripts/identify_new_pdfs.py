"""
identify_new_pdfs.py
Reads the first page of each newly downloaded PDF and prints the first ~500
characters of extracted text for identification purposes.
"""

import os
import pdfplumber

FOLDER = os.path.dirname(os.path.abspath(__file__))

FILES = [
    "1-s2.0-0305750X91901355-main.pdf",
    "1-s2.0-S1877050915027416-main.pdf",
    "baixados.pdf",
    "baixados (1).pdf",
    "baixados (2).pdf",
    "baixados (3).pdf",
    "5-strr.pdf",
    "Artigo+1.pdf",
    "Artigo+19+-+RBGDR+-+2+Edição+2025+-+Português.pdf",
    "rafaelfaber,+05_1850-PT.pdf",
]

SEP = "=" * 80

for i, fname in enumerate(FILES, start=1):
    path = os.path.join(FOLDER, fname)
    print(SEP)
    print(f"[{i}/10]  {fname}")

    if not os.path.isfile(path):
        print("  ** FILE NOT FOUND **")
        print()
        continue

    size = os.path.getsize(path)
    print(f"  Size: {size:,} bytes")

    try:
        with pdfplumber.open(path) as pdf:
            page = pdf.pages[0]
            text = page.extract_text() or ""
            snippet = text[:500]
            print(f"  Pages in PDF: {len(pdf.pages)}")
            print(f"  --- First 500 chars of page 1 ---")
            print(snippet)
    except Exception as exc:
        print(f"  ** ERROR reading PDF: {exc}")

    print()

print(SEP)
print("Done.")
