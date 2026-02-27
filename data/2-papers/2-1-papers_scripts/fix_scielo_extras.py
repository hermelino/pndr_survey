"""
fix_scielo_extras.py
The 2 "extra" PDFs are actually the SciELO records (rows 13 and 14).
Rename them to follow the scielo- convention and update xlsx.
"""
import os, sys, io, openpyxl

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = 'C:/OneDrive/github/pndr_survey/data/2-papers'
XLSX = os.path.join(ROOT, 'all_papers.xlsx')

COL_BAIXADO = 3
COL_ARQUIVO = 4

RENAMES = {
    'extra-2022-gumiero-rbeur.pdf':        ('scielo-2022-gumiero.pdf',              13),
    'extra-2025-quaglio-lopes-heck.pdf':   ('scielo-2025-quaglio-lopes-heck.pdf',   14),
}

print('Renaming...')
for old_name, (new_name, _) in RENAMES.items():
    old_path = os.path.join(ROOT, old_name)
    new_path = os.path.join(ROOT, new_name)
    if not os.path.exists(old_path):
        print(f'  SKIP: {old_name}')
        continue
    if os.path.exists(new_path):
        print(f'  CONFLICT: {new_name}')
        continue
    os.rename(old_path, new_path)
    print(f'  OK: {old_name} -> {new_name}')

print('\nUpdating xlsx...')
wb = openpyxl.load_workbook(XLSX)
ws = wb['Registros']
for old_name, (new_name, row) in RENAMES.items():
    ws.cell(row=row, column=COL_BAIXADO, value='Sim')
    ws.cell(row=row, column=COL_ARQUIVO, value=new_name)
    print(f'  Row {row}: Baixado->"Sim", PDF="{new_name}"')
wb.save(XLSX)
print('DONE!')
