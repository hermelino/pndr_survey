"""Organiza references.bib: renomeia chaves para formato curto e atualiza .tex.

Padroniza chaves BibTeX para formato PrimeiroAutor+Ano, resolve conflitos
(segundo autor ou sufixo), ordena entradas alfabeticamente e atualiza todas
as citacoes nos arquivos .tex correspondentes.

Uso:
    python organize_bibtex.py              # dry-run (padrao)
    python organize_bibtex.py --execute    # aplica mudancas
"""

from __future__ import annotations

import argparse
import logging
import re
from dataclasses import dataclass, field
from pathlib import Path

from unidecode import unidecode

log = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
BIB_PATH = BASE_DIR / "latex" / "references.bib"
ARCHIVE_PATH = BASE_DIR / "latex" / "ref_archived.bib"
TEX_DIR = BASE_DIR / "latex"

_SUFFIXES = {"junior", "júnior", "neto", "filho", "sobrinho", "jr", "sr"}
_PARTICLES = {"de", "da", "do", "dos", "das", "e"}

# Regex para detectar chave ja no formato curto: Autor2024 ou Autor2024a
_SHORT_KEY_RE = re.compile(r"^[A-Z][a-z]+(?:[A-Z][a-z]+)*\d{4}[a-z]?$")

# Stopwords portuguesas: devem ficar em minuscula no meio de titulos
_PT_STOPWORDS_TITLE = {
    "a", "o", "os", "as", "um", "uma", "uns", "umas",
    "à", "ao", "aos", "às",
    "com", "contra",
    "da", "das", "de", "do", "dos", "desde",
    "em", "entre",
    "na", "nas", "no", "nos",
    "para", "pela", "pelas", "pelo", "pelos", "por", "perante",
    "sem", "sob", "sobre",
    "e", "ou", "mas", "nem", "que",
}

# Padroes de nomes proprios: (regex, forma correta) — mais longos primeiro
_PROPER_NOUN_PATTERNS: list[tuple[str, str]] = [
    # Fundos Constitucionais
    (r"fundo\s+constitucional\s+de\s+financiamento\s+do\s+centro[\s-]oeste",
     "Fundo Constitucional de Financiamento do Centro-Oeste"),
    (r"fundo\s+constitucional\s+de\s+financiamento\s+do\s+nordeste",
     "Fundo Constitucional de Financiamento do Nordeste"),
    (r"fundo\s+constitucional\s+de\s+financiamento\s+do\s+norte",
     "Fundo Constitucional de Financiamento do Norte"),
    # Fundos de Desenvolvimento
    (r"fundo\s+de\s+desenvolvimento\s+do\s+nordeste",
     "Fundo de Desenvolvimento do Nordeste"),
    (r"fundo\s+de\s+desenvolvimento\s+do\s+norte",
     "Fundo de Desenvolvimento do Norte"),
    (r"fundo\s+de\s+desenvolvimento\s+do\s+centro[\s-]oeste",
     "Fundo de Desenvolvimento do Centro-Oeste"),
    # PNDR
    (r"pol[ií]tica\s+nacional\s+de\s+desenvolvimento\s+regional",
     "Política Nacional de Desenvolvimento Regional"),
    # Superintendencias
    (r"superintend[eê]ncia\s+d[eo]\s+desenvolvimento\s+d[oa]\s+nordeste",
     "Superintendência do Desenvolvimento do Nordeste"),
    (r"superintend[eê]ncia\s+d[eo]\s+desenvolvimento\s+d[oa]\s+amaz[oô]nia",
     "Superintendência do Desenvolvimento da Amazônia"),
    # Bancos
    (r"banco\s+do\s+nordeste\s+do\s+brasil",
     "Banco do Nordeste do Brasil"),
    (r"banco\s+do\s+nordeste\b",
     "Banco do Nordeste"),
    (r"banco\s+da\s+amaz[oô]nia",
     "Banco da Amazônia"),
    # Regioes brasileiras
    (r"\bnordeste\b", "Nordeste"),
    (r"\bcentro[\s-]oeste\b", "Centro-Oeste"),
]

_TITLE_FIELDS = ("title", "booktitle", "shorttitle")


