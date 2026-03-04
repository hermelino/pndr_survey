#!/usr/bin/env python3
"""Processa dados de Fundos Constitucionais (FC): FNE, FNO, FCO.

Carrega, padroniza e agrega dados dos três fundos constitucionais para
gerar resumos por fundo, tipologia e subperíodo, replicando a lógica de
fc_variables.R da tese.

Entrada (data/external_data/fc/):
    FNE - Contratações 2000 a 2018.xlsx
    FCO - Contratações 2000 a 2018.xlsx
    FNO - Contratações 2000 a 2018.xlsx
    FCO_cod_munic_ausentes.xlsx
    Consolidado Dez_2019 - FCF.xlsx
    Consolidado Dez_2020 - FCF.xlsx
    Consolidado Dez_2021 - FCF.xlsx

Dados auxiliares (data/external_data/):
    tipologia_2007.xlsx
    populacao_municipios.csv
    br_ibge_ipca.anual_2002_2020.csv

Saída:
    data/external_data/resumo_fc.xlsx        (resumo por fundo/tipologia/período)
    data/external_data/painel_fc.xlsx        (painel município/ano)
    latex/tabelas/fc_tabela_resumo.tex       (tabela LaTeX)

Referência R: tese/bulding_dataset_R/source_code/fc_variables.R

Uso:
    python process_fc_data.py
    python process_fc_data.py --verbose
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
FC_DIR = DATA_DIR / "fc"
TABELAS_DIR = PROJECT_ROOT / "latex" / "tabelas"

# Período de análise
ANALYSIS_START = 2002
ANALYSIS_END = 2021

# Subperíodos para a tabela resumo
PERIODS = [
    (2002, 2008),
    (2009, 2015),
    (2016, 2021),
]

# Classificação de setores por fundo (regex patterns)
FNO_SECTOR_MAP: dict[str, str] = {
    r"Rural": "Rural",
    r"Industrial": "Industrial",
    r"Empresarial": "Empresarial",
}

FNE_SECTOR_MAP: dict[str, str] = {
    r"Empresarial": "Empresarial",
    r"Agr[ií]cola|Agricultura|Agroind[uú]stria": "Agrícola/Agroindústria",
    r"Com[eé]rcio|Servi[cç]os": "Comércio e Serviços",
    r"Infra[\-]?estrutura": "Infraestrutura",
    r"Pecu[aá]ria": "Pecuária",
    r"Ind[uú]stria|Industrial": "Indústria",
    r"Rural": "Rural",
    r"Turismo": "Turismo",
}

FCO_SECTOR_MAP: dict[str, str] = {
    r"Rural": "Rural",
    r"Empresarial": "Empresarial",
}


def clean_text(text: str | None) -> str:
    """Remove caracteres de controle e espaços extras."""
    if text is None or pd.isna(text):
        return ""
    return re.sub(r"[\x00-\x1f]+|\s+", " ", str(text)).strip()


def classify_sector(setor: str, fund: str) -> str:
    """Classifica setor conforme o fundo.

    Args:
        setor: Nome original do setor
        fund: FNE, FNO ou FCO

    Returns:
        Setor padronizado
    """
    s = clean_text(setor)
    if not s:
        return "Outro"

    sector_map = {"FNE": FNE_SECTOR_MAP, "FNO": FNO_SECTOR_MAP, "FCO": FCO_SECTOR_MAP}
    mapping = sector_map.get(fund, {})

    for pattern, label in mapping.items():
        if re.search(pattern, s, re.IGNORECASE):
            return label

    return "Outro"


def load_fund_2000_2018(filepath: Path, fund: str) -> pd.DataFrame:
    """Carrega dados de um fundo individual (2000-2018).

    Args:
        filepath: Caminho do Excel
        fund: Nome do fundo (FNE, FNO, FCO)

    Returns:
        DataFrame padronizado
    """
    sheet = fund
    df = pd.read_excel(filepath, sheet_name=sheet)
    logger.info(f"  {fund}: {len(df)} linhas, colunas: {list(df.columns)}")

    # Padronizar nomes de colunas (cada fundo tem nomes diferentes)
    col_rename: dict[str, str] = {}
    for col in df.columns:
        cl = col.lower().strip()
        if cl in ("ano",):
            col_rename[col] = "ano"
        elif cl in ("cd_mun_ibge", "codigo do municipio", "código do município"):
            col_rename[col] = "CD_MUN"
        elif cl in ("uf_mun", "uf"):
            col_rename[col] = "UF"
        elif cl in ("municipio", "município"):
            col_rename[col] = "MUNICIPIO"
        elif cl in ("finalidade",):
            col_rename[col] = "finalidade"
        elif cl in ("setor",):
            col_rename[col] = "setor"
        elif cl in ("programa",):
            col_rename[col] = "programa"
        elif cl in ("linha de financiamento",):
            # FNO tem "Programa" E "Linha de Financiamento"; FCO só tem "Linha de Financiamento"
            if "programa" not in col_rename.values():
                col_rename[col] = "programa"
            else:
                col_rename[col] = "linha_financiamento"
        elif cl in ("porte",):
            col_rename[col] = "porte"
        elif cl in ("qtde", "nr.op.contratadas", "n de operacoes contratadas",
                     "nº de operações contratadas"):
            col_rename[col] = "operacoes"
        elif "valor" in cl:
            col_rename[col] = "fc"

    df = df.rename(columns=col_rename)
    df["INSTR"] = fund

    return df


def load_consolidated(filepath: Path, sheet_name: str) -> pd.DataFrame:
    """Carrega arquivo consolidado (2019-2021).

    Args:
        filepath: Caminho do Excel consolidado
        sheet_name: Nome da sheet

    Returns:
        DataFrame padronizado
    """
    df = pd.read_excel(filepath, sheet_name=sheet_name)
    logger.info(f"  Consolidado '{sheet_name}': {len(df)} linhas")

    # Mapear colunas consolidadas → padrão
    col_rename = {
        "num_ano": "ano",
        "cod_municipio": "CD_MUN",
        "dsc_uf": "UF",
        "dsc_municipio": "MUNICIPIO",
        "dsc_finalidade": "finalidade",
        "dsc_setor_1": "setor",
        "dsc_programa": "programa",
        "dsc_porte": "porte",
        "num_operacao_contratada": "operacoes",
        "vlr_contrato": "fc",
        "dsc_fonte": "INSTR",
    }
    df = df.rename(columns=col_rename)

    return df


def fix_missing_mun_codes(df: pd.DataFrame) -> pd.DataFrame:
    """Corrige códigos de município ausentes usando lookup table.

    Alguns registros FCO (e poucos FNO) têm CD_MUN = '-' ou NaN.
    Usa o arquivo FCO_cod_munic_ausentes.xlsx para preencher.

    Args:
        df: DataFrame com coluna CD_MUN

    Returns:
        DataFrame com CD_MUN corrigidos
    """
    lookup_path = FC_DIR / "FCO_cod_munic_ausentes.xlsx"
    if not lookup_path.exists():
        logger.warning("Lookup de municípios ausentes não encontrado")
        return df

    lookup = pd.read_excel(lookup_path)
    # Colunas: UF, localidade, CD_MUN, municipio2
    lookup["localidade_upper"] = lookup["localidade"].str.upper().str.strip()

    missing_mask = df["CD_MUN"].isna() | (df["CD_MUN"].astype(str).str.strip().isin(["-", "", "nan"]))
    n_missing = missing_mask.sum()
    if n_missing == 0:
        return df

    logger.info(f"  {n_missing} registros com CD_MUN ausente, tentando corrigir...")

    if "MUNICIPIO" not in df.columns:
        return df

    # Criar dicionário de lookup: (UF, MUNICIPIO_UPPER) → CD_MUN
    fix_dict: dict[tuple[str, str], int] = {}
    for _, row in lookup.iterrows():
        key = (str(row["UF"]).strip(), str(row["localidade"]).upper().strip())
        fix_dict[key] = row["CD_MUN"]

    # Aplicar correção
    missing_idx = df.index[missing_mask]
    n_fixed = 0
    for idx in missing_idx:
        uf = str(df.at[idx, "UF"]).strip()
        mun = str(df.at[idx, "MUNICIPIO"]).upper().strip()
        if (uf, mun) in fix_dict:
            df.at[idx, "CD_MUN"] = fix_dict[(uf, mun)]
            n_fixed += 1

    logger.info(f"  Corrigidos: {n_fixed} de {n_missing}")

    return df


def load_all_fc_data() -> pd.DataFrame:
    """Carrega e consolida todos os dados FC (2000-2021).

    Returns:
        DataFrame unificado com colunas padronizadas
    """
    frames: list[pd.DataFrame] = []

    # 1. Dados individuais 2000-2018
    for fund, filename in [
        ("FNE", "FNE - Contratações 2000 a 2018.xlsx"),
        ("FCO", "FCO - Contratações 2000 a 2018.xlsx"),
        ("FNO", "FNO - Contratações 2000 a 2018.xlsx"),
    ]:
        fpath = FC_DIR / filename
        if fpath.exists():
            logger.info(f"Carregando {fund} (2000-2018)...")
            df = load_fund_2000_2018(fpath, fund)
            frames.append(df)
        else:
            logger.warning(f"Arquivo não encontrado: {fpath}")

    # 2. Consolidados 2019-2021
    consolidados = [
        ("Consolidado Dez_2019 - FCF.xlsx", "Consolidado 2019"),
        ("Consolidado Dez_2020 - FCF.xlsx", "Consolidado 2020"),
        ("Consolidado Dez_2021 - FCF.xlsx", "Dezembro"),
    ]
    for filename, sheet in consolidados:
        fpath = FC_DIR / filename
        if fpath.exists():
            logger.info(f"Carregando {filename}...")
            df = load_consolidated(fpath, sheet)
            frames.append(df)
        else:
            logger.warning(f"Arquivo não encontrado: {fpath}")

    if not frames:
        raise FileNotFoundError("Nenhum arquivo FC encontrado")

    # Consolidar
    # Selecionar apenas colunas comuns
    common_cols = ["ano", "CD_MUN", "UF", "MUNICIPIO", "finalidade", "setor",
                   "programa", "porte", "operacoes", "fc", "INSTR"]

    clean_frames = []
    for df in frames:
        available = [c for c in common_cols if c in df.columns]
        clean = df[available].copy()
        for c in common_cols:
            if c not in clean.columns:
                clean[c] = None
        clean_frames.append(clean)

    combined = pd.concat(clean_frames, ignore_index=True)

    # Tipos
    combined["ano"] = pd.to_numeric(combined["ano"], errors="coerce")
    combined["CD_MUN"] = pd.to_numeric(combined["CD_MUN"], errors="coerce")
    combined["operacoes"] = pd.to_numeric(combined["operacoes"], errors="coerce").fillna(0)
    combined["fc"] = pd.to_numeric(combined["fc"], errors="coerce").fillna(0)

    # Limpar textos
    for col in ["setor", "programa", "porte", "finalidade"]:
        combined[col] = combined[col].apply(clean_text)

    # Corrigir códigos de município ausentes
    combined = fix_missing_mun_codes(combined)

    # Filtrar: ano > 2000, CD_MUN válido
    combined = combined[combined["ano"].notna() & (combined["ano"] > 2000)]
    combined = combined[combined["CD_MUN"].notna()]
    combined["CD_MUN"] = combined["CD_MUN"].astype(int)

    # Classificar setor padronizado
    combined["setor2"] = combined.apply(
        lambda r: classify_sector(r["setor"], r["INSTR"]), axis=1
    )

    logger.info(f"Total FC consolidado: {len(combined)} linhas, "
                f"anos {int(combined['ano'].min())}-{int(combined['ano'].max())}")

    return combined


def load_auxiliar_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Carrega dados auxiliares: tipologia, população, IPCA, PIB municipal.

    Returns:
        Tupla (tipologia, populacao, ipca, pib) como DataFrames
    """
    # Tipologia 2007
    tip = pd.read_excel(DATA_DIR / "tipologia_2007.xlsx")
    # Renomear colunas com encoding potencialmente quebrado
    tip.columns = ["CD_MUN", "REGIAO", "UF", "MUNICIPIO", "MICRORREGIAO", "tipologia2007"]
    tip["CD_MUN"] = pd.to_numeric(tip["CD_MUN"], errors="coerce").astype("Int64")
    logger.info(f"Tipologia: {len(tip)} municípios, "
                f"categorias: {tip['tipologia2007'].unique().tolist()}")

    # População
    pop = pd.read_csv(DATA_DIR / "populacao_municipios.csv", sep=";")
    pop = pop.rename(columns={"id_municipio": "CD_MUN"})
    pop["CD_MUN"] = pd.to_numeric(pop["CD_MUN"], errors="coerce")
    pop["ano"] = pd.to_numeric(pop["ano"], errors="coerce")
    pop["populacao"] = pd.to_numeric(pop["populacao"], errors="coerce")
    pop = pop[["ano", "CD_MUN", "populacao"]].dropna()
    logger.info(f"População: {pop['CD_MUN'].nunique()} municípios, "
                f"anos {int(pop['ano'].min())}-{int(pop['ano'].max())}")

    # IPCA (fator de deflação, base = 2020)
    ipca = pd.read_csv(DATA_DIR / "br_ibge_ipca.anual_2002_2020.csv", sep=";")
    ipca["ano"] = pd.to_numeric(ipca["ano"], errors="coerce")
    ipca["ipca_fator"] = ipca["ipca_fator"].str.replace(",", ".").astype(float)
    ipca = ipca[["ano", "ipca_fator"]].dropna()
    logger.info(f"IPCA: {len(ipca)} anos, fator range: "
                f"{ipca['ipca_fator'].min():.3f} - {ipca['ipca_fator'].max():.3f}")

    # PIB municipal (IBGE, em R$ 1.000)
    pib_path = Path("C:/OneDrive/DATABASES/MUNICÍPIOS/pib_municipios.xlsx")
    pib = pd.read_excel(pib_path)
    pib = pib.rename(columns={"id_municipio": "CD_MUN"})
    pib["CD_MUN"] = pd.to_numeric(pib["CD_MUN"], errors="coerce")
    pib["ano"] = pd.to_numeric(pib["ano"], errors="coerce")
    pib["pib"] = pd.to_numeric(pib["pib"], errors="coerce")
    pib = pib[["ano", "CD_MUN", "pib"]].dropna()
    logger.info(f"PIB municipal: {pib['CD_MUN'].nunique()} municípios, "
                f"anos {int(pib['ano'].min())}-{int(pib['ano'].max())}")

    return tip, pop, ipca, pib


