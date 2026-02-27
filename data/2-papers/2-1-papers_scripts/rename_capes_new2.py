"""
rename_capes_new2.py
Rename second batch of CAPES PDFs (12 records) and update all_papers.xlsx.
Also clean up re-downloads and duplicates.
"""
import os, sys, io, openpyxl

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = 'C:/OneDrive/github/pndr_survey/data/2-papers'
XLSX = os.path.join(ROOT, 'all_papers.xlsx')

COL_BAIXADO = 3
COL_ARQUIVO = 4

# ── New files to rename ──────────────────────────────────────────────────────

RENAMES = {
    'icsalomao,+9966-30978-1-CE.pdf':
        ('capes-2007-almeida-resende-silva.pdf', 9),
    'monicafrigeri,+Artigo+04.pdf':
        ('capes-2012-benavente-crespi-maffioli.pdf', 14),
    'monicafrigeri,+Artigo+03.pdf':
        ('capes-2013-vieira.pdf', 15),
    'pri2602,+08_OK_A+Lei+de+Incentivo+Fiscal+no+BRASIL.pdf':
        ('capes-2015-matias-athayde-hungaro.pdf', 16),
    '3903-18934-2-PB.pdf':
        ('capes-2016-matsumoto-bittencourt-silva.pdf', 18),
    'moalves,+12.artigo.pdf':
        ('capes-2017-soares-sousa-neto.pdf', 21),
    'andrea_hespanha,+e64s_jmphc.v11iSup.851_e64s.pdf':
        ('capes-2019-banna-gondinho.pdf', 22),
    '31498-Texto del artículo-50453-2-10-20200326.pdf':
        ('capes-2019-yaguache-sandoval-inga.pdf', 23),
    '1-s2.0-S175778022300077X-main.pdf':
        ('capes-2020-psycharis-iliopoulou-zoi.pdf', 24),
    '11879-Texto do artigo-62153-1-10-20220322.pdf':
        ('capes-2022-matias-elicker-pereira.pdf', 25),
}

# ── Files where target already exists (just update xlsx, delete new) ─────────

ALREADY_EXIST = {
    'revistas,+v19+n3+553-562.pdf':
        ('capes-2015-araujo-santos-rebello.pdf', 17),
    'art12.pdf':
        ('capes-2017-macedo-pires-sampaio.pdf', 20),
}

# ── Duplicates and re-downloads to delete ────────────────────────────────────

DUPLICATES = [
    'monicafrigeri,+Artigo+03 (1).pdf',   # duplicate of Artigo+03 (Vieira Filho)
    'rbeur_202515_7775pt.pdf',              # duplicate of scielo-2025-quaglio-lopes-heck.pdf
    'artigoRenPDF525.pdf',                  # re-download (already capes-1998-rodrigues-guilhoto.pdf)
    'monicafrigeri,+ferrari.pdf',           # re-download (already capes-2002-ferrari.pdf)
]

# ── Execute renames ──────────────────────────────────────────────────────────

print('=== Renaming new PDFs ===')
ok_count = 0
for old_name, (new_name, _) in RENAMES.items():
    old_path = os.path.join(ROOT, old_name)
    new_path = os.path.join(ROOT, new_name)
    if not os.path.exists(old_path):
        print(f'  SKIP (not found): {old_name}')
        continue
    if os.path.exists(new_path):
        os.remove(new_path)
        print(f'  REPLACE existing: {new_name}')
    try:
        os.rename(old_path, new_path)
        ok_count += 1
        print(f'  OK: {old_name} -> {new_name}')
    except Exception as e:
        print(f'  ERROR: {e}')
print(f'Renamed {ok_count} files')

# ── Handle already-existing targets ──────────────────────────────────────────

print('\n=== Already existing (delete new, keep old) ===')
for old_name, (existing_name, _) in ALREADY_EXIST.items():
    old_path = os.path.join(ROOT, old_name)
    if os.path.exists(old_path):
        os.remove(old_path)
        print(f'  DELETED new: {old_name} (keeping {existing_name})')
    else:
        print(f'  SKIP (not found): {old_name}')

# ── Delete duplicates ────────────────────────────────────────────────────────

print('\n=== Deleting duplicates/re-downloads ===')
for dup in DUPLICATES:
    dup_path = os.path.join(ROOT, dup)
    if os.path.exists(dup_path):
        os.remove(dup_path)
        print(f'  DELETED: {dup}')
    else:
        print(f'  SKIP (not found): {dup}')

# ── Update xlsx ──────────────────────────────────────────────────────────────

print('\n=== Updating xlsx ===')
wb = openpyxl.load_workbook(XLSX)
ws = wb['Registros']

updated = 0
all_updates = {**RENAMES, **ALREADY_EXIST}
for old_name, (new_name, row) in all_updates.items():
    ws.cell(row=row, column=COL_BAIXADO, value='Sim')
    ws.cell(row=row, column=COL_ARQUIVO, value=new_name)
    updated += 1
    print(f'  Row {row}: Baixado->"Sim", PDF="{new_name}"')

wb.save(XLSX)
print(f'\nUpdated {updated} rows in xlsx')

# ── Summary ──────────────────────────────────────────────────────────────────

print('\n=== REMAINING MISSING ===')
remaining = []
for row in range(2, ws.max_row + 1):
    base = (ws.cell(row=row, column=1).value or '').strip()
    baixado = (ws.cell(row=row, column=3).value or '').strip()
    if baixado == 'Nao':
        titulo = (ws.cell(row=row, column=6).value or '')[:80]
        ano = ws.cell(row=row, column=8).value or ''
        remaining.append((row, base, ano, titulo))
        print(f'  [{base}] Row {row} | {ano} | {titulo}')

print(f'\n{len(remaining)} records still missing')
print('DONE!')
