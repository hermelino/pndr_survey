"""Modelos de dados centrais do pipeline pndr_survey.

BibRecord: metadados bibliográficos (fase de busca).
PaperRecord: resultado da análise LLM (fase de análise).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class BibRecord:
    """Registro bibliográfico normalizado entre bases acadêmicas.

    Cada base (EconPapers, Google Scholar, CAPES, Scopus) produz BibRecords
    com o mesmo esquema, permitindo deduplicação e exportação unificadas.
    """

    # --- Identidade ---
    source_db: str          # "econpapers", "google_scholar", "capes", "scopus"
    source_id: str          # ID na base de origem (URL, DOI, handle)
    doi: Optional[str] = None

    # --- Metadados bibliográficos ---
    title: str = ""
    authors: List[str] = field(default_factory=list)
    year: Optional[int] = None
    journal: Optional[str] = None
    volume: Optional[str] = None
    issue: Optional[str] = None
    pages: Optional[str] = None

    # --- Conteúdo ---
    abstract: Optional[str] = None
    keywords: List[str] = field(default_factory=list)
    url: Optional[str] = None
    pdf_url: Optional[str] = None
    language: Optional[str] = None
    publication_type: Optional[str] = None  # "article", "working_paper", "book_chapter"

    # --- Classificação temática ---
    matched_instruments: List[str] = field(default_factory=list)
    matched_keywords: List[str] = field(default_factory=list)

    # --- Deduplicação ---
    is_duplicate: bool = False
    duplicate_of: Optional[str] = None  # source_id do registro mantido

    def completeness_score(self) -> int:
        """Pontuação heurística para escolher qual duplicata manter.

        Registros com mais metadados preenchidos recebem pontuação maior.
        Usado pelo deduplicador para manter o registro mais completo.
        """
        score = 0
        if self.doi:
            score += 3
        if self.title:
            score += 1
        if self.authors:
            score += 1
        if self.abstract:
            score += 3
        if self.year:
            score += 1
        if self.journal:
            score += 1
        if self.keywords:
            score += 1
        if self.pdf_url:
            score += 2
        if self.url:
            score += 1
        return score

    @property
    def first_author(self) -> str:
        """Primeiro autor ou string vazia."""
        return self.authors[0] if self.authors else ""

    @property
    def citation_key(self) -> str:
        """Chave curta para identificação: 'sobrenome_ano'."""
        surname = self.first_author.split(",")[0].split()[-1] if self.first_author else "unknown"
        return f"{surname}_{self.year or 'nd'}"


# --- Prioridade de fontes para deduplicação ---
SOURCE_PRIORITY = {
    "scopus": 1,
    "econpapers": 2,
    "google_scholar": 3,
    "capes": 4,
}


@dataclass
class PaperRecord:
    """Resultado da análise LLM de um artigo.

    Vinculado a um BibRecord (metadados bibliográficos) e enriquecido
    com informações extraídas do PDF via Gemini.
    """

    # --- Vínculo com BibRecord ---
    bib: BibRecord
    pdf_path: Optional[str] = None
    file_hash: Optional[str] = None  # SHA-256 do PDF

    # --- Conteúdo extraído do PDF ---
    text_length: int = 0
    text_preview: str = ""  # Primeiros 500 caracteres

    # --- Análise LLM (3 estágios) ---
    stage_1: Optional[Dict] = None  # Triagem: é estudo empírico sobre PNDR?
    stage_2: Optional[Dict] = None  # Metodologia: métodos, variáveis, período
    stage_3: Optional[Dict] = None  # Resultados: instrumentos, efeitos, conclusões

    # --- Classificação derivada da análise ---
    is_empirical: Optional[bool] = None
    pndr_instrument: Optional[str] = None   # FNE, FNO, FCO, FDNE, etc.
    econometric_method: Optional[str] = None
    time_period: Optional[str] = None
    geographic_scope: Optional[str] = None

    # --- Metadados de processamento ---
    analyzed_at: Optional[str] = None
    model_used: Optional[str] = None
    processing_errors: List[str] = field(default_factory=list)

    @property
    def is_analyzed(self) -> bool:
        """Verdadeiro se pelo menos o Stage 1 foi executado."""
        return self.stage_1 is not None

    @property
    def passed_screening(self) -> bool:
        """Verdadeiro se passou na triagem (Stage 1) como estudo empírico."""
        return self.is_empirical is True
