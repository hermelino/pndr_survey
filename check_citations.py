import re, os, glob

latex_dir = r"c:\OneDrive\github\pndr_survey\latex"

tex_files = glob.glob(os.path.join(latex_dir, "*.tex"))
print("=== TEX FILES ===")
for f in tex_files:
    print("  " + os.path.basename(f))

cite_pat = re.compile(r"\(?:cite|citeonline|citeauthor|citeyear)\{([^}]+)\}")
cited_keys = {}
for f in tex_files:
    with open(f, "r", encoding="utf-8") as fh:
        content = fh.read()
    matches = cite_pat.findall(content)
    for match in matches:
        for key in match.split(","):
            key = key.strip()
            if key:
                if key not in cited_keys:
                    cited_keys[key] = set()
                cited_keys[key].add(os.path.basename(f))

print("")
print("=== CITED KEYS (from .tex files): " + str(len(cited_keys)) + " unique keys ===")
for k in sorted(cited_keys.keys()):
    print("  " + k)

bib_file = os.path.join(latex_dir, "references.bib")
with open(bib_file, "r", encoding="utf-8") as fh:
    bib_content = fh.read()
bib_pat = re.compile(r"^\s*@\w+\{([^,]+),", re.MULTILINE)
bib_keys = set(m.strip() for m in bib_pat.findall(bib_content))

print("")
print("=== BIB KEYS (from references.bib): " + str(len(bib_keys)) + " unique keys ===")
for k in sorted(bib_keys):
    print("  " + k)

print("")
print("=== ORPHAN CITATIONS (cited in .tex but missing from .bib) ===")
orphans = sorted(set(cited_keys.keys()) - bib_keys)
if orphans:
    for k in orphans:
        files = ", ".join(sorted(cited_keys[k]))
        print("  MISSING: " + k + "  (cited in: " + files + ")")
else:
    print("  None found. All citation keys exist in references.bib.")
print("")
print("Total orphan citations: " + str(len(orphans)))

print("")
print("=== UNUSED BIB ENTRIES (in .bib but never cited in .tex) ===")
unused = sorted(bib_keys - set(cited_keys.keys()))
if unused:
    for k in unused:
        print("  UNUSED: " + k)
else:
    print("  None found. All bib entries are cited.")
print("")
print("Total unused bib entries: " + str(len(unused)))
