"""Ponto de entrada CLI do pipeline pndr_survey.

Comandos:
    search   — Buscar artigos nas bases acadêmicas
    analyze  — Analisar PDFs coletados via LLM
    export   — Exportar resultados
    full     — Executar pipeline completo (search + analyze + export)
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import List

from src.config import Config, load_config
from src.models import BibRecord, PaperRecord
from src.utils.logger import setup_logging

logger = logging.getLogger("pndr_survey")

SCRIPT_DIR = Path(__file__).parent


# =============================================================================
# CLI
# =============================================================================


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="main.py",
        description="Pipeline de revisão sistemática sobre PNDR",
    )
    parser.add_argument(
        "--config", default="config.yaml",
        help="Arquivo de configuração YAML (default: config.yaml)",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true",
        help="Logging DEBUG no console",
    )
    parser.add_argument(
        "--output-dir",
        help="Diretório de saída (override config)",
    )

    sub = parser.add_subparsers(dest="command", help="Comando a executar")

    # --- search ---
    sp_search = sub.add_parser("search", help="Buscar artigos nas bases acadêmicas")
    sp_search.add_argument(
        "--databases", nargs="+",
        help="Bases para buscar (default: todas do config)",
    )
    sp_search.add_argument("--import-econpapers", metavar="FILE", help="Importar RIS/CSV do EconPapers")
    sp_search.add_argument("--import-capes", metavar="FILE", help="Importar RIS/CSV do CAPES")
    sp_search.add_argument("--import-scopus", metavar="FILE", help="Importar RIS/CSV do Scopus")
    sp_search.add_argument("--import-anpec", metavar="FILE", help="Importar Excel/RIS/CSV da ANPEC")
    sp_search.add_argument("--skip-dedup", action="store_true", help="Pular deduplicação")
    sp_search.add_argument("--skip-download", action="store_true", help="Não baixar PDFs")
    sp_search.add_argument("--dry-run", action="store_true", help="Mostrar queries sem executar")

    # --- analyze ---
    sp_analyze = sub.add_parser("analyze", help="Analisar PDFs coletados via LLM")
    sp_analyze.add_argument(
        "--stage", choices=["1", "2", "3", "all"], default="all",
        help="Etapa da análise (default: all)",
    )
    sp_analyze.add_argument("--max-papers", type=int, help="Limitar número de papers")
    sp_analyze.add_argument("--input-dir", help="Diretório com PDFs (override config)")

    # --- export ---
    sp_export = sub.add_parser("export", help="Exportar resultados")
    sp_export.add_argument(
        "--formats", nargs="+", choices=["excel", "csv", "ris", "json"],
        help="Formatos de saída (default: todos do config)",
    )
    sp_export.add_argument("--input-json", help="Arquivo JSON com resultados anteriores")

    # --- full ---
    sub.add_parser("full", help="Executar pipeline completo")

    return parser


# =============================================================================
# Comandos
# =============================================================================


def cmd_search(config: Config, args: argparse.Namespace) -> List[BibRecord]:
    """Fase 1: busca, importação, deduplicação e download."""
    from src.dedup.deduplicator import deduplicate
    from src.utils.downloader import download_pdfs

    databases = args.databases or config.search.databases
    keywords_dir = SCRIPT_DIR / config.search.keywords_dir
    all_records: List[BibRecord] = []

    # --- Gerar queries / buscar ---
    for db_name in databases:
        searcher = _create_searcher(db_name, keywords_dir)
        if searcher is None:
            continue

        if args.dry_run:
            query = searcher.build_query()
            print(f"\n{'='*60}")
            print(f"Base: {db_name}")
            print(f"Query: {query}")
            print(f"{'='*60}")
            continue

        count = searcher.search()
        records = searcher.fetch_records()
        all_records.extend(records)
        logger.info("%s: %d resultados (%d registros)", db_name, count, len(records))

    if args.dry_run:
        return []

    # --- Importar arquivos manuais ---
    import_map = {
        "econpapers": args.import_econpapers,
        "capes": args.import_capes,
        "scopus": args.import_scopus,
        "anpec": args.import_anpec,
    }
    for db_name, filepath in import_map.items():
        if filepath:
            searcher = _create_searcher(db_name, keywords_dir)
            if searcher:
                imported = searcher.import_from_file(filepath)
                all_records.extend(imported)
                logger.info("Importados %d registros de %s", len(imported), filepath)

    if not all_records:
        logger.warning("Nenhum registro coletado.")
        return []

    logger.info("Total de registros coletados: %d", len(all_records))

    # --- Deduplicar ---
    if not args.skip_dedup:
        unique, duplicates = deduplicate(
            all_records, fuzzy_threshold=config.dedup.fuzzy_threshold
        )
        all_records = unique
        logger.info("Após deduplicação: %d únicos, %d duplicatas", len(unique), len(duplicates))

    # --- Download PDFs ---
    if not args.skip_download:
        papers_dir = SCRIPT_DIR / config.paths.papers_dir
        ok, fail = download_pdfs(all_records, papers_dir)
        logger.info("Download: %d ok, %d falhas", ok, fail)

    return all_records


def cmd_analyze(
    config: Config,
    args: argparse.Namespace,
    bib_records: List[BibRecord] | None = None,
) -> List[PaperRecord]:
    """Fase 2: extração de texto e análise LLM."""
    from src.analyzers.gemini_analyzer import GeminiAnalyzer
    from src.extractors.pdf_extractor import PdfExtractor

    papers_dir = Path(args.input_dir) if hasattr(args, "input_dir") and args.input_dir else SCRIPT_DIR / config.paths.papers_dir
    questionnaires_dir = SCRIPT_DIR / config.paths.questionnaires_dir

    # --- Extrair texto dos PDFs ---
    extractor = PdfExtractor(max_chars=config.llm.max_tokens_input)
    paper_records, errors = extractor.extract_batch(
        papers_dir, bib_records or []
    )

    if errors:
        logger.warning("Erros na extração: %d PDFs com problemas", len(errors))

    if not paper_records:
        logger.warning("Nenhum PDF extraído.")
        return []

    # Limitar se pedido
    if hasattr(args, "max_papers") and args.max_papers:
        paper_records = paper_records[:args.max_papers]
        logger.info("Limitado a %d papers", len(paper_records))

    # --- Análise LLM ---
    analyzer = GeminiAnalyzer(
        api_key=config.llm.api_key,
        model=config.llm.model,
        temperature=config.llm.temperature,
        max_tokens_input=config.llm.max_tokens_input,
        rate_limit_seconds=config.llm.rate_limit_seconds,
    )

    stage = getattr(args, "stage", "all")
    if stage == "all":
        analyzer.analyze_pipeline(paper_records, str(questionnaires_dir))
    else:
        from src.analyzers.base import load_questionnaire
        stage_files = {
            "1": "stage_1_screening.json",
            "2": "stage_2_methods.json",
            "3": "stage_3_results.json",
        }
        q = load_questionnaire(questionnaires_dir / stage_files[stage])
        analyzer.analyze_batch(paper_records, q)

    return paper_records


def cmd_export(
    config: Config,
    args: argparse.Namespace,
    paper_records: List[PaperRecord] | None = None,
    output_dir: Path | None = None,
) -> Path:
    """Exporta resultados nos formatos configurados."""
    from src.exporters.csv_exporter import export_csv
    from src.exporters.excel_exporter import export_excel
    from src.exporters.json_exporter import export_json
    from src.exporters.ris_exporter import export_ris

    # Carregar de JSON anterior se fornecido
    if paper_records is None and hasattr(args, "input_json") and args.input_json:
        paper_records = _load_papers_from_json(args.input_json)

    if not paper_records:
        logger.warning("Nenhum resultado para exportar.")
        return Path(".")

    # Diretório de saída
    if output_dir is None:
        base = Path(args.output_dir) if args.output_dir else SCRIPT_DIR / config.output.directory
        if config.output.timestamp:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_dir = base / ts
        else:
            output_dir = base
    output_dir.mkdir(parents=True, exist_ok=True)

    formats = (
        args.formats if hasattr(args, "formats") and args.formats
        else config.output.formats
    )

    exporters = {
        "excel": lambda: export_excel(paper_records, output_dir / "results.xlsx"),
        "csv": lambda: export_csv(paper_records, output_dir / "results.csv"),
        "ris": lambda: export_ris(paper_records, output_dir / "results.ris"),
        "json": lambda: export_json(paper_records, output_dir / "results.json"),
    }

    for fmt in formats:
        if fmt in exporters:
            exporters[fmt]()

    logger.info("Resultados exportados em: %s", output_dir)
    return output_dir


def cmd_full(config: Config, args: argparse.Namespace) -> None:
    """Pipeline completo: search → analyze → export."""
    logger.info("Iniciando pipeline completo")

    # Fase 1: Busca
    args.databases = None
    args.import_econpapers = None
    args.import_capes = None
    args.import_scopus = None
    args.import_anpec = None
    args.skip_dedup = False
    args.skip_download = False
    args.dry_run = False
    bib_records = cmd_search(config, args)

    # Fase 2: Análise
    args.stage = "all"
    args.max_papers = None
    args.input_dir = None
    paper_records = cmd_analyze(config, args, bib_records=bib_records)

    # Fase 3: Exportação
    args.formats = None
    args.input_json = None
    output_dir = cmd_export(config, args, paper_records=paper_records)

    # Resumo
    _print_summary(paper_records, output_dir)


# =============================================================================
# Helpers
# =============================================================================


def _create_searcher(db_name: str, keywords_dir: Path):
    """Cria instância do searcher para a base especificada."""
    from src.searchers.anpec import ANPECSearcher
    from src.searchers.capes import CapesSearcher
    from src.searchers.econpapers import EconPapersSearcher
    from src.searchers.scopus import ScopusSearcher

    kw_file = keywords_dir / f"{db_name}.txt"
    if not kw_file.exists():
        logger.warning("Keywords não encontrado: %s", kw_file)
        return None

    keywords = kw_file.read_text(encoding="utf-8").strip()

    searcher_map = {
        "econpapers": EconPapersSearcher,
        "capes": CapesSearcher,
        "scopus": ScopusSearcher,
        "anpec": ANPECSearcher,
    }

    cls = searcher_map.get(db_name)
    if cls is None:
        logger.warning("Base desconhecida: %s", db_name)
        return None

    return cls(keywords)


def _load_papers_from_json(json_path: str) -> List[PaperRecord]:
    """Carrega PaperRecords de JSON exportado anteriormente."""
    path = Path(json_path)
    if not path.exists():
        logger.error("Arquivo não encontrado: %s", path)
        return []

    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    papers = []
    for row in data:
        bib = BibRecord(
            source_db=row.get("source_db", ""),
            source_id=row.get("source_id", ""),
            doi=row.get("doi") or None,
            title=row.get("title", ""),
            authors=row.get("authors", "").split("; ") if row.get("authors") else [],
            year=row.get("year"),
            journal=row.get("journal") or None,
            abstract=row.get("abstract") or None,
            url=row.get("url") or None,
            pdf_url=row.get("pdf_url") or None,
        )
        paper = PaperRecord(
            bib=bib,
            pdf_path=row.get("pdf_path") or None,
            file_hash=row.get("file_hash") or None,
            text_length=row.get("text_length", 0),
            is_empirical=row.get("is_empirical"),
            pndr_instrument=row.get("pndr_instrument") or None,
            model_used=row.get("model_used") or None,
        )
        # Restaurar stages
        for stage_num in (1, 2, 3):
            prefix = f"s{stage_num}_"
            stage_data = {
                k[len(prefix):]: v for k, v in row.items() if k.startswith(prefix)
            }
            if stage_data:
                setattr(paper, f"stage_{stage_num}", stage_data)

        papers.append(paper)

    logger.info("Carregados %d papers de %s", len(papers), path)
    return papers


def _print_summary(papers: List[PaperRecord], output_dir: Path) -> None:
    """Imprime resumo PRISMA-like do pipeline."""
    total = len(papers)
    with_text = sum(1 for p in papers if p.text_length > 0)
    analyzed = sum(1 for p in papers if p.stage_1 is not None)
    empirical = sum(1 for p in papers if p.is_empirical)
    with_s2 = sum(1 for p in papers if p.stage_2 is not None)
    with_s3 = sum(1 for p in papers if p.stage_3 is not None)

    print(f"\n{'='*50}")
    print("RESUMO DO PIPELINE")
    print(f"{'='*50}")
    print(f"  PDFs processados:        {total}")
    print(f"  Com texto extraido:      {with_text}")
    print(f"  Analisados (Stage 1):    {analyzed}")
    print(f"  Estudos empiricos:       {empirical}")
    print(f"  Metodologia (Stage 2):   {with_s2}")
    print(f"  Resultados (Stage 3):    {with_s3}")
    print(f"  Saida:                   {output_dir}")
    print(f"{'='*50}\n")


# =============================================================================
# Entry point
# =============================================================================


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    # Logging
    log_level = "DEBUG" if args.verbose else "INFO"
    setup_logging(console_level=log_level)

    # Config
    config_path = SCRIPT_DIR / args.config
    try:
        config = load_config(config_path)
    except (FileNotFoundError, ValueError) as e:
        logger.error(str(e))
        sys.exit(1)

    # Dispatch
    if args.command == "search":
        cmd_search(config, args)
    elif args.command == "analyze":
        cmd_analyze(config, args)
    elif args.command == "export":
        cmd_export(config, args)
    elif args.command == "full":
        cmd_full(config, args)


if __name__ == "__main__":
    main()