# ---------------------------------------------------------------------------
# Modelos
# ---------------------------------------------------------------------------

@dataclass
class BibEntry:
    """Representa uma entrada BibTeX."""

    entry_type: str
    key: str
    body: str  # conteudo entre as chaves externas (campos)
    fields: dict[str, str] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------

def parse_bib_file(path: Path) -> list[BibEntry]:
    """Parseia arquivo .bib e retorna lista de BibEntry."""
    text = path.read_text(encoding="utf-8")
    entries: list[BibEntry] = []
    # Padrão: @type{key,  ... }  (com chaves aninhadas)
    pattern = re.compile(r"@(\w+)\s*\{", re.IGNORECASE)
    pos = 0
    while pos < len(text):
        m = pattern.search(text, pos)
        if not m:
            break
        entry_type = m.group(1).lower()
        brace_start = m.end() - 1  # posicao da {
        # Encontrar a } correspondente
        depth = 0
        i = brace_start
        while i < len(text):
            if text[i] == "{":
                depth += 1
            elif text[i] == "}":
                depth -= 1
                if depth == 0:
                    break
            i += 1
        inner = text[brace_start + 1 : i]  # conteudo entre { ... }
        # Extrair chave (ate a primeira virgula)
        comma_idx = inner.find(",")
        if comma_idx == -1:
            pos = i + 1
            continue
        key = inner[:comma_idx].strip()
        body = inner[comma_idx + 1 :]
        fields = _parse_fields(body)
        entries.append(BibEntry(entry_type=entry_type, key=key, body=body, fields=fields))
        pos = i + 1
    log.info("Parsed %d entries from %s", len(entries), path.name)
    return entries


def _parse_fields(body: str) -> dict[str, str]:
    """Extrai campos de uma entrada BibTeX."""
    fields: dict[str, str] = {}
    # Regex: nome_campo = {valor} ou nome_campo = valor
    pattern = re.compile(r"(\w+)\s*=\s*")
    pos = 0
    while pos < len(body):
        m = pattern.search(body, pos)
        if not m:
            break
        fname = m.group(1).lower()
        vstart = m.end()
        # Pular espacos
        while vstart < len(body) and body[vstart] in " \t":
            vstart += 1
        if vstart >= len(body):
            break
        if body[vstart] == "{":
            # Valor entre chaves — encontrar } correspondente
            depth = 0
            i = vstart
            while i < len(body):
                if body[i] == "{":
                    depth += 1
                elif body[i] == "}":
                    depth -= 1
                    if depth == 0:
                        break
                i += 1
            value = body[vstart + 1 : i]
            pos = i + 1
        elif body[vstart] == '"':
            # Valor entre aspas
            end = body.find('"', vstart + 1)
            if end == -1:
                break
            value = body[vstart + 1 : end]
            pos = end + 1
        else:
            # Valor numerico ou macro
            end = body.find(",", vstart)
            if end == -1:
                end = len(body)
            value = body[vstart:end].strip()
            pos = end + 1
        fields[fname] = value.strip()
    return fields


# ---------------------------------------------------------------------------
# Extracao de sobrenomes
# ---------------------------------------------------------------------------

def _extract_surname(author_str: str, index: int = 0) -> str | None:
    """Extrai sobrenome do autor na posicao `index` do campo author."""
    if not author_str:
        return None
    # Remover chaves BibTeX (autores institucionais: {BRASIL})
    clean = author_str.replace("{", "").replace("}", "")
    authors = re.split(r"\band\b", clean, flags=re.IGNORECASE)
    if index >= len(authors):
        return None
    author = authors[index].strip()
    if not author:
        return None
    # Formato "Surname, Given"
    if "," in author:
        surname = author.split(",")[0].strip()
        # Remover sufixos (Jr., Neto, Filho) do final do sobrenome
        words = surname.split()
        if len(words) > 1 and words[-1].lower().rstrip(".") in _SUFFIXES:
            surname = " ".join(words[:-1])
    else:
        # Formato "Given Surname" — extrair sobrenome com particulas/sufixos
        words = author.strip().split()
        if len(words) <= 1:
            return words[0] if words else None
        i = len(words) - 1
        surname_parts: list[str] = []
        # Sufixo (Junior, Neto, Filho)
        if words[i].lower().rstrip(".") in _SUFFIXES:
            surname_parts.insert(0, words[i])
            i -= 1
        # Sobrenome principal
        if i >= 0:
            surname_parts.insert(0, words[i])
            i -= 1
        # Particulas (de, da, dos)
        while i >= 0 and words[i].lower() in _PARTICLES:
            surname_parts.insert(0, words[i])
            i -= 1
        surname = " ".join(surname_parts)
    return surname


