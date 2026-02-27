"""
Final pass: manual corrections for PDF names where automatic extraction failed.
Based on reading first pages of each PDF.
"""
import os, openpyxl

ROOT = 'C:/OneDrive/github/pndr_survey/data/2-papers'
XLSX = os.path.join(ROOT, 'all_records.xlsx')

# Manual corrections: current_name -> correct_name
CORRECTIONS = {
    # ── ANPEC: fix bad/missing authors ──
    'anpec-1993-simoes-amaral-kingdom.pdf':  'anpec-nd-simoes-amaral.pdf',
    # anpec-2003.pdf: no visible author → keep
    'anpec-2005-jr-crocco.pdf':              'anpec-2005-jayme-crocco.pdf',
    'anpec-2005.pdf':                        'anpec-2005-araujo-neto.pdf',
    'anpec-2005b.pdf':                       'anpec-2005-oliveira-domingues.pdf',
    'anpec-2006.pdf':                        'anpec-2006-guanziroli.pdf',
    'anpec-2006b.pdf':                       'anpec-2006-silva-resende-neto.pdf',
    'anpec-2007.pdf':                        'anpec-2007-stallivieri-britto.pdf',
    'anpec-2008.pdf':                        'anpec-2008-programa.pdf',
    # anpec-2010.pdf: no visible author → keep
    'anpec-2010b.pdf':                       'anpec-2010-correa-paula-oreiro.pdf',
    'anpec-2013.pdf':                        'anpec-2013-programa.pdf',
    'anpec-2013b.pdf':                       'anpec-2013-artigos.pdf',
    'anpec-2015.pdf':                        'anpec-2015-artigos.pdf',
    'anpec-2015b.pdf':                       'anpec-2015-programa.pdf',
    'anpec-2015c.pdf':                       'anpec-2015-oliveira-terra-resende.pdf',
    'anpec-2017-eusebio-maia-silveira.pdf':  'anpec-2017-eusebio-maia.pdf',
    'anpec-2017.pdf':                        'anpec-2017-nascimento-haddad.pdf',
    'anpec-2019.pdf':                        'anpec-2019-programa.pdf',
    'anpec-2020-rauldamotasilveiraneto.pdf': 'anpec-2020-oliveira-neto.pdf',
    'anpec-2020.pdf':                        'anpec-2020-silva-marcelino-parre.pdf',
    'anpec-2021-brasil-ramos.pdf':           'anpec-2021-bezerra-ramos.pdf',
    'anpec-2021-modais-okumura.pdf':         'anpec-2021-okumura.pdf',
    'anpec-2021-rauldamotasilveiraneto.pdf': 'anpec-2021-oliveira-neto.pdf',
    'anpec-2022-ufrn-br.pdf':               'anpec-2022-bastos-manso-finatti.pdf',
    'anpec-2023-ufc-ufc-ufc.pdf':           'anpec-2023-carneiro-costa-irffi.pdf',
    'anpec-2023.pdf':                        'anpec-2023-magalhaes-souza-domingues.pdf',
    'anpec-2023b.pdf':                       'anpec-2023-araujo-souza.pdf',
    'anpec-2023c.pdf':                       'anpec-2023-programa.pdf',
    'anpec-2023d.pdf':                       'anpec-2023-braz-irffi.pdf',
    'anpec-2023e.pdf':                       'anpec-2023-shirasu.pdf',
    'anpec-2023f.pdf':                       'anpec-2023-marin-griebeler.pdf',
    'anpec-2024-as-academicas.pdf':          'anpec-2024-encontro-regional.pdf',
    'anpec-2024-pernambuco.pdf':             'anpec-2024-calife-neto.pdf',
    'anpec-2024-prodepe.pdf':                'anpec-2024-alves-neto-oliveira.pdf',
    'anpec-2024-ufc-ufc-ufc.pdf':           'anpec-2024-veloso-costa-carneiro.pdf',
    'anpec-2024.pdf':                        'anpec-2024-quaglio.pdf',
    'anpec-2024b.pdf':                       'anpec-2024-programa.pdf',
    'anpec-2024c.pdf':                       'anpec-2024-silva-castro.pdf',
    'anpec-2024d.pdf':                       'anpec-2024-filho-alves.pdf',
    'anpec-2024e.pdf':                       'anpec-2024-lazaretti-davanzo-valente.pdf',
    'anpec-2024f.pdf':                       'anpec-2024-braz-bastos-irffi.pdf',
    'anpec-2025.pdf':                        'anpec-2025-shirasu.pdf',
    'anpec-2025b.pdf':                       'anpec-2025-veloso.pdf',
    'anpec-2025c.pdf':                       'anpec-2025-gondim.pdf',
    'anpec-2025d.pdf':                       'anpec-2025-silva-chagas.pdf',
    'anpec-2025e.pdf':                       'anpec-2025-vazio.pdf',
    'anpec-2025f.pdf':                       'anpec-2025-premio.pdf',
    'anpec-2025g.pdf':                       'anpec-2025-silva-chagas-azzoni.pdf',
    'anpec-2025h.pdf':                       'anpec-2025-programa.pdf',
    'anpec-2025i.pdf':                       'anpec-2025-souza-irffi-carneiro.pdf',
    'anpec-2025j.pdf':                       'anpec-2025-lazaretti-davanzo-neves.pdf',
    'anpec-nd-pelo-axima-industrial.pdf':    'anpec-nd-silva-oliveira.pdf',

    # ── CAPES: fix bad names and add authors ──
    'capes-1991-tras-seto.pdf':                       'capes-1991.pdf',
    'capes-1991.pdf':                                 'capes-1991-binswanger.pdf',
    'capes-2015-doi-issn.pdf':                        'capes-2015-araujo-santos-rebello.pdf',
    'capes-2024-intensidade-fundo-financiamento.pdf': 'capes-2024-cunha-soares.pdf',
    'capes-nd-capitalismo-no-sudam.pdf':              'capes-nd-cavalcante.pdf',
    'capes-nd-financiamento-financi.pdf':             'capes-nd-almeida-resende-silva.pdf',
    'capes-nd-financiados.pdf':                       'capes-nd-soares.pdf',
    'capes-2000-fco.pdf':                             'capes-2009-silva-resende-neto.pdf',
    'capes-2000-fcob.pdf':                            'capes-2009-silva-resende-netob.pdf',
    'capes-2017.pdf':                                 'capes-2017-garsous-corderi-velasco.pdf',
    'capes-2017b.pdf':                                'capes-2017-macedo-pires-sampaio.pdf',
    'capes-2007.pdf':                                 'capes-2007-porsse-haddad-ribeiro.pdf',
    'capes-2010.pdf':                                 'capes-2024-rbgdr.pdf',
    'capes-ndb.pdf':                                  'capes-2025-rbgdr.pdf',
    'capes-nd.pdf':                                   'capes-2025-borges.pdf',
    'capes-2004.pdf':                                 'capes-2018-oliveira-menezes-resende.pdf',
    'capes-2026.pdf':                                 'capes-2026-gondim-carneiro-souza.pdf',
    'capes-2026b.pdf':                                'capes-2026-gondim-carneiro-souzab.pdf',
    'capes-2026c.pdf':                                'capes-2026-gondim-carneiro-souzac.pdf',
    'capes-2015-study.pdf':                           'capes-2015-sciencedirect.pdf',

    # ── EconPapers: fix remaining ──
    'econpapers-nd.pdf':                              'econpapers-nd-haddad.pdf',
    'econpapers-ndb.pdf':                             'econpapers-2014-resende-cravo-pires.pdf',
    'econpapers-2004.pdf':                            'econpapers-2018-oliveira-menezes-resende.pdf',
    'econpapers-2016.pdf':                            'econpapers-2016-garsous-corderi-velasco.pdf',
}

