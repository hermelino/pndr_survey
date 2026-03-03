#!/usr/bin/env python3
"""Extrai e consolida dados de Incentivos Fiscais SUDAM a partir de PDFs anuais.

Lê os PDFs anuais de incentivos fiscais da SUDAM (2010-2023), extrai as tabelas,
padroniza as colunas e consolida em um único arquivo Excel.

Dois formatos de PDF são tratados:
  - Formato A (2010-2020): "Relação Incentivos Fiscais Redução e Isenção - YYYY.pdf"
    Colunas: EMPRESA, CNPJ/MF, MUNICÍPIO, UF, SETOR, PRODUTO/SERVIÇO,
             ENQUADRAMENTO, PLEITO, MODALIDADE, LAUDO DATA, LAUDO N.º/ANO
  - Formato B (2021-2023): "Planilha - Aprovados YYYY Redução e Reinvestimento.pdf"
    Colunas: Nº, N.º SEI, EMPRESA, CNPJ/MF, MODALIDADE, MUNICÍPIO, UF,
             PRODUTO/SERVIÇO, ENQ.4.212, Nº DO LAUDO, DATA DO LAUDO

Uso:
    python process_sudam_pdfs.py
    python process_sudam_pdfs.py --validate   # Compara contra Merged.xlsx
    python process_sudam_pdfs.py --verbose

Entrada:
    data/external_data/if_sudam/*.pdf

Saída:
    data/external_data/if_sudam/sudam_incentivos_consolidado.xlsx

Referência R: tese/bulding_dataset_R/source_code/if_variables.R (linhas 33-49)
"""

from __future__ import annotations

import argparse
import logging
import re
from pathlib import Path

import pandas as pd
import pdfplumber

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).parent.parent
SUDAM_DIR = PROJECT_ROOT / "data" / "external_data" / "if_sudam"

# Colunas padronizadas do output
OUTPUT_COLUMNS = [
    "EMPRESA",
    "CNPJ",
    "MUNICIPIO",
    "UF",
    "SETOR",
    "PRODUTO_SERVICO",
    "ENQUADRAMENTO",
    "PLEITO",
    "MODALIDADE",
    "DATA_LAUDO",
    "NUM_LAUDO",
    "ANO",
]

# UFs válidas da Amazônia Legal (área de atuação da SUDAM)
VALID_UFS = {"AC", "AM", "AP", "MA", "MT", "PA", "RO", "RR", "TO"}


def extract_year_from_filename(filepath: Path) -> int | None:
    """Extrai o ano do nome do arquivo PDF.

    Args:
        filepath: Caminho do arquivo PDF

    Returns:
        Ano extraído ou None se não encontrado
    """
    match = re.search(r"(\d{4})", filepath.stem)
    if match:
        return int(match.group(1))
    return None


def clean_cnpj(value: str) -> str:
    """Remove formatação do CNPJ, mantendo apenas dígitos.

    Args:
        value: CNPJ com formatação (pontos, barras, hífens)

    Returns:
        CNPJ apenas com dígitos
    """
    if pd.isna(value):
        return ""
    return re.sub(r"[^\d]", "", str(value))


def normalize_text(value: str) -> str:
    """Normaliza texto removendo espaços extras e quebras de linha.

    Args:
        value: Texto bruto

    Returns:
        Texto normalizado
    """
    if pd.isna(value):
        return ""
    return " ".join(str(value).split()).strip()


