"""Converte approved_papers.ris para BibTeX e atualiza references.bib.

Lê o RIS dos estudos aprovados, converte cada entrada para formato BibTeX
e insere na seção gerada automaticamente de latex/references.bib
(preservando as entradas manuais existentes acima do marcador).

Uso: python generate_bibtex.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

from unidecode import unidecode

BASE_DIR = Path(__file__).resolve().parent.parent
RIS_PATH = BASE_DIR / "data" / "2-papers" / "approved_papers.ris"
BIB_PATH = BASE_DIR / "latex" / "references.bib"

MARKER_START = "% === INÍCIO SEÇÃO GERADA (generate_bibtex.py) — NÃO EDITAR ABAIXO ==="
MARKER_END = "% === FIM SEÇÃO GERADA ==="

_TYPE_MAP = {"JOUR": "article", "RPRT": "techreport", "CPAPER": "inproceedings"}
_SUFFIXES = {"junior", "júnior", "neto", "filho", "sobrinho"}
_PARTICLES = {"de", "da", "do", "dos", "das", "e"}


def parse_ris(ris_path: Path) -> list[dict[str, list[str]]]:
    """Parse RIS em lista de dicts {tag: [valores]}."""
    entries: list[dict[str, list[str]]] = []
    current: dict[str, list[str]] = {}
    with open(ris_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line.strip():
                continue
            m = re.match(r"^([A-Z][A-Z0-9])\s\s-\s(.*)$", line)
            if not m:
                continue
            tag, value = m.group(1), m.group(2)
            if tag == "TY":
                current = {}
                current.setdefault(tag, []).append(value)
            elif tag == "ER":
                if current:
                    entries.append(current)
                current = {}
            else:
                current.setdefault(tag, []).append(value)
    return entries


def _split_given_surname(full_name: str) -> tuple[str, str]:
    """Separa 'Given Middle Surname' em (given, surname).

    Trata sufixos (Júnior, Neto, Filho) e partículas (de, da, do).
    """
    words = full_name.strip().split()
    if len(words) <= 1:
        return ("", full_name.strip())

    i = len(words) - 1
    surname_parts: list[str] = []

    # Sufixo (Júnior, Neto, Filho)
    if words[i].lower().rstrip(".") in _SUFFIXES:
        surname_parts.insert(0, words[i])
        i -= 1

    # Sobrenome principal
    if i >= 0:
        surname_parts.insert(0, words[i])
        i -= 1

    # Partículas (de, da, do)
    while i >= 0 and words[i].lower() in _PARTICLES:
        surname_parts.insert(0, words[i])
        i -= 1

    return (" ".join(words[: i + 1]), " ".join(surname_parts))


def _parse_authors(entry: dict[str, list[str]]) -> list[str]:
    """Retorna lista de autores em formato 'Surname, Given'.

    Detecta formato CAPES (nomes completos separados por vírgula em
    uma única linha AU) vs. formato padrão (uma linha AU por autor).
    """
    au_lines = entry.get("AU", [])
    if not au_lines:
        return []

    if len(au_lines) == 1:
        parts = [p.strip() for p in au_lines[0].split(",")]
        has_space = sum(1 for p in parts if " " in p)
        # CAPES: múltiplos nomes completos "Given Surname" separados por vírgula
        if has_space >= len(parts) * 0.6 and len(parts) >= 2:
            authors = []
            for name in parts:
                given, surname = _split_given_surname(name)
                authors.append(f"{surname}, {given}" if given else surname)
            return authors
        # Autor único em formato "Surname, Given"
        return [au_lines[0]]

    # Múltiplas linhas AU: cada uma é "Surname, Given"
    return [au.strip() for au in au_lines]


def _normalize_author(author: str) -> str:
    """Normaliza MAIÚSCULAS para Title Case em nomes de autores."""
    if "," in author:
        parts = author.split(",", 1)
        surname = parts[0].strip()
        given = parts[1].strip() if len(parts) > 1 else ""
        if surname.isupper() and len(surname) > 2:
            surname = surname.title()
        if given.isupper() and len(given) > 2:
            given = given.title()
        return f"{surname}, {given}" if given else surname
    return author.title() if author.isupper() else author


def _extract_key_surname(authors: list[str]) -> str:
    """Extrai sobrenome do primeiro autor para chave BibTeX."""
    if not authors:
        return "Unknown"
    first = authors[0].strip()
    surname = first.split(",")[0].strip() if "," in first else first
    if surname.isupper():
        surname = surname.title()
    return surname


def _make_key(surname: str, year: str, used: set[str]) -> str:
    """Gera chave BibTeX única: Surname + Year + sufixo alfabético se houver colisão."""
    base = unidecode(surname).replace(" ", "")
    base = re.sub(r"[^a-zA-Z]", "", base)
    base = f"{base}{year}"
    if base not in used:
        used.add(base)
        return base
    for ch in "abcdefghijklmnopqrstuvwxyz":
        candidate = f"{base}{ch}"
        if candidate not in used:
            used.add(candidate)
            return candidate
    raise ValueError(f"Muitas colisões para chave {base}")


def _infer_institution(entry: dict[str, list[str]]) -> str:
    """Infere instituição a partir do URL para entradas RPRT."""
    for url in entry.get("UR", []):
        if "ipe:ipetds" in url:
            return "Instituto de Pesquisa Econômica Aplicada (IPEA)"
        if "wiw:wiwrsa" in url:
            return "European Regional Science Association (ERSA)"
    return ""


def _infer_booktitle(entry: dict[str, list[str]]) -> str:
    """Infere booktitle a partir do URL para entradas CPAPER (ANPEC)."""
    for url in entry.get("UR", []):
        if "anpec.org.br/nordeste" in url:
            return "Encontro Regional de Economia (Fórum BNB)"
        if "anpec.org.br/encontro" in url:
            return "Encontro Nacional de Economia"
    return "Encontro Nacional de Economia"


def entry_to_bibtex(entry: dict[str, list[str]], used: set[str]) -> str:
    """Converte uma entrada RIS parsed para string BibTeX."""
    ris_type = entry.get("TY", ["GEN"])[0]
    bib_type = _TYPE_MAP.get(ris_type, "misc")
    authors = _parse_authors(entry)
    year = entry.get("PY", [""])[0]
    title = entry.get("TI", [""])[0]

    surname = _extract_key_surname(authors)
    key = _make_key(surname, year, used)

    lines = [f"@{bib_type}{{{key},"]

    if authors:
        normalized = [_normalize_author(a) for a in authors]
        lines.append(f'\tauthor = {{{" and ".join(normalized)}}},')

    if title:
        lines.append(f"\ttitle = {{{{{title}}}}},")

    if year:
        lines.append(f"\tyear = {{{year}}},")

    # Campos específicos por tipo
    if bib_type == "article":
        for tag, field in [("JO", "journal"), ("VL", "volume"), ("IS", "number")]:
            val = entry.get(tag, [""])[0]
            if val:
                lines.append(f"\t{field} = {{{val}}},")
        pages = entry.get("SP", [""])[0]
        if pages:
            lines.append(f"\tpages = {{{pages}}},")

    elif bib_type == "techreport":
        inst = _infer_institution(entry)
        if inst:
            lines.append(f"\tinstitution = {{{inst}}},")
        num = entry.get("IS", [""])[0]
        if num:
            lines.append(f"\tnumber = {{{num}}},")

    elif bib_type == "inproceedings":
        lines.append(f"\tbooktitle = {{{_infer_booktitle(entry)}}},")

    # DOI ou URL (DOI tem prioridade)
    doi = entry.get("DO", [""])[0]
    if doi:
        lines.append(f"\tdoi = {{{doi}}},")
    else:
        url = entry.get("UR", [""])[0]
        if url:
            lines.append(f"\turl = {{{url}}},")

    lines.append("}")
    return "\n".join(lines)


def _get_existing_keys(bib_path: Path) -> set[str]:
    """Extrai chaves BibTeX existentes na seção manual do .bib."""
    keys: set[str] = set()
    if not bib_path.exists():
        return keys
    content = bib_path.read_text(encoding="utf-8")
    # Considerar apenas a seção manual (antes do marcador)
    if MARKER_START in content:
        content = content[: content.index(MARKER_START)]
    for m in re.finditer(r"@\w+\{(\w+),", content):
        keys.add(m.group(1))
    return keys


def update_bib(bib_path: Path, bibtex_entries: list[str]) -> None:
    """Atualiza references.bib preservando entradas manuais acima do marcador."""
    content = ""
    if bib_path.exists():
        content = bib_path.read_text(encoding="utf-8")

    if MARKER_START in content:
        manual = content[: content.index(MARKER_START)].rstrip()
    else:
        manual = content.rstrip()

    generated = MARKER_START + "\n"
    generated += f"% {len(bibtex_entries)} entradas convertidas de approved_papers.ris\n\n"
    generated += "\n\n".join(bibtex_entries)
    generated += "\n\n" + MARKER_END + "\n"

    bib_path.write_text(manual + "\n\n" + generated, encoding="utf-8")


def main() -> None:
    if not RIS_PATH.exists():
        print(f"ERRO: {RIS_PATH} não encontrado", file=sys.stderr)
        sys.exit(1)

    entries = parse_ris(RIS_PATH)
    print(f"Entradas RIS: {len(entries)}")

    used_keys = _get_existing_keys(BIB_PATH)
    if used_keys:
        print(f"Chaves manuais existentes: {sorted(used_keys)}")

    bibtex_entries: list[str] = []
    for entry in entries:
        bibtex_entries.append(entry_to_bibtex(entry, used_keys))

    update_bib(BIB_PATH, bibtex_entries)
    print(f"\nBibTeX atualizado: {BIB_PATH}")
    print(f"Entradas geradas: {len(bibtex_entries)}")
    generated_keys = sorted(k for k in used_keys if k not in {"Pageetal2021", "MadalenoWaights2016"})
    print(f"Chaves geradas: {', '.join(generated_keys)}")


if __name__ == "__main__":
    main()
