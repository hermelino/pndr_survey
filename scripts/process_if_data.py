#!/usr/bin/env python3
"""Processa dados de Incentivos Fiscais (IF) da SUDENE e SUDAM.

Carrega, filtra, padroniza e agrega dados de incentivos fiscais das duas
superintendências regionais para gerar um dataset consolidado e resumos
por setor e órgão.

Entrada:
    data/external_data/if_sudene.json          (SUDENE — Portal Dados Abertos)
    data/external_data/if_sudam/
        sudam_incentivos_consolidado.xlsx       (SUDAM — extraído dos PDFs)

Saída:
    data/external_data/if_consolidado.xlsx      (todos os registros filtrados)
    data/external_data/resumo_icf.xlsx          (resumo por órgão/setor)

Referência R: tese/bulding_dataset_R/source_code/if_variables.R

Uso:
    python process_if_data.py
    python process_if_data.py --verbose
"""

from __future__ import annotations

import argparse
import json
import logging
import re
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "external_data"

# ═══════════════════════════════════════════════════════════════════
# Constantes de filtragem e classificação
# ═══════════════════════════════════════════════════════════════════

ANALYSIS_PERIOD = (2010, 2023)

# UFs fora da área de atuação das superintendências (excluir)
EXCLUDED_UFS = {"SC", "RS", "PR", "SP", "RJ", "DF", "GO", "ES", "MG", "-", ""}

# Tipos de incentivo válidos (Redução de 75% do IRPJ)
VALID_TIPO_PATTERNS = [
    "Redução de 75% do IRPJ",
    "REDUÇÃO",
    "Redução",
]

# Modalidades válidas
VALID_MODALIDADES = {
    "Ampliação",
    "Diversificação",
    "Implantação",
    "Modernização",
    "Modernização Parcial",
    "Modernização Total",
}

# ═══════════════════════════════════════════════════════════════════
# Classificação de setores: 6 categorias padronizadas
# ═══════════════════════════════════════════════════════════════════

# Mapeamento SUDENE: setor_economico_abreviado → SETOR2
# Para valores compostos (com " e " ou ", "), usa o primeiro setor
SUDENE_SECTOR_MAP: dict[str, str] = {
    "Infraestrutura": "Infraestrutura",
    "Turismo": "Turismo",
    "Agricultura irrigada": "Agricultura irrigada",
    "Agroindústria": "Agroindústria",
    "Indústria extrativa de minerais metálicos": "Indústria extrativa de minerais metálicos",
    # Todas as subcategorias de indústria de transformação
    "Indústria de transformação - Químicos": "Indústria de transformação",
    "Indústria de transformação - Alimentos e bebidas": "Indústria de transformação",
    "Indústria de transformação - Minerais não-metálicos e outros": "Indústria de transformação",
    "Indústria de transformação - Têxtil e outros": "Indústria de transformação",
    "Indústria de transformação - Fab. de máquinas e equipamentos": "Indústria de transformação",
    "Indústria de transformação - Madeira": "Indústria de transformação",
    "Indústria de transformação - Celulose e papel": "Indústria de transformação",
    "Indústria de transformação - Produtos farmacêuticos": "Indústria de transformação",
    "Indústria de transformação - Material de transporte": "Indústria de transformação",
    "Eletro-eletrônica": "Indústria de transformação",
    "Componentes (microeletrônica)": "Indústria de transformação",
}

# Mapeamento SUDAM: ENQUADRAMENTO (Decreto 4.212/2002) → SETOR2
# Art 2°, Inciso e alínea determinam o setor econômico
SUDAM_ENQUADRAMENTO_MAP: dict[str, str] = {
    "Inciso I": "Infraestrutura",
    "Inciso III": "Turismo",
    "Inciso V": "Indústria extrativa de minerais metálicos",
    'Inciso VI, alínea "a"': "Agricultura irrigada",
    'Inciso VI, alínea "b"': "Indústria de transformação",
    'Inciso VI, alínea "c"': "Indústria de transformação",
    'Inciso VI, alínea "d"': "Indústria de transformação",
    'Inciso VI, alínea "e"': "Indústria de transformação",
    'Inciso VI, alínea "f"': "Indústria de transformação",
    'Inciso VI, alínea "g"': "Indústria de transformação",
    'Inciso VI, alínea "h"': "Agroindústria",
    'Inciso VI, alínea "i"': "Indústria de transformação",
    "Inciso VII": "Indústria de transformação",
    "Inciso IX": "Indústria de transformação",
}

