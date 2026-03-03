#!/usr/bin/env python3
"""Processa dados de PIB municipal do IBGE e gera dataset consolidado.

Lê dados de PIB municipal 2002-2023, calcula PIB per capita relativo
(razão municipal/nacional) e salva em formato Parquet otimizado.

Uso:
    python process_pib_data.py
    python process_pib_data.py --output data/external_data/pib_municipal_completo.parquet
    python process_pib_data.py --years 2002,2010,2019,2021  # Filtrar anos específicos

Entrada:
    - pib_municipios_2002_2009.xlsx
    - pib_municipios_2010_2023.xlsx

Saída:
    - data/external_data/pib_municipal_completo.parquet (otimizado)
    - data/external_data/pib_relativo_anos_selecionados.parquet (filtrado)
"""

from __future__ import annotations

import argparse
import logging
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "external_data"


def normalize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """Padroniza nomes de colunas removendo quebras de linha e espaços extras.

    Args:
        df: DataFrame com colunas brutas do IBGE

    Returns:
        DataFrame com colunas padronizadas
    """
    rename_map = {}

    for col in df.columns:
        # Remover quebras de linha e espaços múltiplos
        clean_name = " ".join(str(col).split())

        # Simplificar nomes longos (match no nome LIMPO, após .split().join())
        simplifications = {
            "Código do Município": "cod_municipio",
            "Nome do Município": "nome_municipio",
            "Sigla da Unidade da Federação": "uf",
            "Ano": "ano",
            "Produto Interno Bruto, a preços correntes (R$ 1.000)": "pib",
            "Produto Interno Bruto per capita, a preços correntes (R$ 1,00)": "pib_per_capita",
            "Valor adicionado bruto da Agropecuária, a preços correntes (R$ 1.000)": "vab_agro",
            "Valor adicionado bruto da Indústria, a preços correntes (R$ 1.000)": "vab_industria",
            "Valor adicionado bruto dos Serviços, a preços correntes - exceto Administração, defesa, educação e saúde públicas e seguridade social (R$ 1.000)": "vab_servicos",
            "Valor adicionado bruto da Administração, defesa, educação e saúde públicas e seguridade social, a preços correntes (R$ 1.000)": "vab_adm_pub",
            "Amazônia Legal": "amazonia_legal",
            "Semiárido": "semiarido",
        }

        if clean_name in simplifications:
            rename_map[col] = simplifications[clean_name]
        else:
            rename_map[col] = clean_name

    return df.rename(columns=rename_map)


def calculate_pib_relativo(df: pd.DataFrame) -> pd.DataFrame:
    """Calcula PIB per capita relativo (municipal/nacional) por ano.

    Args:
        df: DataFrame com colunas 'ano' e 'pib_per_capita'

    Returns:
        DataFrame com coluna adicional 'pib_per_capita_relativo'
    """
    # PIB per capita nacional por ano
    pib_nacional = df.groupby("ano")["pib_per_capita"].mean()

    # Razão PIB municipal / PIB nacional
    df["pib_per_capita_relativo"] = df.apply(
        lambda row: row["pib_per_capita"] / pib_nacional[row["ano"]], axis=1
    )

    return df


def load_and_merge_pib_data(
    file_2002_2009: Path, file_2010_2023: Path
) -> pd.DataFrame:
    """Carrega e mescla dados de PIB municipal de dois períodos.

    Args:
        file_2002_2009: Arquivo Excel PIB 2002-2009
        file_2010_2023: Arquivo Excel PIB 2010-2023

    Returns:
        DataFrame consolidado 2002-2023 com colunas padronizadas
    """
    logger.info(f"Carregando {file_2002_2009.name}...")
    df1 = pd.read_excel(file_2002_2009)
    df1 = normalize_column_names(df1)

    logger.info(f"Carregando {file_2010_2023.name}...")
    df2 = pd.read_excel(file_2010_2023)
    df2 = normalize_column_names(df2)

    # Identificar colunas comuns
    common_cols = list(set(df1.columns) & set(df2.columns))
    logger.info(f"Mesclando datasets ({len(common_cols)} colunas comuns)...")

    # Mesclar apenas colunas comuns
    df_merged = pd.concat([df1[common_cols], df2[common_cols]], ignore_index=True)

    logger.info(
        f"Dataset consolidado: {len(df_merged):,} registros, {len(df_merged.columns)} colunas"
    )

    return df_merged


