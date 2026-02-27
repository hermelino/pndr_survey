"""
rename_scopus_final.py
Rename the last 3 missing Scopus PDFs and update all_papers.xlsx.
"""
import os, sys, io, openpyxl

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = 'C:/OneDrive/github/pndr_survey/data/2-papers'
XLSX = os.path.join(ROOT, 'all_papers.xlsx')

# Column indices (1-based): A=Base, B=URL, C=Baixado, D=Arquivo PDF
COL_BAIXADO = 3
COL_ARQUIVO = 4

RENAMES = {
    # Row 4: Abreu et al. 2012 - Heifer retention in Pantanal
    'baixados.pdf':                                          ('scopus-2012-abreu-gomes-mello.pdf',    4),
    # Row 10: Filho et al. 2024 - FNO evaluation in Pará (RBGDR)
    'Artigo+06+-+RBGDR+-+1+Edição+2024+-+Português.pdf':    ('scopus-2024-filho-moreira-silva.pdf', 10),
}

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
        print(f'  CONFLICT: {new_name} already exists!')
        continue
    try:
        os.rename(old_path, new_path)
        ok_count += 1
        print(f'  OK: {old_name} -> {new_name}')
    except Exception as e:
        print(f'  ERROR: {old_name} -> {new_name}: {e}')

print(f'\nRenamed {ok_count} files')

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

# ── Check remaining ──────────────────────────────────────────────────────────

print('\n=== STILL MISSING ===')
print('  Row 9: Costa et al. 2024 - SUDENE tax incentives')
print('         DOI: 10.1080/13504851.2024.2402927')

print('\nDONE!')
