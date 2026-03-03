#!/usr/bin/env python3
"""Processa dados de Fundos de Desenvolvimento (FD): FDNE, FDA, FDCO.

Carrega, padroniza e agrega dados dos três fundos de desenvolvimento regional
para gerar resumos por fundo e setor.

Entrada:
    data/external_data/fds_contratacoes.xlsx  (contratos: FDA, FDNE, FDCO)
    data/external_data/fdne_liberacoes_ate_jun_2023.xlsx  (liberações FDNE)

Saída:
    data/external_data/resumo_fd.xlsx         (resumo por fundo/setor)
    data/external_data/fd_liberacoes_ano.xlsx  (liberações FDNE por ano)

Referência R: tese/bulding_dataset_R/source_code/fd_variables.R

Uso:
    python process_fd_data.py
    python process_fd_data.py --verbose
"""

from __future__ import annotations

import argparse
import logging
import re
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "external_data"

# Padronização de setores FD
SECTOR_MAP = {
    "infraestrutura": "Infraestrutura",
    "Infraestrutura": "Infraestrutura",
    "INFRAESTRUTURA": "Infraestrutura",
    "Indústria de Transformação": "Indústria de transformação",
    "industria de transformação": "Indústria de transformação",
    "Ind. transformação": "Indústria de transformação",
    "Indústria de transformação": "Indústria de transformação",
    "Tradicional": "Indústria de transformação",
    "Indústria extrativa": "Indústria extrativa",
    "Ind. extrativa": "Indústria extrativa",
    "Serviços": "Serviços",
    "Serviço": "Serviços",
}


def normalize_sector(setor: str) -> str:
    """Normaliza nome do setor para categoria padronizada.

    Args:
        setor: Nome original do setor

    Returns:
        Setor padronizado
    """
    if not setor or pd.isna(setor):
        return "Outro"
    setor = str(setor).strip()

    # Busca exata
    if setor in SECTOR_MAP:
        return SECTOR_MAP[setor]

    # Busca case-insensitive
    setor_lower = setor.lower()
    if "infraestrutura" in setor_lower:
        return "Infraestrutura"
    if "transforma" in setor_lower or "tradicional" in setor_lower:
        return "Indústria de transformação"
    if "extrat" in setor_lower:
        return "Indústria extrativa"
    if "servi" in setor_lower:
        return "Serviços"
    if "agro" in setor_lower or "agri" in setor_lower:
        return "Agroindústria"
    if "turismo" in setor_lower:
        return "Turismo"

    logger.debug(f"  Setor FD não mapeado: '{setor}'")
    return "Outro"


def load_contratacoes(filepath: Path) -> pd.DataFrame:
    """Carrega contratos FD de todas as sheets (FDA, FDNE, FDCO).

    O arquivo tem uma sheet por fundo. A primeira linha de cada sheet
    contém o nome do fundo, a segunda os cabeçalhos reais.

    Args:
        filepath: Caminho do fds_contratacoes.xlsx

    Returns:
        DataFrame consolidado com todos os contratos
    """
    xls = pd.ExcelFile(filepath)
    frames: list[pd.DataFrame] = []

    for sheet_name in xls.sheet_names:
        df = pd.read_excel(xls, sheet_name=sheet_name, header=None)

        if df.empty:
            continue

        # Encontrar a linha de cabeçalho (contém "Razão Social" ou "Empresa")
        header_idx = None
        for i in range(min(5, len(df))):
            row_text = " ".join(str(v) for v in df.iloc[i] if pd.notna(v))
            if "Raz" in row_text or "Empresa" in row_text:
                header_idx = i
                break

        if header_idx is None:
            logger.warning(f"  Sheet '{sheet_name}': cabeçalho não encontrado")
            continue

        # Usar a linha de cabeçalho como nomes de colunas
        headers = [str(v).strip() if pd.notna(v) else f"col_{j}" for j, v in enumerate(df.iloc[header_idx])]
        data = df.iloc[header_idx + 1:].copy()
        data.columns = headers
        data = data.dropna(how="all")

        # Padronizar nomes de colunas
        col_rename = {}
        for col in data.columns:
            col_lower = col.lower()
            if "raz" in col_lower or "empresa" in col_lower:
                col_rename[col] = "EMPRESA"
            elif col_lower == "uf":
                col_rename[col] = "UF"
            elif "munic" in col_lower:
                col_rename[col] = "MUNICIPIO"
            elif "setor" in col_lower:
                col_rename[col] = "SETOR"
            elif "cnae" in col_lower:
                col_rename[col] = "CNAE"
            elif "contrat" in col_lower:
                col_rename[col] = "VALOR_CONTRATADO"
            elif "empenh" in col_lower:
                col_rename[col] = "VALOR_EMPENHADO"
            elif "liberad" in col_lower:
                col_rename[col] = "VALOR_LIBERADO"

        data = data.rename(columns=col_rename)
        data["FUNDO"] = sheet_name.strip()

        # Converter valores monetários
        for vcol in ["VALOR_CONTRATADO", "VALOR_EMPENHADO", "VALOR_LIBERADO"]:
            if vcol in data.columns:
                data[vcol] = pd.to_numeric(data[vcol], errors="coerce").fillna(0)

        # Normalizar setor
        if "SETOR" in data.columns:
            data["SETOR2"] = data["SETOR"].apply(normalize_sector)
        else:
            data["SETOR2"] = "Outro"

        # Filtrar linhas sem empresa
        if "EMPRESA" in data.columns:
            data = data[data["EMPRESA"].notna() & (data["EMPRESA"].astype(str).str.strip() != "")]

        frames.append(data)
        logger.info(f"  Sheet '{sheet_name}': {len(data)} contratos")

    if not frames:
        return pd.DataFrame()

    combined = pd.concat(frames, ignore_index=True)
    logger.info(f"Total contratos: {len(combined)}")
    return combined


