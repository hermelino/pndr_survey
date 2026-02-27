"""
rename_scopus_new.py
Rename newly downloaded Scopus PDFs and update all_papers.xlsx.
Also handles 2 extra PDFs (not in Scopus records) that were downloaded.
"""
import os, sys, io, openpyxl

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = 'C:/OneDrive/github/pndr_survey/data/2-papers'
XLSX = os.path.join(ROOT, 'all_papers.xlsx')

# ── Mapping: original filename -> (new_name, xlsx_row or None) ──────────────

RENAMES = {
    # 8 matched Scopus records
    '1-s2.0-0305750X91901355-main.pdf':                        ('scopus-1991-binswanger.pdf',           2),
    'baixados (3).pdf':                                         ('scopus-2009-silva-resende-neto.pdf',   3),
    '1-s2.0-S1877050915027416-main.pdf':                        ('scopus-2015-junkes-tereso-afonso.pdf', 5),
    'baixados.pdf':                                             ('scopus-2018-oliveira-terra-resende.pdf', 6),
    'rafaelfaber,+05_1850-PT.pdf':                              ('scopus-2021-cavalcante.pdf',           7),
    'Artigo+1.pdf':                                             ('scopus-2024-cunha-soares.pdf',         8),
    '5-strr.pdf':                                               ('scopus-2025-borges-rodrigues.pdf',    11),
    'Artigo+19+-+RBGDR+-+2+Edição+2025+-+Português.pdf':       ('scopus-2025-gumiero.pdf',             12),
    # 2 extra PDFs (not in Scopus records, keep with scopus-extra prefix)
    'baixados (1).pdf':                                         ('extra-2022-gumiero-rbeur.pdf',        None),
    'baixados (2).pdf':                                         ('extra-2025-quaglio-lopes-heck.pdf',   None),
}

# Column indices in all_papers.xlsx (1-based):
# A=Base, B=URL, C=Baixado, D=Arquivo PDF
COL_BAIXADO = 3
COL_ARQUIVO = 4

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
    if row is None:
        continue  # Extra PDFs don't have a row in the xlsx
    # Update Baixado and Arquivo PDF columns
    current_baixado = ws.cell(row=row, column=COL_BAIXADO).value
    ws.cell(row=row, column=COL_BAIXADO, value='Sim')
    ws.cell(row=row, column=COL_ARQUIVO, value=new_name)
    updated += 1
    print(f'  Row {row}: Baixado={current_baixado}->"Sim", PDF="{new_name}"')

wb.save(XLSX)
print(f'\nUpdated {updated} rows in xlsx')

# ── Summary ──────────────────────────────────────────────────────────────────

print('\n=== STILL MISSING (no PDF downloaded) ===')
print('  Row 4: Abreu et al. 2012 - Heifer retention in Pantanal')
print('         DOI: 10.1590/S1516_35982012000800019')
print('  Row 9: Costa et al. 2024 - SUDENE tax incentives')
print('         DOI: 10.1080/13504851.2024.2402927')
print('  Row 10: Filho et al. 2024 - FNO evaluation in Para')
print('          DOI: 10.54399/rbgdr.v20i1.6406')

print('\nDONE!')