def build_panel(
    fc: pd.DataFrame,
    tipologia: pd.DataFrame,
    populacao: pd.DataFrame,
    ipca: pd.DataFrame,
    pib: pd.DataFrame,
) -> pd.DataFrame:
    """Constrói painel município/ano com valores deflacionados.

    Args:
        fc: Dados FC consolidados
        tipologia: Tipologia 2007
        populacao: População municipal
        ipca: Fator IPCA
        pib: PIB municipal (IBGE, em R$ 1.000)

    Returns:
        Painel agregado por (ano, CD_MUN, INSTR)
    """
    # Filtrar período
    fc = fc[(fc["ano"] >= ANALYSIS_START) & (fc["ano"] <= ANALYSIS_END)].copy()

    # Agregar por ano/município/instrumento
    panel = (
        fc.groupby(["ano", "CD_MUN", "INSTR"])
        .agg(
            fc=("fc", "sum"),
            operacoes=("operacoes", "sum"),
        )
        .reset_index()
    )

    # Join com IPCA para deflacionar
    panel = panel.merge(ipca, on="ano", how="left")
    # Para anos sem IPCA (ex: 2021), usar o mais próximo
    if panel["ipca_fator"].isna().any():
        last_ipca = ipca.sort_values("ano").iloc[-1]
        logger.info(f"Usando IPCA de {int(last_ipca['ano'])} para anos sem dados")
        panel["ipca_fator"] = panel["ipca_fator"].fillna(last_ipca["ipca_fator"])

    panel["fc_deflac"] = panel["fc"] * panel["ipca_fator"]

    # Join com tipologia
    panel = panel.merge(
        tipologia[["CD_MUN", "tipologia2007"]],
        on="CD_MUN",
        how="left",
    )

    # Join com população
    panel = panel.merge(populacao, on=["ano", "CD_MUN"], how="left")

    # Per capita
    panel["fc_pc"] = panel["fc_deflac"] / panel["populacao"]
    panel["fc_pc"] = panel["fc_pc"].replace([float("inf"), float("-inf")], 0)

    # Join com PIB municipal
    panel = panel.merge(pib, on=["ano", "CD_MUN"], how="left")

    # Participação no PIB: fc / (pib * 1000) — ambos nominais, mesmo ano
    panel["fc_pib"] = panel["fc"] / (panel["pib"] * 1000)
    panel["fc_pib"] = panel["fc_pib"].replace([float("inf"), float("-inf")], 0).fillna(0)

    logger.info(f"Painel: {len(panel)} obs, {panel['CD_MUN'].nunique()} municípios, "
                f"tipologia preenchida: {panel['tipologia2007'].notna().sum()}/{len(panel)}")

    return panel