def load_fdne_liberacoes(filepath: Path) -> pd.DataFrame:
    """Carrega liberações FDNE por evento/ano.

    O arquivo tem formato de log por liberação com linhas "Total YYYY" separando anos.

    Args:
        filepath: Caminho do fdne_liberacoes_ate_jun_2023.xlsx

    Returns:
        DataFrame com liberações agregadas por ano
    """
    df = pd.read_excel(filepath, header=None)

    # Encontrar linha de dados (após "Documento", "Data", "Empresa"...)
    data_start = None
    for i in range(len(df)):
        val = str(df.iloc[i, 0]) if pd.notna(df.iloc[i, 0]) else ""
        if "Documento" in val:
            data_start = i + 1
            break

    if data_start is None:
        logger.warning("FDNE: não encontrou linha de dados")
        return pd.DataFrame()

    # Processar linhas: extrair ano de "Total YYYY" ou da coluna Data
    releases: list[dict] = []
    current_year: int | None = None

    for i in range(data_start, len(df)):
        val0 = str(df.iloc[i, 0]) if pd.notna(df.iloc[i, 0]) else ""

        # Linha "Total YYYY" marca o fim de um ano
        total_match = re.match(r"Total\s+(\d{4})", val0)
        if total_match:
            year = int(total_match.group(1))
            total_val = pd.to_numeric(df.iloc[i, 8], errors="coerce") or 0
            releases.append({"ANO": year, "TOTAL": total_val, "TIPO": "total_ano"})
            current_year = None
            continue

        # Linha de dados (documento começa com YYYY)
        year_match = re.match(r"(\d{4})", val0)
        if year_match:
            current_year = int(year_match.group(1))

        # Extrair ano da coluna Data se disponível
        if current_year is None and pd.notna(df.iloc[i, 1]):
            dt = str(df.iloc[i, 1])
            dt_match = re.search(r"(\d{4})", dt)
            if dt_match:
                current_year = int(dt_match.group(1))

        # Se é uma linha de liberação individual
        empresa = str(df.iloc[i, 2]) if pd.notna(df.iloc[i, 2]) else ""
        valor_total = pd.to_numeric(df.iloc[i, 8], errors="coerce")

        if empresa.strip() and pd.notna(valor_total) and current_year:
            releases.append({
                "ANO": current_year,
                "EMPRESA": empresa.strip(),
                "TOTAL": valor_total,
                "TIPO": "liberacao",
            })

    df_releases = pd.DataFrame(releases)

    # Resumo por ano (usando totais anuais)
    totais = df_releases[df_releases["TIPO"] == "total_ano"][["ANO", "TOTAL"]]
    totais = totais.rename(columns={"TOTAL": "VALOR_LIBERADO"})
    totais["FUNDO"] = "FDNE"

    logger.info(f"FDNE liberações: {len(totais)} anos, {len(df_releases[df_releases['TIPO']=='liberacao'])} liberações individuais")
    return totais