# Código para pivotagem: SETOR2 → nome de coluna no painel
SECTOR_COLUMN_CODES = {
    "Indústria de transformação": "icf_indtrans",
    "Infraestrutura": "icf_infra",
    "Turismo": "icf_turismo",
    "Indústria extrativa de minerais metálicos": "icf_extmin",
    "Agricultura irrigada": "icf_irrig",
    "Agroindústria": "icf_agro",
}


# ═══════════════════════════════════════════════════════════════════
# Funções de carregamento
# ═══════════════════════════════════════════════════════════════════


def load_sudene(json_path: Path) -> pd.DataFrame:
    """Carrega dados SUDENE do JSON e padroniza colunas.

    Args:
        json_path: Caminho do arquivo if_sudene.json

    Returns:
        DataFrame com colunas padronizadas
    """
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    df = pd.DataFrame(data)
    logger.info(f"SUDENE JSON: {len(df)} registros carregados")

    # Extrair ANO de data_laudo ou data_portaria (DD/MM/YYYY → YYYY)
    def extract_year(row: pd.Series) -> int | None:
        for col in ["data_laudo", "data_portaria", "data_processo"]:
            dt = row.get(col) or ""
            if "/" in str(dt):
                parts = str(dt).split("/")
                if len(parts) == 3 and len(parts[2]) >= 4:
                    try:
                        return int(parts[2][:4])
                    except ValueError:
                        continue
        return None

    df["ANO"] = df.apply(extract_year, axis=1)

    # Padronizar colunas
    result = pd.DataFrame(
        {
            "ORGAO": "SUDENE",
            "EMPRESA": df["razao_social"].fillna(""),
            "CNPJ": df["cnpj"].fillna("").astype(str),
            "MUNICIPIO": df["municipio"].fillna(""),
            "UF": df["uf"].fillna(""),
            "SETOR_ORIG": df["setor_economico_abreviado"].fillna(""),
            "TIPO": df["incentivo"].fillna(""),
            "MODALIDADE": df["tipo_projeto"].fillna(""),
            "ANO": df["ANO"],
        }
    )

    return result


def load_sudam(xlsx_path: Path) -> pd.DataFrame:
    """Carrega dados SUDAM do consolidado e padroniza colunas.

    Args:
        xlsx_path: Caminho do sudam_incentivos_consolidado.xlsx

    Returns:
        DataFrame com colunas padronizadas
    """
    df = pd.read_excel(xlsx_path, dtype={"CNPJ": str})
    logger.info(f"SUDAM consolidado: {len(df)} registros carregados")

    # Padronizar CNPJ
    df["CNPJ"] = df["CNPJ"].fillna("").astype(str).str.replace(r"[^\d]", "", regex=True)

    # Mapear PLEITO → TIPO
    tipo = df["PLEITO"].fillna("").str.strip()
    tipo = tipo.replace(
        {"Redução": "Redução de 75% do IRPJ", "REDUÇÃO": "Redução de 75% do IRPJ"}
    )

    result = pd.DataFrame(
        {
            "ORGAO": "SUDAM",
            "EMPRESA": df["EMPRESA"].fillna(""),
            "CNPJ": df["CNPJ"],
            "MUNICIPIO": df["MUNICIPIO"].fillna(""),
            "UF": df["UF"].fillna(""),
            "SETOR_ORIG": df["SETOR"].fillna(""),
            "ENQUADRAMENTO": df["ENQUADRAMENTO"].fillna(""),
            "TIPO": tipo,
            "MODALIDADE": df["MODALIDADE"].fillna(""),
            "ANO": df["ANO"],
        }
    )

    return result


# ═══════════════════════════════════════════════════════════════════
# Funções de classificação
# ═══════════════════════════════════════════════════════════════════