def generate_summary_table(panel: pd.DataFrame) -> pd.DataFrame:
    """Gera tabela resumo por fundo, tipologia e subperíodo.

    Replica o formato da tabela fc_tabela_resumo.tex.
    Totais e participação no PIB calculados a partir do painel agregado (município-ano).
    Participação no PIB = mean(fc / PIB) por município-ano.

    Args:
        panel: Painel agregado (município-ano) com fc_deflac, fc_pc

    Returns:
        DataFrame com resumo
    """
    panel_tip = panel[panel["tipologia2007"].notna()].copy()

    rows: list[dict] = []

    for instr in ["FNE", "FCO", "FNO"]:
        df_instr = panel_tip[panel_tip["INSTR"] == instr]
        tipologias = sorted(df_instr["tipologia2007"].dropna().unique())

        for tip in tipologias:
            df_tip = df_instr[df_instr["tipologia2007"] == tip]
            row: dict = {"INSTR": instr, "tipologia": tip}

            for p_start, p_end in PERIODS:
                period_key = f"{p_start}_{p_end}"
                df_period = df_tip[
                    (df_tip["ano"] >= p_start) & (df_tip["ano"] <= p_end)
                ]

                # Valor total em R$ milhões
                total = df_period["fc_deflac"].sum() / 1e6
                row[f"total_{period_key}"] = total

                # Participação no PIB: média no nível município-ano
                valid_pib = df_period["fc_pib"].replace(
                    [float("inf"), float("-inf")], float("nan")
                ).dropna()
                pib_mean = valid_pib.mean() if len(valid_pib) > 0 else 0
                row[f"pib_{period_key}"] = pib_mean

            rows.append(row)

    summary = pd.DataFrame(rows)
    return summary


