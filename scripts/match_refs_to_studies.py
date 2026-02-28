"""Identifica referências em JSONs que correspondem a estudos na triagem.

Para cada referência de cada JSON em refs_por_estudo/, verifica se ela
corresponde a algum paper em 2-2-papers.json. Adiciona campos:
  - cita_estudo_aprovado (bool)  — match com qualquer estudo na lista
  - estudo_citado_pdf (str | None)
  - match_score (int | None)

Usa fuzzy matching de título (token_sort_ratio) + verificação de sobrenomes.
Fonte enriquecida: usa titulo do registro E titulo extraído pelo LLM (S1).

Matching em duas faixas:
  - Anos iguais: threshold >= 75 (FUZZY_THRESHOLD)
  - Anos diferentes (±6): threshold >= 90 (YEAR_FLEX_THRESHOLD)
    Captura working papers citados pelo ano de publicação diferente.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from rapidfuzz import fuzz
from unidecode import unidecode

# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
PAPERS_JSON = BASE_DIR / "data" / "2-papers" / "2-2-papers.json"
REFS_DIR = BASE_DIR / "data" / "3-ref-bib" / "refs_por_estudo"

FUZZY_THRESHOLD = 75
YEAR_FLEX_THRESHOLD = 90   # threshold mais alto quando anos não batem
MAX_YEAR_DIFF = 6          # tolerância máxima de diferença de ano

STOPWORDS = {
    "the", "a", "an", "of", "in", "on", "at", "to", "for", "and", "or",
    "with", "by", "from", "as", "is", "was", "are", "were", "been",
    "o", "os", "um", "uma", "uns", "umas", "de", "do", "da",
    "dos", "das", "em", "no", "na", "nos", "nas", "por", "para", "com",
    "que", "se", "ao", "aos",
    "el", "la", "los", "las", "un", "una", "unos", "unas", "del", "en", "con",
}


# ---------------------------------------------------------------------------
# Normalização
# ---------------------------------------------------------------------------
def normalize_title(title: str) -> str:
    text = unidecode(title).lower()
    text = re.sub(r"[^\w\s]", " ", text)
    words = [w for w in text.split() if w not in STOPWORDS]
    return " ".join(words)


def extract_surnames_paper(authors_str: str) -> List[str]:
    """Extrai sobrenomes da string de autores dos papers (formatos variados)."""
    if not authors_str:
        return []

    surnames = []
    if ";" in authors_str:
        parts = authors_str.split(";")
    else:
        parts = authors_str.split(",")

    for part in parts:
        part = part.strip()
        if not part:
            continue
        if "," in part:
            surname = part.split(",")[0].strip()
        else:
            tokens = part.split()
            if not tokens:
                continue
            surname = tokens[-1]
            suffixes = {"junior", "júnior", "jr", "filho", "neto", "sobrinho"}
            if surname.lower().rstrip(".") in suffixes and len(tokens) >= 2:
                surname = tokens[-2] + " " + tokens[-1]

        surname_norm = unidecode(surname).lower().strip().rstrip(".")
        if surname_norm and len(surname_norm) > 1:
            surnames.append(surname_norm)

    return surnames


def extract_surnames_ref(autor_str: str) -> List[str]:
    """Extrai sobrenomes do campo autor de uma referência (formato ABNT/APA)."""
    if not autor_str:
        return []

    surnames = []
    autor_str = re.sub(r"\bet al\.?\b", "", autor_str, flags=re.IGNORECASE)
    autor_str = re.sub(r"\band\b", ";", autor_str)
    # Só troca "e" isolado se cercado por espaços e não é parte de palavra
    autor_str = re.sub(r"(?<=\s)e(?=\s)", ";", autor_str)

    if ";" in autor_str:
        parts = autor_str.split(";")
    else:
        parts = [autor_str]

    for part in parts:
        part = part.strip()
        if not part:
            continue

        if "," in part:
            surname = part.split(",")[0].strip()
        else:
            tokens = part.split()
            if not tokens:
                continue
            if part == part.upper():
                surname = tokens[0]
            else:
                surname = tokens[-1]
                suffixes = {"junior", "júnior", "jr", "filho", "neto", "sobrinho"}
                if surname.lower().rstrip(".") in suffixes and len(tokens) >= 2:
                    surname = tokens[-2] + " " + tokens[-1]

        surname_norm = unidecode(surname).lower().strip().rstrip(".")
        if surname_norm and len(surname_norm) > 1:
            surnames.append(surname_norm)

    return surnames


# ---------------------------------------------------------------------------
# Carregamento
# ---------------------------------------------------------------------------
def load_papers(json_path: Path) -> List[Dict]:
    """Carrega papers do JSON enriquecido e pré-computa dados para matching."""
    with open(json_path, "r", encoding="utf-8") as f:
        raw = json.load(f)

    papers = []
    for p in raw:
        titulo = p.get("titulo") or ""
        s1_titulo = (p.get("s1") or {}).get("titulo") or ""
        autores = p.get("autores") or ""
        s1_autores = (p.get("s1") or {}).get("autores") or ""
        ano = (p.get("ano") or "").split(".")[0].strip()
        pdf = p.get("arquivo_pdf") or ""

        # Combinar sobrenomes de ambas as fontes
        sobrenomes = set(extract_surnames_paper(autores))
        sobrenomes.update(extract_surnames_paper(s1_autores))

        # Normalizar títulos de ambas as fontes
        titulo_norm = normalize_title(titulo) if titulo else ""
        s1_titulo_norm = normalize_title(s1_titulo) if s1_titulo else ""

        papers.append({
            "titulo_norm": titulo_norm,
            "s1_titulo_norm": s1_titulo_norm,
            "sobrenomes": list(sobrenomes),
            "ano": ano,
            "pdf": pdf,
        })

    return papers


def load_json(json_path: Path) -> Dict:
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(json_path: Path, data: Dict) -> None:
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# Matching
# ---------------------------------------------------------------------------
def find_match(
    ref: Dict,
    papers: List[Dict],
    self_pdf: str,
) -> Tuple[Optional[str], Optional[int]]:
    """Tenta encontrar um paper que corresponda a esta referência."""
    ref_ano = (ref.get("ano") or "").split(".")[0].strip()
    ref_titulo = ref.get("titulo") or ""
    ref_autor = ref.get("autor") or ""

    ref_titulo_norm = normalize_title(ref_titulo) if ref_titulo else ""
    ref_sobrenomes = extract_surnames_ref(ref_autor)

    if not ref_titulo_norm and not ref_sobrenomes:
        return None, None

    best_match_pdf = None
    best_score = 0

    for paper in papers:
        # Auto-exclusão
        if paper["pdf"] and self_pdf:
            paper_stem = paper["pdf"].replace(".pdf", "")
            self_stem = self_pdf.replace("_refs.json", "")
            if paper_stem == self_stem or paper_stem in self_stem:
                continue

        # Filtro por ano (com tolerância para working papers)
        year_exact = True
        if ref_ano and paper["ano"]:
            try:
                diff = abs(int(ref_ano) - int(paper["ano"]))
            except ValueError:
                diff = 0
            if diff > MAX_YEAR_DIFF:
                continue
            if diff > 0:
                year_exact = False

        # Similaridade de título (tenta tanto titulo do registro quanto titulo S1)
        score = 0
        if ref_titulo_norm:
            if paper["titulo_norm"]:
                score = max(score, fuzz.token_sort_ratio(ref_titulo_norm, paper["titulo_norm"]))
            if paper["s1_titulo_norm"]:
                score = max(score, fuzz.token_sort_ratio(ref_titulo_norm, paper["s1_titulo_norm"]))

        # Threshold mais alto quando anos não batem (exige match mais rigoroso)
        threshold = FUZZY_THRESHOLD if year_exact else YEAR_FLEX_THRESHOLD
        if score < threshold:
            continue

        # Verificação de sobrenomes
        if ref_sobrenomes and paper["sobrenomes"]:
            ref_set = set(ref_sobrenomes)
            paper_set = set(paper["sobrenomes"])

            direct_match = ref_set & paper_set

            if not direct_match:
                fuzzy_match = False
                for rs in ref_set:
                    for ps in paper_set:
                        if fuzz.ratio(rs, ps) >= 85:
                            fuzzy_match = True
                            break
                    if fuzzy_match:
                        break
                if not fuzzy_match:
                    continue
        elif ref_sobrenomes or paper["sobrenomes"]:
            if score < 90:
                continue

        if score > best_score:
            best_score = score
            best_match_pdf = paper["pdf"]

    if best_match_pdf:
        return best_match_pdf, best_score
    return None, None


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    print(f"Carregando papers de {PAPERS_JSON}...")
    papers = load_papers(PAPERS_JSON)
    print(f"  {len(papers)} papers carregados (com titulo registro + titulo S1)")

    json_files = sorted(REFS_DIR.glob("*_refs.json"))
    print(f"\nProcessando {len(json_files)} JSONs de referências...\n")

    total_refs = 0
    total_matches = 0
    summary = []

    for json_path in json_files:
        data = load_json(json_path)
        self_pdf = data.get("meta", {}).get("pdf", "")
        refs = data.get("referencias", [])
        file_matches = 0

        for ref in refs:
            match_pdf, match_score = find_match(ref, papers, json_path.name)

            if match_pdf:
                ref["cita_estudo_aprovado"] = True
                ref["estudo_citado_pdf"] = match_pdf
                ref["match_score"] = match_score
                file_matches += 1
            else:
                ref["cita_estudo_aprovado"] = False
                ref["estudo_citado_pdf"] = None
                ref["match_score"] = None

        save_json(json_path, data)
        total_refs += len(refs)
        total_matches += file_matches

        if file_matches > 0:
            summary.append((json_path.name, len(refs), file_matches))
            print(f"  {json_path.name}: {file_matches}/{len(refs)} matches")

    print(f"\n{'='*60}")
    print(f"RESUMO")
    print(f"{'='*60}")
    print(f"Total de referências processadas: {total_refs}")
    print(f"Total de matches encontrados: {total_matches}")
    print(f"Arquivos com pelo menos 1 match: {len(summary)}/{len(json_files)}")
    print()

    if summary:
        print("Detalhamento dos matches:")
        for name, n_refs, n_matches in sorted(summary, key=lambda x: -x[2]):
            print(f"  {name}: {n_matches}/{n_refs}")


if __name__ == "__main__":
    main()
