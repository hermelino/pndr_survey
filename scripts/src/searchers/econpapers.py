"""Buscador semi-automático para EconPapers/RePEc.

O EconPapers migrou para Solr com renderização via JavaScript,
inviabilizando scraping direto. Este módulo gera queries formatadas e
instruções para busca manual, e importa resultados via RIS ou CSV.

Para enriquecimento de metadados, visita páginas individuais dos papers
e extrai Dublin Core meta tags (dc.Title, dc.Creator, dc.Date, etc.).
"""

from __future__ import annotations

import logging
import re
import time
from typing import List, Optional
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from src.models import BibRecord
from src.searchers.base import BaseSearcher, _extract_year

logger = logging.getLogger("pndr_survey")

BASE_URL = "https://econpapers.repec.org"
RATE_LIMIT = 2.0  # segundos entre requisições


class EconPapersSearcher(BaseSearcher):
    """Busca semi-automática no EconPapers/RePEc."""

    name = "econpapers"

    def __init__(self, keywords: str, *, max_results: int = 1000):
        super().__init__(keywords, max_results=max_results)
        self.session = requests.Session()
        self.session.verify = _ssl_verify()
        self.session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 Chrome/120.0 Safari/537.36"
            )
        })

    def build_query(self) -> str:
        """Retorna a query no formato aceito pelo EconPapers."""
        return self.keywords

    def search(self) -> int:
        """EconPapers usa Solr com renderização JavaScript.

        Busca automática via scraping não é confiável.
        Use save_query_instructions() + import_from_file().

        Returns:
            0 (sempre — resultados vêm via importação).
        """
        logger.info(
            "EconPapers requer busca manual (Solr + JavaScript). "
            "Use save_query_instructions() para gerar o arquivo de instruções."
        )
        return 0

    def fetch_records(self) -> List[BibRecord]:
        """Retorna registros importados."""
        return self.records

    def enrich_record(self, record: BibRecord) -> BibRecord:
        """Visita a página individual do paper para extrair metadados extras.

        Usa Dublin Core meta tags (dc.Title, dc.Creator, dc.Date, etc.)
        que são mais confiáveis que exports manuais.

        Args:
            record: BibRecord com pelo menos url preenchido.

        Returns:
            BibRecord enriquecido com abstract, autores, DOI, pdf_url.
        """
        if not record.url:
            return record

        try:
            resp = self.session.get(record.url, timeout=30)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.content, "html.parser")

            # Dublin Core meta tags
            record.title = _meta(soup, "dc.Title") or record.title
            record.year = _extract_year(_meta(soup, "dc.Date")) or record.year
            record.abstract = _meta(soup, "description") or record.abstract

            dc_creators = soup.find_all("meta", attrs={"name": "dc.Creator"})
            if dc_creators:
                record.authors = [
                    m.get("content", "").strip()
                    for m in dc_creators
                    if m.get("content")
                ]

            # PDF links
            pdf_url = _find_pdf_link(soup, record.url)
            if pdf_url:
                record.pdf_url = pdf_url

            # RePEc handle
            handle = _extract_handle(record.url)
            if handle:
                record.source_id = handle

        except requests.RequestException as e:
            logger.warning(f"Erro ao enriquecer {record.url}: {e}")

        return record

    def enrich_batch(self, records: Optional[List[BibRecord]] = None) -> List[BibRecord]:
        """Enriquece todos os registros visitando páginas individuais.

        Args:
            records: Lista de registros (default: self.records).

        Returns:
            Lista de registros enriquecidos.
        """
        target = records if records is not None else self.records
        logger.info(f"Enriquecendo {len(target)} registros do EconPapers...")

        for i, record in enumerate(target):
            self.enrich_record(record)
            if (i + 1) % 10 == 0:
                logger.info(f"Enriquecidos {i + 1}/{len(target)} registros")
            time.sleep(RATE_LIMIT / 2)

        enriched_with_abstract = sum(1 for r in target if r.abstract)
        enriched_with_pdf = sum(1 for r in target if r.pdf_url)
        logger.info(
            f"Enriquecimento concluído: {enriched_with_abstract} com abstract, "
            f"{enriched_with_pdf} com PDF"
        )
        return target

    def _build_instructions(self, query: str) -> str:
        """Gera instruções detalhadas para busca no EconPapers."""
        search_url = f"{BASE_URL}/scripts/search.pf"

        return (
            "=" * 70 + "\n"
            "BUSCA NO ECONPAPERS (RePEc)\n"
            "=" * 70 + "\n\n"
            f"Query:\n{query}\n\n"
            "--- Instruções ---\n\n"
            f"1. Acesse: {search_url}\n"
            "2. Cole a query no campo 'Free text search'\n"
            "3. Marque: Working Papers, Journal Articles, Books and Chapters\n"
            "4. Clique em 'Search!'\n\n"
            "--- Exportar resultados ---\n\n"
            "EconPapers não tem botão de exportação direta.\n"
            "Opções para coletar os resultados:\n\n"
            "  Opção A — Zotero Connector (recomendado):\n"
            "    1. Instale a extensão Zotero Connector no navegador\n"
            "    2. Na página de resultados, clique no ícone do Zotero\n"
            "    3. Salve todos os registros em uma coleção\n"
            "    4. No Zotero, exporte a coleção como RIS\n"
            "    5. Importe com:\n"
            "       python main.py search --import-econpapers <arquivo.ris>\n\n"
            "  Opção B — Copiar URLs e enriquecer:\n"
            "    1. Copie as URLs dos artigos encontrados\n"
            "    2. Crie um CSV com coluna 'url'\n"
            "    3. Importe e use enrich_batch() para extrair metadados\n\n"
            "--- Busca alternativa no IDEAS ---\n\n"
            "O IDEAS (https://ideas.repec.org/) indexa o mesmo conteúdo\n"
            "e pode ser mais fácil para exportação via Zotero.\n"
        )


# --- Utilitários ---


def _meta(soup: BeautifulSoup, name: str) -> Optional[str]:
    """Extrai conteúdo de uma meta tag pelo atributo name."""
    tag = soup.find("meta", attrs={"name": name})
    if tag:
        content = tag.get("content", "").strip()
        return content if content else None
    return None


def _find_pdf_link(soup: BeautifulSoup, base_url: str) -> Optional[str]:
    """Encontra link para PDF na página individual do paper."""
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.endswith(".pdf"):
            return urljoin(base_url, href)
    return None


def _extract_handle(url: str) -> Optional[str]:
    """Extrai handle RePEc da URL do EconPapers."""
    match = re.search(r"/paper/([^/]+)/([^/]+)/([^/.]+)", url)
    if match:
        return f"RePEc:{match.group(1)}:{match.group(2)}:{match.group(3)}"
    return None


def _ssl_verify() -> str | bool:
    """Retorna caminho do bundle SSL ou False como fallback.

    No Windows, o bundle padrão do Python pode não conter os certificados
    necessários. Testa conexão real e desabilita verificação se necessário.
    """
    try:
        import certifi
        requests.head(BASE_URL, timeout=5, verify=certifi.where())
        return certifi.where()
    except Exception:
        pass

    try:
        requests.head(BASE_URL, timeout=5)
        return True
    except requests.exceptions.SSLError:
        logger.warning(
            "Certificado SSL não pôde ser verificado para %s. "
            "Continuando sem verificação SSL.",
            BASE_URL,
        )
        return False