def generate_figure_data(
    fc_raw: pd.DataFrame,
    panel: pd.DataFrame,
    tipologia: pd.DataFrame,
    ipca: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Gera dados agregados para a figura FC por setor/tipologia.

    Produz duas tabelas:
    - setor_tipologia: valor total (R$ bilhões, deflacionado) por (INSTR, tipologia, setor2)
    - medias_pc: média per capita por (INSTR, tipologia), calculada como
      mean(mean_anos_por_municipio), replicando a lógica R.

    Args:
        fc_raw: Dados brutos FC (nível transação)
        panel: Painel agregado (município-ano) com fc_deflac
        tipologia: Tipologia 2007
        ipca: Fator IPCA

    Returns:
        Tupla (setor_tipologia, medias_pc)
    """
    # 1. Dados por setor e tipologia (do raw, deflacionado)
    raw = fc_raw[
        (fc_raw["ano"] >= ANALYSIS_START) & (fc_raw["ano"] <= ANALYSIS_END)
    ].copy()
    raw = raw.merge(ipca, on="ano", how="left")
    if raw["ipca_fator"].isna().any():
        last_ipca = ipca.sort_values("ano").iloc[-1]["ipca_fator"]
        raw["ipca_fator"] = raw["ipca_fator"].fillna(last_ipca)
    raw["fc_deflac"] = raw["fc"] * raw["ipca_fator"]
    raw = raw.merge(tipologia[["CD_MUN", "tipologia2007"]], on="CD_MUN", how="left")
    raw = raw[raw["tipologia2007"].notna()]

    setor_tip = (
        raw.groupby(["INSTR", "tipologia2007", "setor2"])["fc_deflac"]
        .sum()
        .reset_index()
    )
    setor_tip["valor_bi"] = setor_tip["fc_deflac"] / 1e9
    setor_tip = setor_tip.drop(columns=["fc_deflac"])

    # 2. Médias per capita (do panel, estilo R: mean por município, depois mean por tipologia)
    panel_tip = panel[panel["tipologia2007"].notna()].copy()
    # Passo 1: média ao longo dos anos para cada município
    pc_by_mun = (
        panel_tip.groupby(["CD_MUN", "INSTR", "tipologia2007"])["fc_pc"]
        .mean()
        .reset_index()
    )
    # Passo 2: média entre municípios para cada tipologia
    medias_pc = (
        pc_by_mun.groupby(["INSTR", "tipologia2007"])["fc_pc"]
        .mean()
        .reset_index()
        .rename(columns={"fc_pc": "pc_media"})
    )

    logger.info(f"Dados para figura: {len(setor_tip)} linhas setor/tipologia, "
                f"{len(medias_pc)} linhas per capita")

    return setor_tip, medias_pc


def generate_latex_table(summary: pd.DataFrame) -> str:
    """Gera tabela LaTeX a partir do resumo.

    Args:
        summary: DataFrame do resumo

    Returns:
        String com código LaTeX
    """
    def fmt_total(x: float) -> str:
        if x >= 1000:
            return f"{x:,.0f}".replace(",", ".")
        elif x >= 1:
            return f"{x:,.1f}".replace(",", "X").replace(".", ",").replace("X", ".")
        return f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    def fmt_pib(x: float) -> str:
        """Formata participação no PIB como percentual."""
        pct = x * 100
        if abs(pct) < 0.01:
            return "0,00"
        return f"{pct:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    lines = [
        r"\begin{table}[h!]",
        r"	\centering",
        r"	\caption{Aplicações dos Fundos Constitucionais (R\$ de 2020)}",
        r"	\label{tab:resumo_fc}",
        r"	\footnotesize",
        r"	\renewcommand{\arraystretch}{1.2}",
        r"	\begin{tabular}{llcccccc}",
        r"		\toprule",
        r"		\multirow{2}{*}{Fundo} & \multirow{2}{*}{Tipologia} & \multicolumn{3}{c}{Valor total (R\$ Milhões)} & \multicolumn{3}{c}{Participação média no PIB municipal (\%)} \\",
        r"		\cmidrule(lr){3-5} \cmidrule(lr){6-8}",
        r"		& & 2002-2008 & 2009-2015 & 2016-2021 & 2002-2008 & 2009-2015 & 2016-2021 \\",
        r"		\midrule",
    ]

    for instr in ["FNE", "FCO", "FNO"]:
        df_instr = summary[summary["INSTR"] == instr]
        n_rows = len(df_instr)

        for i, (_, row) in enumerate(df_instr.iterrows()):
            tip = row["tipologia"]

            if i == 0:
                prefix = rf"		\multirow{{{n_rows}}}{{*}}{{{instr}}}"
            else:
                prefix = r"		"

            t1 = fmt_total(row["total_2002_2008"])
            t2 = fmt_total(row["total_2009_2015"])
            t3 = fmt_total(row["total_2016_2021"])
            p1 = fmt_pib(row["pib_2002_2008"])
            p2 = fmt_pib(row["pib_2009_2015"])
            p3 = fmt_pib(row["pib_2016_2021"])

            lines.append(
                f"{prefix} & {tip} & {t1} & {t2} & {t3} & {p1} & {p2} & {p3} \\\\"
            )

        if instr != "FNO":
            lines.append(r"		\midrule")

    lines.extend([
        r"		\bottomrule",
        r"		\multicolumn{8}{l}{\footnotesize{Fonte: Elaborada pelo autor a partir de dados de BB, BASA e BNB.}} \\",
        r"	\end{tabular}",
        r"\end{table}",
    ])

    return "\n".join(lines)


def main() -> int:
    """Ponto de entrada principal."""
    parser = argparse.ArgumentParser(
        description="Processa dados de Fundos Constitucionais (FNE, FNO, FCO)"
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Logging detalhado"
    )
    parser.add_argument(
        "--no-table", action="store_true", help="Não gerar tabela LaTeX"
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s: %(message)s",
    )

    try:
        # 1. Carregar dados FC
        fc = load_all_fc_data()

        # 2. Carregar dados auxiliares
        tipologia, populacao, ipca, pib = load_auxiliar_data()

        # 3. Construir painel
        panel = build_panel(fc, tipologia, populacao, ipca, pib)

        # 4. Gerar resumo (per capita no nível município-ano)
        summary = generate_summary_table(panel)

        # 4b. Gerar dados para figuras
        setor_tip, medias_pc = generate_figure_data(fc, panel, tipologia, ipca)

        # 5. Salvar outputs
        out_resumo = DATA_DIR / "resumo_fc.xlsx"
        with pd.ExcelWriter(out_resumo) as writer:
            summary.to_excel(writer, index=False, sheet_name="resumo_tipologia")
            # Agregar total por fundo/ano para referência
            por_fundo_ano = (
                panel.groupby(["INSTR", "ano"])
                .agg(fc_total=("fc_deflac", "sum"), operacoes=("operacoes", "sum"))
                .reset_index()
            )
            por_fundo_ano.to_excel(writer, index=False, sheet_name="por_fundo_ano")
            # Dados para figuras
            setor_tip.to_excel(writer, index=False, sheet_name="por_fundo_setor_tipologia")
            medias_pc.to_excel(writer, index=False, sheet_name="medias_pc_tipologia")

        logger.info(f"Resumo salvo: {out_resumo}")

        # 6. Salvar painel (Excel — pyarrow/parquet não disponível)
        out_panel = DATA_DIR / "painel_fc.xlsx"
        panel.to_excel(out_panel, index=False, sheet_name="painel")
        logger.info(f"Painel salvo: {out_panel}")

        # 7. Gerar tabela LaTeX
        if not args.no_table:
            latex_str = generate_latex_table(summary)
            out_tex = TABELAS_DIR / "fc_tabela_resumo.tex"
            out_tex.parent.mkdir(parents=True, exist_ok=True)
            out_tex.write_text(latex_str, encoding="utf-8")
            logger.info(f"Tabela LaTeX salva: {out_tex}")

        # 8. Resumo no log
        logger.info("\n" + "=" * 60)
        logger.info("RESUMO DOS FUNDOS CONSTITUCIONAIS")
        logger.info("=" * 60)

        for instr in ["FNE", "FCO", "FNO"]:
            df_i = panel[panel["INSTR"] == instr]
            total = df_i["fc_deflac"].sum()
            n_mun = df_i["CD_MUN"].nunique()
            logger.info(f"\n{instr}: {n_mun} municípios, "
                        f"R$ {total/1e9:.1f} bi (deflacionado)")

            s = summary[summary["INSTR"] == instr]
            for _, row in s.iterrows():
                logger.info(f"  {row['tipologia']}: "
                            f"R$ {row['total_2002_2008']:,.0f}M | "
                            f"R$ {row['total_2009_2015']:,.0f}M | "
                            f"R$ {row['total_2016_2021']:,.0f}M")

        return 0

    except Exception:
        logger.exception("Erro ao processar dados FC")
        return 1


if __name__ == "__main__":
    import sys

    sys.exit(main())