def _normalize_surname(surname: str) -> str:
    """Normaliza sobrenome para uso como chave: remove acentos, espacos, hifens."""
    normalized = unidecode(surname)
    # Remover hifens, espacos — manter apenas letras
    normalized = re.sub(r"[^a-zA-Z]", "", normalized)
    if not normalized:
        return normalized
    # Se todo maiusculo (ex: BRASIL), converter para Title Case
    if normalized.isupper() and len(normalized) > 1:
        normalized = normalized.title()
    # Garantir primeira letra maiuscula
    normalized = normalized[0].upper() + normalized[1:]
    return normalized


# ---------------------------------------------------------------------------
# Geracao de chaves
# ---------------------------------------------------------------------------

def _generate_short_key(
    entry: BibEntry,
    used_keys: set[str],
    preserved: set[str],
) -> str:
    """Gera chave curta para uma entrada.

    Se a chave atual ja esta no formato curto E nao conflita, preserva.
    Senao, gera nova chave com resolucao de conflitos.
    """
    author_field = entry.fields.get("author", "")
    year = entry.fields.get("year", "0000")
    # Limpar sufixos do year (ex: "2018a" -> "2018")
    year = re.sub(r"[^0-9]", "", year)[:4]
    if not year:
        year = "0000"

    surname1 = _extract_surname(author_field, 0)
    if not surname1:
        # Sem autor — usar chave existente ou titulo abreviado
        log.warning("Entry '%s' has no author field", entry.key)
        return entry.key

    base = _normalize_surname(surname1) + year

    # Se chave atual e exatamente a base (ou base+sufixo) e nao conflita, preservar
    if entry.key == base and base not in used_keys:
        return base
    if _SHORT_KEY_RE.match(entry.key) and entry.key.startswith(base):
        if entry.key not in used_keys:
            return entry.key

    # Tentar base simples
    if base not in used_keys and base not in preserved:
        return base

    # Tentar com segundo autor
    surname2 = _extract_surname(author_field, 1)
    if surname2:
        base2 = _normalize_surname(surname1) + _normalize_surname(surname2) + year
        if base2 not in used_keys and base2 not in preserved:
            return base2

    # Sufixo alfabetico
    for ch in "bcdefghijklmnopqrstuvwxyz":
        candidate = f"{base}{ch}"
        if candidate not in used_keys and candidate not in preserved:
            return candidate

    raise ValueError(f"Too many conflicts for key base '{base}'")


def build_key_mapping(entries: list[BibEntry]) -> dict[str, str]:
    """Constroi mapeamento old_key -> new_key para todas as entradas.

    Processa em duas passadas:
    1. Identifica chaves ja no formato curto que serao preservadas.
    2. Gera novas chaves para as restantes, respeitando as preservadas.
    """
    # Primeira passada: identificar chaves que ja estao corretas
    preserved: set[str] = set()
    needs_rename: list[int] = []

    for i, entry in enumerate(entries):
        author_field = entry.fields.get("author", "")
        year = re.sub(r"[^0-9]", "", entry.fields.get("year", ""))[:4]
        surname1 = _extract_surname(author_field, 0)
        if surname1:
            expected_base = _normalize_surname(surname1) + year
        else:
            expected_base = None

        # Chave curta que corresponde ao autor+ano: preservar
        if (
            _SHORT_KEY_RE.match(entry.key)
            and expected_base
            and entry.key.startswith(expected_base)
        ):
            preserved.add(entry.key)
        else:
            needs_rename.append(i)

    log.info(
        "Keys already in short form: %d, to rename: %d",
        len(preserved),
        len(needs_rename),
    )

    # Segunda passada: gerar chaves novas
    used_keys: set[str] = set(preserved)
    mapping: dict[str, str] = {}

    for i, entry in enumerate(entries):
        if entry.key in preserved:
            continue
        new_key = _generate_short_key(entry, used_keys, preserved)
        used_keys.add(new_key)
        if new_key != entry.key:
            mapping[entry.key] = new_key

    return mapping


