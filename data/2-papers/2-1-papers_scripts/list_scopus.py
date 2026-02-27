import openpyxl

filepath = r"c:\OneDrive\github\pndr_survey\data\2-papers\all_papers.xlsx"
wb = openpyxl.load_workbook(filepath, read_only=True, data_only=True)
ws = wb["Registros"]

# Actual columns (1-indexed):
# A=1 Base, B=2 URL, C=3 Baixado, D=4 Arquivo PDF, E=5 ID,
# F=6 Titulo, G=7 Autores, H=8 Ano, I=9 Periodico, J=10 DOI,
# K=11 Resumo, L=12 Tipo, M=13 Palavras-chave, N=14 Obs

scopus_rows = []
for i, row in enumerate(ws.iter_rows(min_row=2, max_col=14, values_only=True), start=2):
    base = row[0]  # A: Base
    if base and str(base).strip().lower() == "scopus":
        titulo   = str(row[5] or "").strip()[:60]   # F: Titulo
        autores  = str(row[6] or "").strip()[:40]   # G: Autores
        ano      = str(row[7] or "").strip()         # H: Ano
        baixado  = str(row[2] or "").strip()         # C: Baixado
        pdf      = str(row[3] or "").strip()         # D: Arquivo PDF
        scopus_rows.append((i, titulo, autores, ano, baixado, pdf))

wb.close()

# Print header
hdr = f"{'Row':>4}  {'Titulo':<62}  {'Autores':<42}  {'Ano':<5}  {'Baixado':<8}  Arquivo PDF"
print(hdr)
print("-" * len(hdr))

for (rownum, titulo, autores, ano, baixado, pdf) in scopus_rows:
    print(f"{rownum:>4}  {titulo:<62}  {autores:<42}  {ano:<5}  {baixado:<8}  {pdf}")

# Summary
total = len(scopus_rows)
baixado_sim = sum(1 for r in scopus_rows if r[4].lower() == "sim")
has_pdf = sum(1 for r in scopus_rows if r[5] and r[5].lower() not in ("", "none", "nan"))

print()
print("=" * 80)
print("SUMMARY")
print(f"  Total Scopus records:           {total}")
print(f"  Baixado = Sim:                  {baixado_sim}")
print(f"  Baixado = Nao:                  {total - baixado_sim}")
print(f"  With PDF filename (col D):      {has_pdf}")
print(f"  Without PDF filename:           {total - has_pdf}")
print("=" * 80)