# ── Execute renames ────────────────────────────────────────────────────

# Handle ordering: rename files that would conflict (e.g. capes-1991.pdf -> ... but
# capes-1991-tras-seto.pdf also wants to become capes-1991.pdf)
# Solution: two-phase rename through temp names

phase1 = {}  # old_name -> temp_name
phase2 = {}  # temp_name -> new_name

for old_name, new_name in CORRECTIONS.items():
    if old_name == new_name:
        continue
    old_path = os.path.join(ROOT, old_name)
    if not os.path.exists(old_path):
        print(f'  SKIP (not found): {old_name}')
        continue
    temp_name = f'_tmp_{hash(old_name) & 0xFFFFFF:06x}.pdf'
    phase1[old_name] = temp_name
    phase2[temp_name] = new_name

print('Phase 1: rename to temp...')
for old_name, temp_name in phase1.items():
    try:
        os.rename(os.path.join(ROOT, old_name), os.path.join(ROOT, temp_name))
    except Exception as e:
        print(f'  ERROR: {old_name} -> {temp_name}: {e}')

print('Phase 2: rename to final...')
ok_count = 0
for temp_name, new_name in phase2.items():
    new_path = os.path.join(ROOT, new_name)
    if os.path.exists(new_path):
        print(f'  CONFLICT: {new_name} already exists!')
        # Rename back
        old_name = [k for k, v in phase1.items() if v == temp_name][0]
        os.rename(os.path.join(ROOT, temp_name), os.path.join(ROOT, old_name))
        continue
    try:
        os.rename(os.path.join(ROOT, temp_name), new_path)
        ok_count += 1
        print(f'  OK: {new_name}')
    except Exception as e:
        print(f'  ERROR: {temp_name} -> {new_name}: {e}')

print(f'\nRenamed {ok_count} files')

# ── Update xlsx ────────────────────────────────────────────────────────

print('\nUpdating xlsx...')
wb = openpyxl.load_workbook(XLSX)
ws = wb['Registros']

updated = 0
for row in range(2, ws.max_row + 1):
    pdf = ws.cell(row=row, column=13).value or ''
    if pdf in CORRECTIONS:
        ws.cell(row=row, column=13, value=CORRECTIONS[pdf])
        updated += 1

if 'Arquivos Extra' in wb.sheetnames:
    ws_extra = wb['Arquivos Extra']
    for row in range(2, ws_extra.max_row + 1):
        fname = ws_extra.cell(row=row, column=2).value or ''
        if fname in CORRECTIONS:
            ws_extra.cell(row=row, column=2, value=CORRECTIONS[fname])

wb.save(XLSX)
print(f'Updated {updated} rows in xlsx')
print('DONE!')
