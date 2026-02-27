"""
rename_capes_new.py
Rename 13 newly downloaded CAPES PDFs (10 unique + 3 duplicates).
Update all_papers.xlsx.
"""
import os, sys, io, openpyxl

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = 'C:/OneDrive/github/pndr_survey/data/2-papers'
XLSX = os.path.join(ROOT, 'all_papers.xlsx')

COL_BAIXADO = 3
COL_ARQUIVO = 4

# ── Mapping: old_name -> (new_name, xlsx_row) ───────────────────────────────

RENAMES = {
    'artigoRenPDF525.pdf':
        ('capes-1998-rodrigues-guilhoto.pdf', 3),
    'monicafrigeri,+ferrari.pdf':
        ('capes-2002-ferrari.pdf', 4),
    'baixados.pdf':
        ('capes-2002-viola.pdf', 5),
    'baixados (2).pdf':
        ('capes-2003-arruda.pdf', 6),
    'baixados (1).pdf':
        ('capes-2003-cruz.pdf', 7),
    'baixados (4).pdf':
        ('capes-2007-haddad.pdf', 8),
    "j140v07n03_09 -- 88835e1f801f5df3a713dc908b8d1127 -- Anna's Archive.pdf":
        ('capes-2007-porsse-haddad-ribeiro.pdf', 10),
    'juliaangst,+10804-35488-1-CE.pdf':
        ('capes-2009-nascimento-lima.pdf', 11),
    'baixados (5).pdf':
        ('capes-2009-avellar.pdf', 12),
    'bortolon,+1171-2123-1-CE.pdf':
        ('capes-2011-diniz-corrar.pdf', 13),
}

# Duplicates to delete
DUPLICATES = [
    'baixados (3).pdf',   # same as baixados (2).pdf = Arruda
    'baixados (6).pdf',   # same as baixados (5).pdf = Avellar
    'baixados (7).pdf',   # same as baixados (5).pdf = Avellar
]

# ── Execute renames ──────────────────────────────────────────────────────────

print('Renaming PDFs...')
ok_count = 0
for old_name, (new_name, _row) in RENAMES.items():
    old_path = os.path.join(ROOT, old_name)
    new_path = os.path.join(ROOT, new_name)
    if not os.path.exists(old_path):
        print(f'  SKIP (not found): {old_name}')
        continue
    if os.path.exists(new_path):
        # Replace existing (e.g., capes-2007-porsse-haddad-ribeiro.pdf)
        os.remove(new_path)
        print(f'  REPLACE: {new_name} (existing removed)')
    try:
        os.rename(old_path, new_path)
        ok_count += 1
        print(f'  OK: {old_name} -> {new_name}')
    except Exception as e:
        print(f'  ERROR: {old_name} -> {new_name}: {e}')

print(f'\nRenamed {ok_count} files')

# ── Delete duplicates ────────────────────────────────────────────────────────

print('\nDeleting duplicates...')
for dup in DUPLICATES:
    dup_path = os.path.join(ROOT, dup)
    if os.path.exists(dup_path):
        os.remove(dup_path)
        print(f'  DELETED: {dup}')
    else:
        print(f'  SKIP (not found): {dup}')

# ── Update xlsx ──────────────────────────────────────────────────────────────

print('\nUpdating xlsx...')
wb = openpyxl.load_workbook(XLSX)
ws = wb['Registros']

updated = 0
for old_name, (new_name, row) in RENAMES.items():
    ws.cell(row=row, column=COL_BAIXADO, value='Sim')
    ws.cell(row=row, column=COL_ARQUIVO, value=new_name)
    updated += 1
    print(f'  Row {row}: Baixado->"Sim", PDF="{new_name}"')

wb.save(XLSX)
print(f'\nUpdated {updated} rows in xlsx')

# ── Summary ──────────────────────────────────────────────────────────────────

print('\n=== STILL MISSING CAPES ===')
remaining = []
for row in range(2, ws.max_row + 1):
    base = (ws.cell(row=row, column=1).value or '').strip()
    baixado = (ws.cell(row=row, column=3).value or '').strip()
    if base.lower() == 'capes' and baixado == 'Nao':
        titulo = (ws.cell(row=row, column=6).value or '')[:80]
        ano = ws.cell(row=row, column=8).value or ''
        remaining.append((row, ano, titulo))
        print(f'  Row {row} | {ano} | {titulo}')

print(f'\n{len(remaining)} CAPES records still missing')
print('DONE!')