def extract_format_a(filepath: Path) -> pd.DataFrame:
    """Extrai tabela de PDF no formato A (2010-2020).

    Formato fixo (11 colunas):
        EMPRESA, CNPJ/MF, MUNICÍPIO, UF, SETOR, PRODUTO/SERVIÇO,
        ENQUADRAMENTO, PLEITO, MODALIDADE, LAUDO DATA, LAUDO N.º/ANO

    Empresas com múltiplos produtos aparecem com EMPRESA/CNPJ vazio nas
    linhas subsequentes (forward-fill necessário).

    Args:
        filepath: Caminho do PDF

    Returns:
        DataFrame com dados extraídos e colunas padronizadas
    """
    year = extract_year_from_filename(filepath)
    logger.info(f"Extraindo formato A: {filepath.name} (ano {year})")

    all_rows: list[dict] = []

    with pdfplumber.open(filepath) as pdf:
        for page_num, page in enumerate(pdf.pages):
            tables = page.extract_tables()
            for table in tables:
                if not table:
                    continue

                # Detectar linha de cabeçalho
                header_row_idx = None
                for i, row in enumerate(table):
                    if row and any(
                        cell and "EMPRESA" in str(cell).upper()
                        for cell in row
                        if cell
                    ):
                        header_row_idx = i
                        break

                start_idx = (header_row_idx + 1) if header_row_idx is not None else 0

                for row in table[start_idx:]:
                    if not row or all(cell is None or str(cell).strip() == "" for cell in row):
                        continue

                    cells = [normalize_text(c) if c else "" for c in row]

                    # Pular linhas que parecem ser cabeçalho repetido
                    if cells and any("EMPRESA" in c.upper() for c in cells if c):
                        continue

                    # Formato A: 11 colunas fixas
                    if len(cells) >= 11:
                        record = {
                            "EMPRESA": cells[0],
                            "CNPJ": clean_cnpj(cells[1]),
                            "MUNICIPIO": cells[2],
                            "UF": cells[3],
                            "SETOR": cells[4],
                            "PRODUTO_SERVICO": cells[5],
                            "ENQUADRAMENTO": cells[6],
                            "PLEITO": cells[7],
                            "MODALIDADE": cells[8],
                            "DATA_LAUDO": cells[9],
                            "NUM_LAUDO": cells[10],
                            "ANO": year,
                        }
                        all_rows.append(record)

    df = pd.DataFrame(all_rows)

    if not df.empty:
        # Forward-fill: quando EMPRESA está vazio mas há dados em outras colunas,
        # a empresa é a mesma da linha anterior (múltiplos produtos por empresa)
        ffill_cols = ["EMPRESA", "CNPJ", "MUNICIPIO", "UF", "SETOR"]
        for col in ffill_cols:
            df[col] = df[col].replace("", pd.NA).ffill().fillna("")

    logger.info(f"  -> {len(df)} registros extraídos de {filepath.name}")
    return df


def _find_column_index(header_cells: list[str], patterns: list[str]) -> int | None:
    """Encontra o índice de uma coluna no cabeçalho por padrões de nome.

    Args:
        header_cells: Células do cabeçalho normalizadas
        patterns: Lista de padrões a buscar (case-insensitive, substring match)

    Returns:
        Índice da coluna ou None se não encontrada
    """
    for idx, cell in enumerate(header_cells):
        cell_upper = cell.upper()
        for pattern in patterns:
            if pattern.upper() in cell_upper:
                return idx
    return None


def _build_column_map(header_rows: list[list[str]]) -> dict[str, int | None]:
    """Constrói mapeamento coluna → índice a partir das linhas de cabeçalho.

    Combina múltiplas linhas de cabeçalho (ex: 2022 tem 3 linhas) em uma única
    representação, então busca cada coluna padrão.

    Args:
        header_rows: Uma ou mais linhas de cabeçalho extraídas do PDF

    Returns:
        Dicionário com nomes padronizados → índice da coluna (None se ausente)
    """
    # Combinar linhas de cabeçalho: juntar textos por coluna
    n_cols = max(len(row) for row in header_rows)
    combined = [""] * n_cols
    for row in header_rows:
        for i, cell in enumerate(row):
            if cell and str(cell).strip():
                combined[i] = (combined[i] + " " + normalize_text(cell)).strip()

    logger.debug(f"  Cabeçalho combinado: {combined}")

    return {
        "EMPRESA": _find_column_index(combined, ["EMPRESA"]),
        "CNPJ": _find_column_index(combined, ["CNPJ"]),
        "MODALIDADE": _find_column_index(combined, ["MODALIDADE"]),
        "MUNICIPIO": _find_column_index(combined, ["MUNIC"]),
        "UF": _find_column_index(combined, ["UF"]),
        "PRODUTO_SERVICO": _find_column_index(combined, ["PRODUTO", "SERVI"]),
        "ENQUADRAMENTO": _find_column_index(combined, ["ENQ", "ENQUADRAMENTO"]),
        "NUM_LAUDO": _find_column_index(combined, ["LAUDO N", "N\u00ba DO LAUDO", "N DO LAUDO"]),
        "DATA_LAUDO": _find_column_index(combined, ["DATA DO LAUDO", "DATA DO"]),
    }