def classify_sudene_sector(setor_orig: str) -> str:
    """Classifica setor SUDENE em uma das 6 categorias padronizadas.

    Para valores compostos (com separadores " e " ou ", "), usa o primeiro setor.

    Args:
        setor_orig: Valor original de setor_economico_abreviado

    Returns:
        Setor padronizado ou "Outro"
    """
    if not setor_orig or setor_orig.strip() == "":
        return "Outro"

    # Extrair primeiro setor (antes de " e " ou ", " repetido)
    first = re.split(r"\s+e\s+|,\s+", setor_orig)[0].strip()
    if not first:
        return "Outro"

    # Buscar correspondência exata
    if first in SUDENE_SECTOR_MAP:
        return SUDENE_SECTOR_MAP[first]

    # Buscar por substring
    for key, value in SUDENE_SECTOR_MAP.items():
        if key in first:
            return value

    # Fallback: se contém "Indústria de transformação"
    if "Ind" in first and "transforma" in first:
        return "Indústria de transformação"

    logger.debug(f"  Setor SUDENE não mapeado: '{first}' (orig: '{setor_orig[:60]}')")
    return "Outro"


def classify_sudam_sector(enquadramento: str, setor_orig: str) -> str:
    """Classifica setor SUDAM via ENQUADRAMENTO (Decreto 4.212/2002).

    Usa regex para extrair inciso (numeral romano) e alínea, evitando
    falsos positivos de substring (ex: "V" em "VII").

    Args:
        enquadramento: Artigo de enquadramento legal (ex: "Art 2°, Inciso VII")
        setor_orig: Valor original da coluna SETOR (IND, SERV, etc.)

    Returns:
        Setor padronizado ou "Outro"
    """
    enq = str(enquadramento).strip() if enquadramento else ""

    if enq:
        enq_upper = enq.upper()

        # Extrair inciso com regex preciso (word boundary para evitar V ⊂ VII)
        inciso_match = re.search(
            r"INCISO\s+(IX|VII|VI|IV|V|III|II|I)\b", enq_upper
        )
        if inciso_match:
            inciso = inciso_match.group(1)

            # Extrair alínea se presente
            alinea_match = re.search(
                r'AL[IÍ\u00cd]NEA\s*["\u201c\']?\s*(\w)\s*["\u201d\']?', enq_upper
            )

            if inciso == "I":
                return "Infraestrutura"
            elif inciso == "III":
                return "Turismo"
            elif inciso == "V":
                return "Indústria extrativa de minerais metálicos"
            elif inciso == "VI":
                if alinea_match:
                    alinea = alinea_match.group(1).lower()
                    if alinea == "a":
                        return "Agricultura irrigada"
                    elif alinea == "h":
                        return "Agroindústria"
                    else:
                        return "Indústria de transformação"
                # Inciso VI sem alínea → ind. transformação (genérico)
                return "Indústria de transformação"
            elif inciso == "VII":
                return "Indústria de transformação"
            elif inciso == "IX":
                return "Indústria de transformação"

    # Fallback: usar coluna SETOR original
    setor = str(setor_orig).strip().upper() if setor_orig else ""
    if setor in ("IND", "IND."):
        return "Indústria de transformação"
    elif setor == "SERV":
        return "Infraestrutura"

    return "Outro"


def normalize_modalidade(mod: str) -> str:
    """Normaliza variações de modalidade para nomes padronizados.

    Args:
        mod: Modalidade original

    Returns:
        Modalidade normalizada
    """
    if not mod:
        return ""
    mod = mod.strip()

    # Mapeamento de variações comuns
    variations = {
        "Modernização": "Modernização Total",
        "Modernizacao Total": "Modernização Total",
        "Modernizacao Parcial": "Modernização Parcial",
        "Complementação de Equipamentos": "Modernização Parcial",
        "Complementação de equipamentos": "Modernização Parcial",
        "Complementa ção de equipamento s": "Modernização Parcial",
        "Complementa ção de Equipamento s": "Modernização Parcial",
        "Moderniza ção de equipamento s": "Modernização Total",
        "Moderniza\u00e7\u00e3o de equipamento s": "Modernização Total",
        "Ampliacao": "Ampliação",
        "Diversificacao": "Diversificação",
        "Implantacao": "Implantação",
    }

    if mod in variations:
        return variations[mod]

    # Tentar match por início de string
    mod_lower = mod.lower()
    if "implanta" in mod_lower:
        return "Implantação"
    if "amplia" in mod_lower:
        return "Ampliação"
    if "diversifica" in mod_lower:
        return "Diversificação"
    if "moderniza" in mod_lower:
        if "parcial" in mod_lower:
            return "Modernização Parcial"
        return "Modernização Total"
    if "complement" in mod_lower:
        return "Modernização Parcial"

    return mod


