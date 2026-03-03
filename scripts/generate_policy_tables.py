#!/usr/bin/env python3
"""Gera tabelas LaTeX de política regional para o artigo.

Produz tabelas formatadas (abntex2 + booktabs) a partir dos dados processados:
  - FD: Resumo por fundo e setor (valor contratado e liberado)
  - IF: Resumo por órgão e setor (quantidade de incentivos)

Entrada:
    data/external_data/resumo_fd.xlsx
    data/external_data/if_consolidado.xlsx

Saída:
    latex/tabelas/fd_tabela_resumo.tex
    latex/tabelas/if_tabela_resumo.tex

Uso:
    python generate_policy_tables.py
"""

from __future__ import annotations

import argparse
import logging
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "external_data"
TABELAS_DIR = PROJECT_ROOT / "latex" / "tabelas"


def fmt_valor(x: float, divisor: float = 1e6) -> str:
    """Formata valor monetário para a tabela (R$ milhões/bilhões).

    Args:
        x: Valor em reais
        divisor: Divisor (1e6 para milhões, 1e9 para bilhões)

    Returns:
        String formatada no padrão brasileiro
    """
    val = x / divisor
    if val >= 100:
        return f"{val:,.0f}".replace(",", ".")
    elif val >= 1:
        return f"{val:,.1f}".replace(",", "X").replace(".", ",").replace("X", ".")
    else:
        return f"{val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def fmt_int(x: int) -> str:
    """Formata inteiro com separador de milhares."""
    return f"{x:,}".replace(",", ".")


def generate_fd_table() -> Path:
    """Gera tabela LaTeX de resumo dos Fundos de Desenvolvimento.

    Returns:
        Caminho do arquivo gerado
    """
    resumo = pd.read_excel(DATA_DIR / "resumo_fd.xlsx", sheet_name="por_fundo_setor")
    resumo = resumo[resumo["SETOR2"] != "TOTAL"].copy()

    # Preparar dados por fundo
    fundos = {
        "FDNE": {"gestor": "SUDENE", "regiao": "Nordeste"},
        "FDA": {"gestor": "SUDAM", "regiao": "Amazônia"},
        "FDCO": {"gestor": "SUDECO", "regiao": "Centro-Oeste"},
    }

    tex_lines = [
        r"\begin{table}[h!]",
        r"	\centering",
        r"	\caption{Resumo dos Fundos de Desenvolvimento Regional}",
        r"	\label{tab:resumo_fd}",
        r"	\footnotesize",
        r"	\renewcommand{\arraystretch}{1.2}",
        r"	\begin{tabular}{llrrr}",
        r"		\toprule",
        r"		Fundo & Setor & Projetos & \makecell{Valor contratado \\ (R\$ milhões)} & \makecell{Valor liberado \\ (R\$ milhões)} \\",
        r"		\midrule",
    ]

    for fundo in ["FDNE", "FDA", "FDCO"]:
        subset = resumo[resumo["FUNDO"] == fundo].copy()
        if subset.empty:
            continue

        n_rows = len(subset)
        first = True
        for _, row in subset.iterrows():
            setor = row["SETOR2"]
            n_proj = int(row["N_PROJETOS"])
            v_contr = row.get("VALOR_CONTRATADO", 0)
            v_lib = row.get("VALOR_LIBERADO", 0)

            if first:
                prefix = rf"		\multirow{{{n_rows}}}{{*}}{{{fundo}}}"
                first = False
            else:
                prefix = r"		"

            tex_lines.append(
                f"{prefix} & {setor} & {n_proj} & {fmt_valor(v_contr)} & {fmt_valor(v_lib)} \\\\"
            )

        # Subtotal por fundo
        total_proj = int(subset["N_PROJETOS"].sum())
        total_contr = subset["VALOR_CONTRATADO"].sum() if "VALOR_CONTRATADO" in subset.columns else 0
        total_lib = subset["VALOR_LIBERADO"].sum() if "VALOR_LIBERADO" in subset.columns else 0
        tex_lines.append(
            rf"		& \textit{{Total}} & \textit{{{total_proj}}} & \textit{{{fmt_valor(total_contr)}}} & \textit{{{fmt_valor(total_lib)}}} \\"
        )

        # Separador entre fundos (exceto o último)
        if fundo != "FDCO":
            tex_lines.append(r"		\midrule")

    tex_lines.extend([
        r"		\bottomrule",
        r"		\multicolumn{5}{l}{\footnotesize{Fonte: Elaborada pelo autor a partir de dados de SUDENE, SUDAM e SUDECO.}} \\",
        r"	\end{tabular}",
        r"\end{table}",
    ])

    out_path = TABELAS_DIR / "fd_tabela_resumo.tex"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(tex_lines), encoding="utf-8")

    logger.info(f"Tabela FD salva: {out_path}")
    return out_path