def extract_format_b(filepath: Path) -> pd.DataFrame:
    """Extrai tabela de PDF no formato B (2021-2023).

    Usa detecção dinâmica de cabeçalho para lidar com três variantes:
      - 2021: 10 cols (Nº, SEI, EMPRESA, CNPJ, MODALIDADE, MUNIC, UF, PROD, LAUDO, ENQ)
      - 2022: 10 cols com cabeçalho multi-linha (Nº, EMPRESA, CNPJ, MODAL, MUNIC, UF, PROD, ENQ, LAUDO, DATA)
      - 2023: 9 cols (N, PROCESSO, EMPRESA, CNPJ, MUNIC, UF, MODALIDADE, PROD, LAUDO)

    Nenhum formato B possui coluna SETOR.

    Args:
        filepath: Caminho do PDF

    Returns:
        DataFrame com dados extraídos e colunas padronizadas
    """
    year = extract_year_from_filename(filepath)
    logger.info(f"Extraindo formato B: {filepath.name} (ano {year})")

    all_rows: list[dict] = []
    col_map: dict[str, int | None] | None = None

    with pdfplumber.open(filepath) as pdf:
        for page_num, page in enumerate(pdf.pages):
            tables = page.extract_tables()
            for table in tables:
                if not table:
                    continue

                # Detectar linhas de cabeçalho (pode ser multi-linha)
                header_rows: list[list[str]] = []
                data_start_idx = 0

                for i, row in enumerate(table):
                    if not row:
                        continue
                    row_text = " ".join(str(c) for c in row if c)
                    if "EMPRESA" in row_text.upper():
                        # Verificar linhas anteriores (ex: 2022 Row 0 tem ENQ/LAUDO/DATA)
                        for k in range(max(0, i - 2), i):
                            prev_row = table[k]
                            if prev_row and any(c and str(c).strip() for c in prev_row):
                                header_rows.append(prev_row)
                        header_rows.append(row)
                        data_start_idx = i + 1
                        # Verificar se próximas linhas também são cabeçalho
                        for j in range(i + 1, min(i + 4, len(table))):
                            next_row = table[j]
                            if not next_row:
                                continue
                            non_empty = sum(1 for c in next_row if c and str(c).strip())
                            is_header_continuation = all(
                                c is None or str(c).strip() == "" or "LAUDO" in str(c).upper()
                                or "4.212" in str(c)
                                for c in next_row
                            )
                            if is_header_continuation and non_empty <= 3:
                                header_rows.append(next_row)
                                data_start_idx = j + 1
                            else:
                                break
                        break

                # Construir mapa de colunas na primeira página
                if header_rows and col_map is None:
                    col_map = _build_column_map(header_rows)
                    logger.debug(f"  Mapa de colunas: {col_map}")

                if col_map is None:
                    # Sem cabeçalho encontrado (página sem header), usar mapa anterior
                    data_start_idx = 0

                if col_map is None:
                    continue

                emp_idx = col_map["EMPRESA"]
                if emp_idx is None:
                    continue

                for row in table[data_start_idx:]:
                    if not row or all(cell is None or str(cell).strip() == "" for cell in row):
                        continue

                    cells = [normalize_text(c) if c else "" for c in row]

                    # Pular cabeçalhos repetidos e linhas vazias de separação
                    if any("EMPRESA" in c.upper() for c in cells if c):
                        continue

                    # Verificar que a linha tem dados na posição EMPRESA
                    empresa = cells[emp_idx] if emp_idx < len(cells) else ""
                    if not empresa:
                        continue

                    def _get(col_name: str) -> str:
                        idx = col_map.get(col_name)  # type: ignore[union-attr]
                        if idx is not None and idx < len(cells):
                            return cells[idx]
                        return ""

                    record = {
                        "EMPRESA": empresa,
                        "CNPJ": clean_cnpj(_get("CNPJ")),
                        "MODALIDADE": _get("MODALIDADE"),
                        "MUNICIPIO": _get("MUNICIPIO"),
                        "UF": _get("UF"),
                        "PRODUTO_SERVICO": _get("PRODUTO_SERVICO"),
                        "ENQUADRAMENTO": _get("ENQUADRAMENTO"),
                        "NUM_LAUDO": _get("NUM_LAUDO"),
                        "DATA_LAUDO": _get("DATA_LAUDO"),
                        "SETOR": "",  # Formato B não tem SETOR
                        "PLEITO": "Redução",
                        "ANO": year,
                    }
                    all_rows.append(record)

    df = pd.DataFrame(all_rows)
    logger.info(f"  -> {len(df)} registros extraídos de {filepath.name}")
    return df