# ---------------------------------------------------------------------------
# Reescrita do .bib
# ---------------------------------------------------------------------------

def _rebuild_bib(entries: list[BibEntry], mapping: dict[str, str]) -> str:
    """Reconstroi o conteudo do .bib com chaves atualizadas e ordenadas."""
    # Atualizar chaves
    updated: list[BibEntry] = []
    for entry in entries:
        new_key = mapping.get(entry.key, entry.key)
        updated.append(BibEntry(
            entry_type=entry.entry_type,
            key=new_key,
            body=entry.body,
            fields=entry.fields,
        ))
    # Ordenar alfabeticamente (case-insensitive)
    updated.sort(key=lambda e: e.key.lower())
    # Reconstruir texto
    lines: list[str] = []
    for entry in updated:
        lines.append(f"@{entry.entry_type}{{{entry.key},{entry.body}}}")
        lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Atualizacao de .tex
# ---------------------------------------------------------------------------

def _update_tex_files(
    tex_dir: Path, mapping: dict[str, str],
) -> dict[str, int]:
    """Atualiza citacoes em todos os .tex, retorna {arquivo: n_substituicoes}."""
    results: dict[str, int] = {}
    tex_files = sorted(tex_dir.rglob("*.tex"))
    # Construir regex que casa qualquer chave antiga em contexto de citacao
    if not mapping:
        return results
    # Substituir chave por chave (nao regex global — evitar falsos positivos)
    for tex_path in tex_files:
        content = tex_path.read_text(encoding="utf-8")
        original = content
        count = 0
        for old_key, new_key in mapping.items():
            # Substituir em contextos \cite{...} e \citeonline{...}
            # A chave pode aparecer sozinha ou em lista separada por virgula
            # Usar word boundary: a chave e delimitada por { , ou }
            pattern = re.compile(
                r"(?<=[\{,])\s*" + re.escape(old_key) + r"\s*(?=[,\}])"
            )
            new_content = pattern.sub(new_key, content)
            n = len(pattern.findall(content))
            count += n
            content = new_content
        if count > 0:
            tex_path.write_text(content, encoding="utf-8")
            rel = tex_path.relative_to(BASE_DIR)
            results[str(rel)] = count
            log.info("Updated %d citations in %s", count, rel)
    return results


# ---------------------------------------------------------------------------
# Correcao de titulos
# ---------------------------------------------------------------------------


def _fix_title_case(title: str) -> str:
    """Fix Portuguese title capitalization: lowercase stopwords, capitalize proper nouns."""
    if not title:
        return title
    result = title
    # Passo 1: Lowercasar stopwords no meio do titulo (ex: "Da" -> "da")
    for sw in _PT_STOPWORDS_TITLE:
        cap = sw[0].upper() + sw[1:]
        # Casar stopword Title Case precedida de espaco/til/abertura
        # e seguida de espaco/pontuacao/fechamento (nao no inicio do titulo)
        pattern = re.compile(
            r"(?<=[\s~(])" + re.escape(cap) + r"(?=[\s~,.:;)\}\-]|$)"
        )
        result = pattern.sub(sw, result)
    # Passo 2: Capitalizar nomes proprios conhecidos (case-insensitive)
    for pat, repl in _PROPER_NOUN_PATTERNS:
        result = re.sub(pat, repl, result, flags=re.IGNORECASE)
    return result


def _replace_field_value(body: str, field_name: str, new_value: str) -> str:
    """Replace a BibTeX field value in the raw entry body."""
    pattern = re.compile(
        r"(" + re.escape(field_name) + r"\s*=\s*)\{",
        re.IGNORECASE,
    )
    m = pattern.search(body)
    if not m:
        return body
    start = m.end()  # posicao logo apos a { de abertura
    depth = 1
    i = start
    while i < len(body) and depth > 0:
        if body[i] == "{":
            depth += 1
        elif body[i] == "}":
            depth -= 1
        i += 1
    # body[start:i-1] = valor antigo, body[i-1] = } de fechamento
    return body[:start] + new_value + body[i - 1 :]


