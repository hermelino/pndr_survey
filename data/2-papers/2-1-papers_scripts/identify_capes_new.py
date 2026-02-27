"""
identify_capes_new.py
Reads the first page of each newly downloaded CAPES PDF and prints
filename, file size, page count, and the first ~600 characters of text.
"""

import os
import pdfplumber

FOLDER = os.path.dirname(os.path.abspath(__file__))

FILES = [
    "artigoRenPDF525.pdf",
    "monicafrigeri,+ferrari.pdf",
    "baixados.pdf",
    "baixados (1).pdf",
    "baixados (2).pdf",
    "baixados (3).pdf",
    "baixados (4).pdf",
    "baixados (5).pdf",
    "baixados (6).pdf",
    "baixados (7).pdf",
    "juliaangst,+10804-35488-1-CE.pdf",
    "bortolon,+1171-2123-1-CE.pdf",
]

SEP = "=" * 80

for i, fname in enumerate(FILES, start=1):
    path = os.path.join(FOLDER, fname)
    print(f"\n{SEP}")
    print(f"  [{i:02d}/12]  {fname}")
    print(SEP)

    if not os.path.isfile(path):
        print("  *** FILE NOT FOUND ***")
        continue

    size_bytes = os.path.getsize(path)
    size_kb = size_bytes / 1024

    try:
        with pdfplumber.open(path) as pdf:
            n_pages = len(pdf.pages)
            first_page = pdf.pages[0]
            text = first_page.extract_text() or ""
    except Exception as exc:
        print(f"  File size : {size_kb:,.1f} KB")
        print(f"  ERROR reading PDF: {exc}")
        continue

    print(f"  File size : {size_kb:,.1f} KB")
    print(f"  Pages     : {n_pages}")
    print(f"  --- First 600 chars of page 1 ---")
    snippet = text[:600]
    print(snippet if snippet else "  (no text extracted)")
    print(f"  --- end snippet ({len(text)} total chars on page 1) ---")

print(f"\n{SEP}")
print("Done.")