def generate_resumo(contratacoes: pd.DataFrame) -> pd.DataFrame:
    """Gera resumo de FD por fundo e setor.

    Args:
        contratacoes: DataFrame de contratos com FUNDO, SETOR2, VALOR_*

    Returns:
        DataFrame resumo agrupado
    """
    if contratacoes.empty:
        return pd.DataFrame()

    valor_cols = [c for c in ["VALOR_CONTRATADO", "VALOR_EMPENHADO", "VALOR_LIBERADO"]
                  if c in contratacoes.columns]

    resumo = (
        contratacoes.groupby(["FUNDO", "SETOR2"])
        .agg(
            N_PROJETOS=("EMPRESA", "count"),
            **{col: (col, "sum") for col in valor_cols},
        )
        .reset_index()
    )

    # Adicionar totais por fundo
    totais = (
        contratacoes.groupby("FUNDO")
        .agg(
            N_PROJETOS=("EMPRESA", "count"),
            **{col: (col, "sum") for col in valor_cols},
        )
        .reset_index()
    )
    totais["SETOR2"] = "TOTAL"
    resumo = pd.concat([resumo, totais], ignore_index=True)

    resumo = resumo.sort_values(["FUNDO", "SETOR2"]).reset_index(drop=True)
    return resumo


def main() -> int:
    """Ponto de entrada principal."""
    parser = argparse.ArgumentParser(
        description="Processa dados de Fundos de Desenvolvimento (FDNE, FDA, FDCO)"
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
        # 1. Carregar contratos
        contratacoes_path = DATA_DIR / "fds_contratacoes.xlsx"
        if not contratacoes_path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {contratacoes_path}")

        logger.info(f"Carregando contratos: {contratacoes_path.name}")
        contratacoes = load_contratacoes(contratacoes_path)

        # 2. Carregar liberações FDNE
        fdne_lib_path = DATA_DIR / "fdne_liberacoes_ate_jun_2023.xlsx"
        if fdne_lib_path.exists():
            logger.info(f"\nCarregando liberações FDNE: {fdne_lib_path.name}")
            fdne_liberacoes = load_fdne_liberacoes(fdne_lib_path)
        else:
            logger.warning(f"FDNE liberações não encontrado: {fdne_lib_path}")
            fdne_liberacoes = pd.DataFrame()

        # 3. FDA liberações — PENDENTE (PDF requer extração)
        fda_pdf = DATA_DIR / "fda_liberacoes_ate_2025.pdf"
        if fda_pdf.exists():
            logger.warning(f"FDA liberações disponível em PDF: {fda_pdf.name} (extração pendente)")

        # 4. Gerar resumo por fundo/setor
        resumo = generate_resumo(contratacoes)

        # 5. Salvar outputs
        out_resumo = DATA_DIR / "resumo_fd.xlsx"
        with pd.ExcelWriter(out_resumo) as writer:
            resumo.to_excel(writer, index=False, sheet_name="por_fundo_setor")
            contratacoes.to_excel(writer, index=False, sheet_name="contratos")
            if not fdne_liberacoes.empty:
                fdne_liberacoes.to_excel(writer, index=False, sheet_name="fdne_liberacoes_ano")

        logger.info(f"\nSalvo: {out_resumo}")

        # 6. Resumo final
        logger.info("\n" + "=" * 60)
        logger.info("RESUMO DOS FUNDOS DE DESENVOLVIMENTO")
        logger.info("=" * 60)

        for fundo in contratacoes["FUNDO"].unique():
            subset = contratacoes[contratacoes["FUNDO"] == fundo]
            total_lib = subset["VALOR_LIBERADO"].sum() if "VALOR_LIBERADO" in subset.columns else 0
            total_contr = subset["VALOR_CONTRATADO"].sum() if "VALOR_CONTRATADO" in subset.columns else 0
            logger.info(f"\n{fundo}: {len(subset)} projetos")
            logger.info(f"  Valor contratado: R$ {total_contr/1e9:.2f} bi")
            logger.info(f"  Valor liberado:   R$ {total_lib/1e9:.2f} bi")
            logger.info(f"  Por setor:")
            for setor, count in subset["SETOR2"].value_counts().items():
                setor_lib = subset[subset["SETOR2"] == setor]["VALOR_LIBERADO"].sum()
                logger.info(f"    {setor}: {count} projetos (R$ {setor_lib/1e9:.2f} bi)")

        if not fdne_liberacoes.empty:
            logger.info(f"\nLiberações FDNE por ano:")
            for _, row in fdne_liberacoes.iterrows():
                logger.info(f"  {int(row['ANO'])}: R$ {row['VALOR_LIBERADO']/1e9:.2f} bi")

        return 0

    except Exception:
        logger.exception("Erro ao processar dados FD")
        return 1


if __name__ == "__main__":
    import sys

    sys.exit(main())