def _compute_title_fixes(
    entries: list[BibEntry],
) -> list[tuple[int, str, str, str]]:
    """Compute title fixes without applying. Returns [(idx, field, old, new)]."""
    fixes: list[tuple[int, str, str, str]] = []
    for idx, entry in enumerate(entries):
        for fld in _TITLE_FIELDS:
            old = entry.fields.get(fld, "")
            if not old:
                continue
            new = _fix_title_case(old)
            if new != old:
                fixes.append((idx, fld, old, new))
    return fixes


def _apply_title_fixes(
    entries: list[BibEntry],
    fixes: list[tuple[int, str, str, str]],
) -> None:
    """Apply title fixes to entries in place."""
    for idx, fld, _old, new in fixes:
        entries[idx].fields[fld] = new
        entries[idx].body = _replace_field_value(entries[idx].body, fld, new)


# ---------------------------------------------------------------------------
# Arquivamento de referencias nao citadas
# ---------------------------------------------------------------------------

def _collect_cited_keys(tex_dir: Path) -> set[str]:
    """Coleta todas as chaves citadas nos arquivos .tex."""
    cited: set[str] = set()
    cite_re = re.compile(r"\\cite(?:online)?\{([^}]+)\}")
    for tex_path in sorted(tex_dir.rglob("*.tex")):
        content = tex_path.read_text(encoding="utf-8")
        # Ignorar linhas comentadas
        lines = [ln for ln in content.splitlines() if not ln.lstrip().startswith("%")]
        text = "\n".join(lines)
        for m in cite_re.finditer(text):
            keys = [k.strip() for k in m.group(1).split(",")]
            cited.update(keys)
    return cited


def _split_used_archived(
    entries: list[BibEntry],
    cited_keys: set[str],
) -> tuple[list[BibEntry], list[BibEntry]]:
    """Separa entradas em usadas (citadas) e arquivadas (nao citadas)."""
    used: list[BibEntry] = []
    archived: list[BibEntry] = []
    for entry in entries:
        if entry.key in cited_keys:
            used.append(entry)
        else:
            archived.append(entry)
    return used, archived


# ---------------------------------------------------------------------------
# Relatorio
# ---------------------------------------------------------------------------