def process_all_pdfs(sudam_dir: Path) -> pd.DataFrame:
    """Processa todos os PDFs SUDAM no diretório e consolida.

    Args:
        sudam_dir: Diretório contendo os PDFs

    Returns:
        DataFrame consolidado com todos os anos
    """
    frames: list[pd.DataFrame] = []

    # Formato A: 2010-2020
    for year in range(2010, 2021):
        pattern = f"*{year}*.pdf"
        matches = [
            f for f in sudam_dir.glob(pattern)
            if "Merged" not in f.name and "Aprovados" not in f.name
        ]
        if matches:
            df = extract_format_a(matches[0])
            if not df.empty:
                frames.append(df)
        else:
            logger.warning(f"PDF não encontrado para {year} (formato A)")

    # Formato B: 2021-2023
    for year in range(2021, 2024):
        pattern = f"*Aprovados*{year}*.pdf"
        matches = list(sudam_dir.glob(pattern))
        if matches:
            df = extract_format_b(matches[0])
            if not df.empty:
                frames.append(df)
        else:
            # TODO: pendente — obter PDFs de anos faltantes
            logger.warning(f"PDF não encontrado para {year} (formato B)")

    if not frames:
        logger.error("Nenhum PDF processado com sucesso")
        return pd.DataFrame(columns=OUTPUT_COLUMNS)

    consolidated = pd.concat(frames, ignore_index=True)

    # Garantir colunas e ordem
    for col in OUTPUT_COLUMNS:
        if col not in consolidated.columns:
            consolidated[col] = ""
    consolidated = consolidated[OUTPUT_COLUMNS]

    # Limpar registros vazios
    consolidated = consolidated[consolidated["EMPRESA"].str.strip() != ""]

    # Corrigir UF: quando UF contém texto não-UF mas MUNICIPIO tem UF válida,
    # colunas foram deslocadas pelo pdfplumber (ocorre em 2022 com MODALIDADE longa)
    invalid_uf_mask = ~consolidated["UF"].isin(VALID_UFS)
    municipio_is_uf = consolidated["MUNICIPIO"].isin(VALID_UFS)
    shifted = invalid_uf_mask & municipio_is_uf
    if shifted.any():
        n_shifted = shifted.sum()
        logger.warning(f"Corrigindo {n_shifted} registros com colunas deslocadas (UF ↔ MUNICIPIO)")
        # MUNICIPIO na verdade contém a UF; o texto em UF é MODALIDADE
        consolidated.loc[shifted, "MODALIDADE"] = consolidated.loc[shifted, "UF"]
        consolidated.loc[shifted, "UF"] = consolidated.loc[shifted, "MUNICIPIO"]
        consolidated.loc[shifted, "MUNICIPIO"] = ""  # município desconhecido

    # Remover registros com UF inválida restantes (poucos, ex: "-", "ECMIST")
    still_invalid = ~consolidated["UF"].isin(VALID_UFS)
    if still_invalid.any():
        n_invalid = still_invalid.sum()
        logger.warning(f"Removendo {n_invalid} registros com UF inválida")
        consolidated = consolidated[~still_invalid]

    # Ordenar por ano e número do laudo
    consolidated = consolidated.sort_values(["ANO", "NUM_LAUDO"]).reset_index(drop=True)

    logger.info(f"Total consolidado: {len(consolidated)} registros de {consolidated['ANO'].nunique()} anos")
    return consolidated