# ═══════════════════════════════════════════════════════════════════
# Pipeline principal
# ═══════════════════════════════════════════════════════════════════


def process_if_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Pipeline principal de processamento de IF.

    Returns:
        Tupla (consolidado filtrado, resumo por órgão/setor)
    """
    # 1. Carregar dados
    sudene_path = DATA_DIR / "if_sudene.json"
    sudam_path = DATA_DIR / "if_sudam" / "sudam_incentivos_consolidado.xlsx"

    if not sudene_path.exists():
        raise FileNotFoundError(f"SUDENE JSON não encontrado: {sudene_path}")
    if not sudam_path.exists():
        raise FileNotFoundError(f"SUDAM consolidado não encontrado: {sudam_path}")

    sudene = load_sudene(sudene_path)
    sudam = load_sudam(sudam_path)

    # 2. Unificar colunas (SUDAM tem ENQUADRAMENTO extra)
    if "ENQUADRAMENTO" not in sudene.columns:
        sudene["ENQUADRAMENTO"] = ""

    combined = pd.concat([sudene, sudam], ignore_index=True)
    logger.info(f"Combinado: {len(combined)} registros ({len(sudene)} SUDENE + {len(sudam)} SUDAM)")

    # 3. Filtrar por período
    combined = combined[combined["ANO"].notna()]
    combined["ANO"] = combined["ANO"].astype(int)
    before_year = len(combined)
    combined = combined[
        (combined["ANO"] >= ANALYSIS_PERIOD[0]) & (combined["ANO"] <= ANALYSIS_PERIOD[1])
    ]
    logger.info(f"Filtro período {ANALYSIS_PERIOD}: {before_year} → {len(combined)}")

    # 4. Filtrar por UF (excluir estados fora da área de atuação)
    before_uf = len(combined)
    combined = combined[~combined["UF"].isin(EXCLUDED_UFS)]
    logger.info(f"Filtro UF: {before_uf} → {len(combined)}")

    # 5. Filtrar por tipo de incentivo (Redução 75% IRPJ)
    before_tipo = len(combined)
    tipo_mask = combined["TIPO"].str.contains(
        "|".join(VALID_TIPO_PATTERNS), case=False, na=False
    )
    # SUDAM: todos os registros já são de redução (extraídos dos PDFs de "Redução e Isenção")
    sudam_mask = combined["ORGAO"] == "SUDAM"
    combined = combined[tipo_mask | sudam_mask]
    combined["TIPO"] = "Redução de 75% do IRPJ"
    logger.info(f"Filtro tipo: {before_tipo} → {len(combined)}")

    # 6. Normalizar e filtrar modalidade
    combined["MODALIDADE"] = combined["MODALIDADE"].apply(normalize_modalidade)
    before_mod = len(combined)
    combined = combined[combined["MODALIDADE"].isin(VALID_MODALIDADES)]
    logger.info(f"Filtro modalidade: {before_mod} → {len(combined)}")

    # 7. Classificar setores
    def classify_sector(row: pd.Series) -> str:
        if row["ORGAO"] == "SUDENE":
            return classify_sudene_sector(row["SETOR_ORIG"])
        return classify_sudam_sector(row.get("ENQUADRAMENTO", ""), row["SETOR_ORIG"])

    combined["SETOR2"] = combined.apply(classify_sector, axis=1)

    # Reportar setores não classificados
    outros = combined[combined["SETOR2"] == "Outro"]
    if len(outros) > 0:
        logger.warning(f"  {len(outros)} registros com setor 'Outro' ({100*len(outros)/len(combined):.1f}%)")

    logger.info(f"\nRegistros finais: {len(combined)}")
    logger.info(f"  SUDENE: {(combined['ORGAO'] == 'SUDENE').sum()}")
    logger.info(f"  SUDAM:  {(combined['ORGAO'] == 'SUDAM').sum()}")

    # 8. Gerar resumo por órgão e setor
    resumo = (
        combined.groupby(["ORGAO", "SETOR2"])
        .agg(
            QUANTIDADE=("EMPRESA", "count"),
            N_MUNICIPIOS=("MUNICIPIO", "nunique"),
            N_UFS=("UF", "nunique"),
        )
        .reset_index()
    )

    # Adicionar resumo por ano
    resumo_ano = (
        combined.groupby(["ANO", "ORGAO"])
        .size()
        .reset_index(name="QUANTIDADE")
    )

    return combined, resumo


def save_outputs(
    consolidado: pd.DataFrame, resumo: pd.DataFrame
) -> None:
    """Salva os DataFrames de saída em Excel.

    Args:
        consolidado: DataFrame com todos os registros filtrados
        resumo: DataFrame resumo por órgão/setor
    """
    # Consolidado
    out_consolidado = DATA_DIR / "if_consolidado.xlsx"
    consolidado_out = consolidado[
        ["ORGAO", "EMPRESA", "CNPJ", "MUNICIPIO", "UF", "SETOR2", "TIPO", "MODALIDADE", "ANO"]
    ].copy()
    consolidado_out["CNPJ"] = consolidado_out["CNPJ"].astype(str)
    consolidado_out.to_excel(out_consolidado, index=False, sheet_name="incentivos_fiscais")
    logger.info(f"Salvo: {out_consolidado} ({len(consolidado_out)} registros)")

    # Resumo
    out_resumo = DATA_DIR / "resumo_icf.xlsx"
    with pd.ExcelWriter(out_resumo) as writer:
        resumo.to_excel(writer, index=False, sheet_name="por_orgao_setor")

        # Sheet adicional: por ano e órgão
        resumo_ano = (
            consolidado.groupby(["ANO", "ORGAO"])
            .size()
            .reset_index(name="QUANTIDADE")
        )
        resumo_ano.to_excel(writer, index=False, sheet_name="por_ano_orgao")

        # Sheet adicional: por ano e setor
        resumo_setor = (
            consolidado.groupby(["ANO", "SETOR2"])
            .size()
            .reset_index(name="QUANTIDADE")
        )
        resumo_setor.to_excel(writer, index=False, sheet_name="por_ano_setor")

    logger.info(f"Salvo: {out_resumo}")


def main() -> int:
    """Ponto de entrada principal."""
    parser = argparse.ArgumentParser(
        description="Processa dados de Incentivos Fiscais (SUDENE + SUDAM)"
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
        consolidado, resumo = process_if_data()
        save_outputs(consolidado, resumo)

        # Resumo final
        logger.info("\n" + "=" * 60)
        logger.info("RESUMO DE INCENTIVOS FISCAIS")
        logger.info("=" * 60)
        logger.info(f"Período: {ANALYSIS_PERIOD[0]}-{ANALYSIS_PERIOD[1]}")
        logger.info(f"Total: {len(consolidado)} incentivos")

        for orgao in ["SUDENE", "SUDAM"]:
            subset = consolidado[consolidado["ORGAO"] == orgao]
            logger.info(f"\n{orgao}: {len(subset)} incentivos")
            for setor, count in subset["SETOR2"].value_counts().items():
                logger.info(f"  {setor}: {count}")

        logger.info(f"\nDistribuição por ano:")
        for ano, count in sorted(consolidado.groupby("ANO").size().items()):
            logger.info(f"  {ano}: {count}")

        return 0

    except Exception:
        logger.exception("Erro ao processar dados de IF")
        return 1


if __name__ == "__main__":
    import sys

    sys.exit(main())