def filter_years(df: pd.DataFrame, years: list[int]) -> pd.DataFrame:
    """Filtra dataset para anos específicos.

    Args:
        df: DataFrame completo
        years: Lista de anos a manter

    Returns:
        DataFrame filtrado
    """
    df_filtered = df[df["ano"].isin(years)].copy()
    logger.info(
        f"Dados filtrados para anos {years}: {len(df_filtered):,} registros"
    )
    return df_filtered


def save_dataframe(df: pd.DataFrame, output_path: Path, format: str = "parquet") -> None:
    """Salva DataFrame em formato otimizado.

    Args:
        df: DataFrame a salvar
        output_path: Caminho do arquivo de saída
        format: Formato de saída ('parquet', 'pickle', 'csv', 'feather')
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if format == "parquet":
        try:
            df.to_parquet(
                output_path,
                engine="pyarrow",
                compression="snappy",
                index=False,
            )
        except ImportError:
            logger.warning("pyarrow não disponível, usando pickle")
            output_path = output_path.with_suffix(".pkl")
            df.to_pickle(output_path, compression=None)
    elif format == "pickle":
        df.to_pickle(output_path, compression=None)
    elif format == "feather":
        df.to_feather(output_path)
    elif format == "csv":
        df.to_csv(output_path, index=False, encoding="utf-8-sig")
    else:
        raise ValueError(f"Formato inválido: {format}")

    size_mb = output_path.stat().st_size / (1024 * 1024)
    logger.info(f"Arquivo salvo: {output_path} ({size_mb:.2f} MB)")


def main() -> int:
    """Ponto de entrada principal.

    Returns:
        Exit code (0 = sucesso, 1 = erro)
    """
    parser = argparse.ArgumentParser(
        description="Processa dados de PIB municipal IBGE 2002-2023"
    )
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=PROJECT_ROOT,
        help="Diretório contendo arquivos Excel de entrada",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DATA_DIR,
        help="Diretório de saída para arquivos Parquet",
    )
    parser.add_argument(
        "--years",
        type=str,
        default="2002,2010,2019,2021",
        help="Anos para dataset filtrado (separados por vírgula)",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Logging detalhado"
    )

    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s: %(message)s",
    )

    try:
        # Localizar arquivos de entrada
        file_2002_2009 = args.input_dir / "pib_municipios_2002_2009.xlsx"
        file_2010_2023 = args.input_dir / "pib_municipios_2010_2023.xlsx"

        if not file_2002_2009.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {file_2002_2009}")
        if not file_2010_2023.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {file_2010_2023}")

        # Processar dados
        df = load_and_merge_pib_data(file_2002_2009, file_2010_2023)

        # Calcular PIB relativo
        logger.info("Calculando PIB per capita relativo...")
        df = calculate_pib_relativo(df)

        # Salvar dataset completo
        output_full = args.output_dir / "pib_municipal_completo.parquet"
        save_dataframe(df, output_full, format="parquet")

        # Filtrar anos específicos
        years = [int(y.strip()) for y in args.years.split(",")]
        df_filtered = filter_years(df, years)

        # Salvar dataset filtrado
        output_filtered = args.output_dir / "pib_relativo_anos_selecionados.parquet"
        save_dataframe(df_filtered, output_filtered, format="parquet")

        logger.info("\n✓ Processamento concluído com sucesso!")
        logger.info(f"  Dataset completo: {output_full}")
        logger.info(f"  Dataset filtrado: {output_filtered}")

        return 0

    except Exception as e:
        logger.exception("Erro ao processar dados de PIB")
        return 1


if __name__ == "__main__":
    import sys

    sys.exit(main())