def validate_against_merged(
    consolidated: pd.DataFrame, merged_path: Path
) -> dict[str, int]:
    """Compara o consolidado extraído dos PDFs contra o Merged.xlsx existente.

    Args:
        consolidated: DataFrame extraído dos PDFs
        merged_path: Caminho do Merged.xlsx de referência

    Returns:
        Dicionário com contagens de validação por ano
    """
    logger.info(f"Validando contra {merged_path.name}...")

    try:
        # Ler sheet principal do Merged.xlsx
        merged_main = pd.read_excel(merged_path, sheet_name="reduções e isenções")
        logger.info(f"  Merged.xlsx 'reduções e isenções': {len(merged_main)} registros")
    except Exception as e:
        logger.warning(f"  Não foi possível ler sheet 'reduções e isenções': {e}")
        merged_main = pd.DataFrame()

    try:
        # Ler sheet Table 15 (dados 2021)
        merged_2021 = pd.read_excel(merged_path, sheet_name="Table 15", skiprows=1)
        logger.info(f"  Merged.xlsx 'Table 15': {len(merged_2021)} registros")
    except Exception as e:
        logger.warning(f"  Não foi possível ler sheet 'Table 15': {e}")
        merged_2021 = pd.DataFrame()

    # Comparar contagens por ano
    pdf_counts = consolidated.groupby("ANO").size().to_dict()

    results = {"pdf_total": len(consolidated)}
    if not merged_main.empty:
        results["merged_main_total"] = len(merged_main)
    if not merged_2021.empty:
        results["merged_2021_total"] = len(merged_2021)

    logger.info("\n  Contagem por ano (PDFs extraídos):")
    for year in sorted(pdf_counts.keys()):
        logger.info(f"    {year}: {pdf_counts[year]} registros")

    return results


def save_consolidated(df: pd.DataFrame, output_path: Path) -> None:
    """Salva o DataFrame consolidado em Excel.

    Args:
        df: DataFrame consolidado
        output_path: Caminho do arquivo de saída
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Garantir CNPJ como string (evitar notação científica no Excel)
    df = df.copy()
    df["CNPJ"] = df["CNPJ"].astype(str)

    df.to_excel(output_path, index=False, sheet_name="consolidado")

    size_kb = output_path.stat().st_size / 1024
    logger.info(f"Arquivo salvo: {output_path} ({size_kb:.1f} KB, {len(df)} registros)")


def main() -> int:
    """Ponto de entrada principal.

    Returns:
        Exit code (0 = sucesso, 1 = erro)
    """
    parser = argparse.ArgumentParser(
        description="Extrai e consolida PDFs de Incentivos Fiscais SUDAM"
    )
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=SUDAM_DIR,
        help="Diretório contendo os PDFs SUDAM",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=SUDAM_DIR / "sudam_incentivos_consolidado.xlsx",
        help="Caminho do arquivo Excel de saída",
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validar contra Merged.xlsx existente",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Logging detalhado"
    )

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s: %(message)s",
    )

    try:
        # Verificar diretório de entrada
        if not args.input_dir.exists():
            raise FileNotFoundError(f"Diretório não encontrado: {args.input_dir}")

        pdf_count = len(list(args.input_dir.glob("*.pdf")))
        logger.info(f"Diretório: {args.input_dir} ({pdf_count} PDFs encontrados)")

        # Processar todos os PDFs
        consolidated = process_all_pdfs(args.input_dir)

        if consolidated.empty:
            logger.error("Nenhum dado extraído dos PDFs")
            return 1

        # Salvar consolidado
        save_consolidated(consolidated, args.output)

        # Validar contra Merged.xlsx se solicitado
        if args.validate:
            merged_path = args.input_dir / "Merged.xlsx"
            if merged_path.exists():
                validate_against_merged(consolidated, merged_path)
            else:
                logger.warning(f"Merged.xlsx não encontrado em {args.input_dir}")

        # Resumo
        logger.info("\nResumo da extração:")
        for year, count in sorted(consolidated.groupby("ANO").size().items()):
            logger.info(f"  {year}: {count} incentivos")
        logger.info(f"  TOTAL: {len(consolidated)} incentivos ({consolidated['ANO'].min()}-{consolidated['ANO'].max()})")

        return 0

    except Exception:
        logger.exception("Erro ao processar PDFs SUDAM")
        return 1


if __name__ == "__main__":
    import sys

    sys.exit(main())