def generate_if_table() -> Path:
    """Gera tabela LaTeX de resumo dos Incentivos Fiscais.

    Returns:
        Caminho do arquivo gerado
    """
    consolidado = pd.read_excel(
        DATA_DIR / "if_consolidado.xlsx", dtype={"CNPJ": str}
    )

    # Contar por órgão e setor
    counts = (
        consolidado.groupby(["ORGAO", "SETOR2"])
        .agg(
            QUANTIDADE=("EMPRESA", "count"),
            N_UFS=("UF", "nunique"),
            N_MUNICIPIOS=("MUNICIPIO", "nunique"),
        )
        .reset_index()
        .sort_values(["ORGAO", "QUANTIDADE"], ascending=[True, False])
    )

    setores_order = [
        "Indústria de transformação",
        "Infraestrutura",
        "Agroindústria",
        "Turismo",
        "Agricultura irrigada",
        "Indústria extrativa de minerais metálicos",
        "Outro",
    ]

    tex_lines = [
        r"\begin{table}[h!]",
        r"	\centering",
        r"	\caption{Incentivos fiscais por superintendência e setor (2010--2023)}",
        r"	\label{tab:resumo_if}",
        r"	\footnotesize",
        r"	\renewcommand{\arraystretch}{1.2}",
        r"	\begin{tabular}{llrr}",
        r"		\toprule",
        r"		Superintendência & Setor & Incentivos & UFs \\",
        r"		\midrule",
    ]

    for orgao in ["SUDENE", "SUDAM"]:
        subset = counts[counts["ORGAO"] == orgao].copy()
        # Reordenar por setores_order
        subset["sort_key"] = subset["SETOR2"].apply(
            lambda s: setores_order.index(s) if s in setores_order else 99
        )
        subset = subset.sort_values("sort_key")

        n_rows = len(subset)
        first = True

        for _, row in subset.iterrows():
            setor = row["SETOR2"]
            # Abreviar nome longo
            if setor == "Indústria extrativa de minerais metálicos":
                setor = "Indústria extrativa"
            qtd = int(row["QUANTIDADE"])
            n_ufs = int(row["N_UFS"])

            if first:
                prefix = rf"		\multirow{{{n_rows}}}{{*}}{{{orgao}}}"
                first = False
            else:
                prefix = r"		"

            tex_lines.append(
                f"{prefix} & {setor} & {fmt_int(qtd)} & {n_ufs} \\\\"
            )

        # Subtotal
        total_qtd = int(subset["QUANTIDADE"].sum())
        total_ufs = int(consolidado[consolidado["ORGAO"] == orgao]["UF"].nunique())
        tex_lines.append(
            rf"		& \textit{{Total}} & \textit{{{fmt_int(total_qtd)}}} & \textit{{{total_ufs}}} \\"
        )

        if orgao != "SUDAM":
            tex_lines.append(r"		\midrule")

    tex_lines.extend([
        r"		\bottomrule",
        r"		\multicolumn{4}{l}{\footnotesize{Fonte: Elaborada pelo autor a partir de dados de SUDENE e SUDAM.}} \\",
        r"	\end{tabular}",
        r"\end{table}",
    ])

    out_path = TABELAS_DIR / "if_tabela_resumo.tex"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(tex_lines), encoding="utf-8")

    logger.info(f"Tabela IF salva: {out_path}")
    return out_path


def main() -> int:
    """Ponto de entrada principal."""
    parser = argparse.ArgumentParser(
        description="Gera tabelas LaTeX de política regional"
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
        generated: list[Path] = []

        logger.info("Gerando tabela FD...")
        generated.append(generate_fd_table())

        logger.info("Gerando tabela IF...")
        generated.append(generate_if_table())

        logger.info(f"\n{len(generated)} tabelas geradas com sucesso")
        return 0

    except Exception:
        logger.exception("Erro ao gerar tabelas")
        return 1


if __name__ == "__main__":
    import sys

    sys.exit(main())
