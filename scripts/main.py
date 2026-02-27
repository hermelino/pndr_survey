"""Ponto de entrada CLI do pipeline pndr_survey.

Comandos:
    search   — Buscar artigos nas bases acadêmicas
    screen   — Filtrar registros (tipo, idioma, PDF) com relatório PRISMA
    analyze  — Analisar PDFs coletados via LLM
    export   — Exportar resultados
    full     — Executar pipeline completo (search + screen + analyze + export)
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import List

from collections import Counter

from src.config import Config, load_config
from src.models import BibRecord, PaperRecord, ScreeningStatus
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
    sp_search.add_argument("--import-scielo", metavar="FILE", help="Importar RIS/CSV do SciELO")
    sp_search.add_argument("--skip-dedup", action="store_true", help="Pular deduplicação")
    sp_search.add_argument("--dry-run", action="store_true", help="Mostrar queries sem executar")

    # --- screen ---
    sp_screen = sub.add_parser("screen", help="Filtrar registros (tipo, idioma, PDF)")
    sp_screen.add_argument(
        "--title-filter", action="store_true",
        help="Ativar filtro de relevância por título (step 4). "
             "Por padrão, relevância é avaliada pelo LLM.",
    )
    sp_screen.add_argument(
        "--report", action="store_true",
        help="Apenas exibir relatório PRISMA (sem modificar registros)",
    )
    sp_screen.add_argument(
        "--input-json", metavar="FILE",
        help="Carregar registros de JSON anterior",
    )

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
    """Fase 1: importação, deduplicação e salvamento."""
    from src.dedup.deduplicator import deduplicate
    from src.importer import import_from_file

    all_records: List[BibRecord] = []

    # --- Dry-run: mostra queries dos arquivos de keywords ---
    if args.dry_run:
        keywords_dir = SCRIPT_DIR / config.search.keywords_dir
        for db_name in (args.databases or config.search.databases):
            kw_file = keywords_dir / f"{db_name}.txt"
            if kw_file.exists():
                print(f"\n{'='*60}")
                print(f"Base: {db_name}")
                print(f"Query: {kw_file.read_text(encoding='utf-8').strip()}")
                print(f"{'='*60}")
        return []

    # --- Importar arquivos ---
    import_map = {
        "econpapers": args.import_econpapers,
        "capes": args.import_capes,
        "scopus": args.import_scopus,
        "anpec": args.import_anpec,
        "scielo": args.import_scielo,
    }
    for db_name, filepath in import_map.items():
        if filepath:
            imported = import_from_file(filepath, source_db=db_name)
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
        for rec in duplicates:
            rec.screening_status = ScreeningStatus.EXCLUDED_DUPLICATE
        all_records = unique + duplicates
        logger.info("Após deduplicação: %d únicos, %d duplicatas", len(unique), len(duplicates))

    # --- Salvar BibRecords para uso posterior ---
    output_base = SCRIPT_DIR / config.output.directory
    output_base.mkdir(parents=True, exist_ok=True)
    _save_bibs_to_json(all_records, output_base / "bib_records.json")

    return all_records


def cmd_screen(
    config: Config,
    args: argparse.Namespace,
    bib_records: List[BibRecord] | None = None,
) -> List[BibRecord]:
    """Fase 1.5: triagem pré-LLM (tipo+idioma, PDF) do PRISMA."""
    from src.screening.screener import run_screening

    # Carregar registros se necessário
    if bib_records is None:
        input_json = getattr(args, "input_json", None)
        if input_json:
            bib_records = _load_bibs_from_json(input_json)
        else:
            logger.error(
                "Sem registros para filtrar. "
                "Use --input-json ou execute 'search' antes."
            )
            return []

    # Modo report: apenas imprimir contagens
    if getattr(args, "report", False):
        _print_prisma_report(bib_records)
        return bib_records

    # Filtrar apenas registros não-duplicatas e pendentes
    to_screen = [
        r for r in bib_records
        if not r.is_duplicate and r.screening_status == ScreeningStatus.PENDING
    ]
    logger.info("Registros para triagem: %d (de %d total)", len(to_screen), len(bib_records))

    # Executar screening (modifica records in-place)
    title_filter = getattr(args, "title_filter", False)
    run_screening(
        to_screen, config.screening,
        include_title_filter=title_filter,
    )

    # Salvar resultado
    output_base = SCRIPT_DIR / config.output.directory
    output_base.mkdir(parents=True, exist_ok=True)
    output_path = output_base / "bib_screened.json"
    _save_bibs_to_json(bib_records, output_path)

    # Imprimir relatório
    _print_prisma_report(bib_records)

    return bib_records


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
    """Pipeline completo: search → screen → analyze → export."""
    logger.info("Iniciando pipeline completo")

    # Fase 1: Busca
    args.databases = None
    args.import_econpapers = None
    args.import_capes = None
    args.import_scopus = None
    args.import_anpec = None
    args.skip_dedup = False
    args.dry_run = False
    bib_records = cmd_search(config, args)

    # Fase 1.5: Triagem
    args.title_filter = False
    args.report = False
    args.input_json = None
    bib_records = cmd_screen(config, args, bib_records=bib_records)

    # Fase 2: Análise (apenas registros incluídos)
    included = [r for r in bib_records if r.screening_status == ScreeningStatus.INCLUDED]
    logger.info("Registros incluídos para análise: %d", len(included))
    args.stage = "all"
    args.max_papers = None
    args.input_dir = None
    paper_records = cmd_analyze(config, args, bib_records=included)

    # Fase 3: Exportação
    args.formats = None
    args.input_json = None
    output_dir = cmd_export(config, args, paper_records=paper_records)

    # Resumo PRISMA completo
    _print_prisma_report(bib_records, paper_records, output_dir)


# =============================================================================
# Helpers
# =============================================================================



def _save_bibs_to_json(records: List[BibRecord], path: Path) -> None:
    """Salva BibRecords em JSON para persistência entre comandos."""
    data = []
    for bib in records:
        row = {
            "source_db": bib.source_db,
            "source_id": bib.source_id,
            "doi": bib.doi or "",
            "title": bib.title,
            "authors": "; ".join(bib.authors),
            "year": bib.year,
            "journal": bib.journal or "",
            "volume": bib.volume or "",
            "issue": bib.issue or "",
            "pages": bib.pages or "",
            "abstract": bib.abstract or "",
            "keywords": "; ".join(bib.keywords),
            "url": bib.url or "",
            "pdf_url": bib.pdf_url or "",
            "language": bib.language or "",
            "publication_type": bib.publication_type or "",
            "matched_instruments": "; ".join(bib.matched_instruments),
            "is_duplicate": bib.is_duplicate,
            "duplicate_of": bib.duplicate_of or "",
            "screening_status": bib.screening_status.value,
            "exclusion_reason": bib.exclusion_reason or "",
        }
        data.append(row)

    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    logger.info("Salvos %d registros em %s", len(data), path)


def _load_bibs_from_json(json_path: str) -> List[BibRecord]:
    """Carrega BibRecords de JSON salvo anteriormente."""
    path = Path(json_path)
    if not path.exists():
        logger.error("Arquivo não encontrado: %s", path)
        return []

    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    records = []
    for row in data:
        # Restaurar screening_status como enum
        status_str = row.get("screening_status", "pending")
        try:
            status = ScreeningStatus(status_str)
        except ValueError:
            status = ScreeningStatus.PENDING

        bib = BibRecord(
            source_db=row.get("source_db", ""),
            source_id=row.get("source_id", ""),
            doi=row.get("doi") or None,
            title=row.get("title", ""),
            authors=row.get("authors", "").split("; ") if row.get("authors") else [],
            year=row.get("year"),
            journal=row.get("journal") or None,
            volume=row.get("volume") or None,
            issue=row.get("issue") or None,
            pages=row.get("pages") or None,
            abstract=row.get("abstract") or None,
            keywords=row.get("keywords", "").split("; ") if row.get("keywords") else [],
            url=row.get("url") or None,
            pdf_url=row.get("pdf_url") or None,
            language=row.get("language") or None,
            publication_type=row.get("publication_type") or None,
            matched_instruments=row.get("matched_instruments", "").split("; ") if row.get("matched_instruments") else [],
            is_duplicate=row.get("is_duplicate", False),
            duplicate_of=row.get("duplicate_of") or None,
            screening_status=status,
            exclusion_reason=row.get("exclusion_reason") or None,
        )
        records.append(bib)

    logger.info("Carregados %d BibRecords de %s", len(records), path)
    return records


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
        # Restaurar screening_status como enum
        status_str = row.get("screening_status", "pending")
        try:
            status = ScreeningStatus(status_str)
        except ValueError:
            status = ScreeningStatus.PENDING

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
            screening_status=status,
            exclusion_reason=row.get("exclusion_reason") or None,
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


def _print_prisma_report(
    bib_records: List[BibRecord],
    paper_records: List[PaperRecord] | None = None,
    output_dir: Path | None = None,
) -> None:
    """Imprime relatório PRISMA com contagens de cada etapa de triagem."""
    total = len(bib_records)
    counts = Counter(r.screening_status for r in bib_records)
    duplicates = sum(1 for r in bib_records if r.is_duplicate)
    unique = total - duplicates

    n_doctype = counts.get(ScreeningStatus.EXCLUDED_DOCTYPE, 0)
    n_language = counts.get(ScreeningStatus.EXCLUDED_LANGUAGE, 0)
    n_relevance = counts.get(ScreeningStatus.EXCLUDED_RELEVANCE, 0)
    n_econometrics = counts.get(ScreeningStatus.EXCLUDED_NO_ECONOMETRICS, 0)
    n_awaiting = counts.get(ScreeningStatus.AWAITING_PDF, 0)
    n_included = counts.get(ScreeningStatus.INCLUDED, 0)

    print(f"\n{'='*55}")
    print("PRISMA FLOW — pndr_survey")
    print(f"{'='*55}")
    print()
    print(f"  1. IDENTIFICAÇÃO")
    print(f"     Registros das bases:           {total}")
    print()
    print(f"  2. DEDUPLICAÇÃO")
    print(f"     Duplicatas removidas:          -{duplicates}")
    print(f"     Registros únicos:               {unique}")
    print()
    print(f"  3. TIPO DOCUMENTAL + IDIOMA")
    print(f"     Excluídos (tipo):              -{n_doctype}")
    print(f"     Excluídos (idioma):            -{n_language}")

    # Step 4 (filtro de título) — mostrar apenas se foi usado
    if n_relevance > 0:
        print()
        print(f"     FILTRO DE TÍTULO (opcional)")
        print(f"     Excluídos (fora do escopo):    -{n_relevance}")

    print()
    print(f"     DISPONIBILIDADE PDF")
    print(f"     Aguardando texto completo:      {n_awaiting}")
    print(f"     Com texto completo:             {n_included}")

    if paper_records is not None:
        analyzed = sum(1 for p in paper_records if p.stage_1 is not None)
        with_s2 = sum(1 for p in paper_records if p.stage_2 is not None)
        with_s3 = sum(1 for p in paper_records if p.stage_3 is not None)

        print()
        print(f"  4. ANÁLISE LLM (Stage 1)")
        print(f"     Papers analisados:              {analyzed}")
        print(f"     Excluídos (sem relevância):     -{n_relevance}")
        print(f"     Excluídos (sem econometria):    -{n_econometrics}")
        print()
        print(f"     INCLUÍDOS")
        print(f"     Estudos para Stages 2-3:        {n_included}")
        print(f"     Com metodologia (Stage 2):      {with_s2}")
        print(f"     Com resultados (Stage 3):       {with_s3}")
    else:
        print()
        print(f"     Registros para análise LLM:     {n_included}")

    if output_dir:
        print()
        print(f"     Saída: {output_dir}")

    print(f"\n{'='*55}\n")


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
    elif args.command == "screen":
        cmd_screen(config, args)
    elif args.command == "analyze":
        cmd_analyze(config, args)
    elif args.command == "export":
        cmd_export(config, args)
    elif args.command == "full":
        cmd_full(config, args)


if __name__ == "__main__":
    main()