def _generate_report(
    mapping: dict[str, str],
    tex_updates: dict[str, int],
    total_entries: int,
    archived_keys: list[str] | None = None,
    title_fixes: list[tuple[int, str, str, str]] | None = None,
    entries: list[BibEntry] | None = None,
) -> str:
    """Gera relatorio de mudancas."""
    lines: list[str] = []
    lines.append("=" * 60)
    lines.append("ORGANIZE BIBTEX — REPORT")
    lines.append("=" * 60)
    lines.append(f"Total entries:       {total_entries}")
    lines.append(f"Keys renamed:        {len(mapping)}")
    lines.append(f"Keys preserved:      {total_entries - len(mapping)}")
    if archived_keys is not None:
        lines.append(f"Archived (unused):   {len(archived_keys)}")
        lines.append(f"Kept (cited):        {total_entries - len(archived_keys)}")
    if title_fixes is not None:
        lines.append(f"Title fields fixed:  {len(title_fixes)}")
    lines.append(f"TeX files updated:   {len(tex_updates)}")
    total_cit = sum(tex_updates.values())
    lines.append(f"Citations updated:   {total_cit}")
    lines.append("")
    if mapping:
        lines.append("KEY RENAMES:")
        lines.append("-" * 60)
        for old, new in sorted(mapping.items(), key=lambda x: x[1].lower()):
            lines.append(f"  {old:<50s} -> {new}")
    if archived_keys:
        lines.append("")
        lines.append("ARCHIVED (unused in .tex):")
        lines.append("-" * 60)
        for key in sorted(archived_keys, key=str.lower):
            lines.append(f"  {key}")
    if title_fixes:
        lines.append("")
        lines.append("TITLE FIXES:")
        lines.append("-" * 60)
        for idx, fld, old, new in title_fixes:
            key = entries[idx].key if entries else f"entry#{idx}"
            final_key = mapping.get(key, key)
            lines.append(f"  [{final_key}] {fld}:")
            lines.append(f"    - {old}")
            lines.append(f"    + {new}")
    if tex_updates:
        lines.append("")
        lines.append("TEX FILES UPDATED:")
        lines.append("-" * 60)
        for fpath, cnt in sorted(tex_updates.items()):
            lines.append(f"  {fpath:<45s} ({cnt} citations)")
    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    """Ponto de entrada CLI."""
    parser = argparse.ArgumentParser(
        description="Organize references.bib: short keys, alphabetical order.",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Apply changes (default is dry-run).",
    )
    parser.add_argument(
        "--archive",
        action="store_true",
        help="Move uncited entries to ref_archived.bib.",
    )
    parser.add_argument(
        "--fix-titles",
        action="store_true",
        help="Fix Portuguese title capitalization (stopwords, proper nouns).",
    )
    parser.add_argument(
        "--bib",
        type=Path,
        default=BIB_PATH,
        help="Path to references.bib.",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s: %(message)s",
    )

    entries = parse_bib_file(args.bib)

    # Compute title fixes (non-destructive)
    title_fixes: list[tuple[int, str, str, str]] = []
    if args.fix_titles:
        title_fixes = _compute_title_fixes(entries)
        log.info("Title fixes found: %d", len(title_fixes))
        # Apply early in execute mode so downstream ops use fixed titles
        if args.execute and title_fixes:
            _apply_title_fixes(entries, title_fixes)

    mapping = build_key_mapping(entries)

    # Aplicar renomeacao nas chaves antes de verificar citacoes
    renamed_entries: list[BibEntry] = []
    for entry in entries:
        new_key = mapping.get(entry.key, entry.key)
        renamed_entries.append(BibEntry(
            entry_type=entry.entry_type,
            key=new_key,
            body=entry.body,
            fields=entry.fields,
        ))

    # Detectar referencias nao citadas (usando chaves novas)
    archived_keys: list[str] | None = None
    if args.archive:
        cited_keys = _collect_cited_keys(TEX_DIR)
        log.info("Found %d unique citation keys in .tex files", len(cited_keys))
        # Mapear chaves citadas: se o .tex ainda usa chave antiga, considerar
        all_cited = set(cited_keys)
        for old, new in mapping.items():
            if old in all_cited:
                all_cited.add(new)
        used, archived = _split_used_archived(renamed_entries, all_cited)
        archived_keys = [e.key for e in archived]
        log.info("Used: %d, Archived: %d", len(used), len(archived))

    if not args.execute:
        report = _generate_report(
            mapping, {}, len(entries), archived_keys, title_fixes, entries,
        )
        log.info("DRY RUN — no files modified.\n%s", report)
        return

    # Atualizar .tex primeiro (antes de renomear .bib)
    tex_updates = _update_tex_files(TEX_DIR, mapping)

    if args.archive and archived_keys is not None:
        # Re-coletar citacoes apos atualizacao dos .tex
        cited_keys = _collect_cited_keys(TEX_DIR)
        used, archived = _split_used_archived(renamed_entries, cited_keys)
        archived_keys = [e.key for e in archived]

        # Escrever ref_archived.bib
        archive_path = args.bib.parent / "ref_archived.bib"
        archived.sort(key=lambda e: e.key.lower())
        arch_lines: list[str] = []
        for entry in archived:
            arch_lines.append(f"@{entry.entry_type}{{{entry.key},{entry.body}}}")
            arch_lines.append("")
        archive_path.write_text("\n".join(arch_lines), encoding="utf-8")
        log.info("Archived %d entries to %s", len(archived), archive_path.name)

        # Escrever .bib apenas com entradas usadas
        new_bib = _rebuild_bib(
            [e for e in entries if mapping.get(e.key, e.key) in cited_keys],
            mapping,
        )
    else:
        new_bib = _rebuild_bib(entries, mapping)

    args.bib.write_text(new_bib, encoding="utf-8")
    log.info("Wrote updated %s", args.bib.name)

    report = _generate_report(
        mapping, tex_updates, len(entries), archived_keys, title_fixes, entries,
    )
    log.info("\n%s", report)


if __name__ == "__main__":
    main()
