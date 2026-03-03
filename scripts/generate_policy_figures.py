#!/usr/bin/env python3
"""Gera figuras de política regional para o artigo LaTeX.

Produz gráficos de barras empilhadas para os instrumentos da PNDR:
  - FC (Fundos Constitucionais) por fundo, setor e tipologia
  - FD (Fundos de Desenvolvimento) por fundo e setor
  - IF (Incentivos Fiscais) por órgão e setor

Entrada:
    data/external_data/resumo_fc.xlsx      (resumo FC)
    data/external_data/resumo_fd.xlsx      (resumo FD)
    data/external_data/resumo_icf.xlsx     (resumo IF)
    data/external_data/if_consolidado.xlsx  (IF detalhado)

Saída:
    figures/fc_setor_tipologia.png         (FC por setor/tipologia)
    figures/fd_fundo_setor.png             (FD por fundo/setor)
    figures/if_orgao_setor.png             (IF por órgão/setor)

Referência R:
    tese/bulding_dataset_R/source_code/grafico_resumo_fc.R
    tese/bulding_dataset_R/source_code/grafico_resumo_fd.R

Uso:
    python generate_policy_figures.py
    python generate_policy_figures.py --only fc
    python generate_policy_figures.py --only fd
    python generate_policy_figures.py --only if
"""

from __future__ import annotations

import argparse
import logging
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd

matplotlib.use("Agg")

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "external_data"
FIGURES_DIR = PROJECT_ROOT / "figures"

# Paleta de cores para setores (similar ao RColorBrewer Set3)
SECTOR_COLORS = {
    "Infraestrutura": "#8DD3C7",
    "Indústria de transformação": "#FFFFB3",
    "Indústria extrativa": "#BEBADA",
    "Indústria extrativa de minerais metálicos": "#BEBADA",
    "Agroindústria": "#FB8072",
    "Turismo": "#80B1D3",
    "Agricultura irrigada": "#B3DE69",
    "Serviços": "#FDB462",
    "Outro": "#D9D9D9",
}

# Formatação numérica brasileira
def fmt_br(x: float, pos: int | None = None) -> str:
    """Formata número no padrão brasileiro (ponto para milhar, vírgula para decimal)."""
    if x == 0:
        return "0"
    return f"{x:,.1f}".replace(",", "X").replace(".", ",").replace("X", ".")


def generate_fc_figure() -> Path:
    """Gera figura FC por setor e tipologia (3 painéis: FNE, FNO, FCO).

    Barras empilhadas por tipologia, coloridas por setor.
    Linha vermelha de per capita no eixo secundário.

    Referência R: grafico_resumo_fc.R

    Returns:
        Caminho da figura salva
    """
    resumo_path = DATA_DIR / "resumo_fc.xlsx"
    setor_tip = pd.read_excel(resumo_path, sheet_name="por_fundo_setor_tipologia")
    medias_pc = pd.read_excel(resumo_path, sheet_name="medias_pc_tipologia")

    fundos = ["FNE", "FNO", "FCO"]
    tipologias = ["Alta Renda", "Baixa Renda", "Dinâmica", "Estagnada"]
    tip_labels = {"Alta Renda": "Alta\nRenda", "Baixa Renda": "Baixa\nRenda",
                  "Dinâmica": "Dinâmica", "Estagnada": "Estagnada"}

    # RColorBrewer Set3 (12 cores)
    set3_colors = [
        "#8DD3C7", "#FFFFB3", "#BEBADA", "#FB8072", "#80B1D3", "#FDB462",
        "#B3DE69", "#FCCDE5", "#D9D9D9", "#BC80BD", "#CCEBC5", "#FFED6F",
    ]

    # Escala Y comum: máximo total por (fundo, tipologia)
    max_vals = []
    for fundo in fundos:
        df_f = setor_tip[setor_tip["INSTR"] == fundo]
        for tip in tipologias:
            total = df_f[df_f["tipologia2007"] == tip]["valor_bi"].sum()
            if total > 0:
                max_vals.append(total)
    limite_y = max(max_vals) * 1.05 if max_vals else 1

    # Escala per capita comum
    max_pc = medias_pc["pc_media"].max() if len(medias_pc) > 0 else 1
    limite_pc = max_pc * 1.1

    fig, axes = plt.subplots(1, 3, figsize=(18, 7), sharey=True)

    color_offset = {
        "FNE": 0,    # cores 0-7 (8 setores)
        "FNO": 3,    # cores 3-5 (3 setores)
        "FCO": 6,    # cores 6-7 (2 setores)
    }

    for ax_idx, fundo in enumerate(fundos):
        ax = axes[ax_idx]
        df_f = setor_tip[setor_tip["INSTR"] == fundo]

        # Tipologias presentes para este fundo
        tips_presentes = [t for t in tipologias
                          if df_f[df_f["tipologia2007"] == t]["valor_bi"].sum() > 0]

        # Setores ordenados por valor total (decrescente)
        setores_order = (
            df_f.groupby("setor2")["valor_bi"].sum()
            .sort_values(ascending=False)
            .index.tolist()
        )

        # Atribuir cores
        offset = color_offset[fundo]
        cores_setor = {s: set3_colors[(offset + i) % len(set3_colors)]
                       for i, s in enumerate(setores_order)}

        x = np.arange(len(tips_presentes))
        x_labels = [tip_labels.get(t, t) for t in tips_presentes]
        width = 0.7
        bottom = np.zeros(len(tips_presentes))

        for setor in setores_order:
            values = []
            for tip in tips_presentes:
                val = df_f[(df_f["tipologia2007"] == tip) & (df_f["setor2"] == setor)]["valor_bi"].sum()
                values.append(val)
            values = np.array(values)
            ax.bar(x, values, width, bottom=bottom, label=setor,
                   color=cores_setor[setor], edgecolor="white", linewidth=0.5)
            bottom += values

        # Linha per capita (eixo secundário via escala)
        pc_data = medias_pc[medias_pc["INSTR"] == fundo]
        pc_vals = []
        for tip in tips_presentes:
            row = pc_data[pc_data["tipologia2007"] == tip]
            pc_vals.append(float(row["pc_media"].iloc[0]) if len(row) > 0 else 0)

        # Escalar per capita para o eixo Y principal
        pc_scaled = [max(0, v / limite_pc * limite_y) for v in pc_vals]
        ax.plot(x, pc_scaled, color="red", linewidth=1.2, marker="o",
                markersize=5, zorder=5)

        ax.set_xticks(x)
        ax.set_xticklabels(x_labels, fontsize=13)
        ax.set_title(fundo, fontsize=16)
        ax.set_ylim(0, limite_y)

        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.grid(axis="y", alpha=0.3, linestyle="--")
        ax.tick_params(axis="both", labelsize=12)

        if ax_idx == 0:
            ax.set_ylabel("Valor (R$ bilhões)", fontsize=14)
            ax.yaxis.set_major_formatter(mticker.FuncFormatter(fmt_br))
        else:
            ax.tick_params(axis="y", labelleft=False)

        # Eixo secundário per capita (apenas no último painel)
        if ax_idx == 2:
            ax2 = ax.twinx()
            ax2.set_ylim(0, limite_pc)
            ax2.set_ylabel("Per Capita (R$)", fontsize=14)
            ax2.yaxis.set_major_formatter(mticker.FuncFormatter(
                lambda v, p: f"{v:,.0f}".replace(",", ".") if v >= 1 else "0"
            ))
            ax2.tick_params(axis="y", labelsize=12)
            ax2.spines["top"].set_visible(False)

        # Legenda individual por painel (abaixo)
        ax.legend(
            loc="upper center",
            bbox_to_anchor=(0.5, -0.12),
            ncol=min(4, len(setores_order)),
            fontsize=10,
            frameon=False,
        )

    plt.tight_layout()

    out_path = FIGURES_DIR / "fc_setor_tipologia.png"
    fig.savefig(out_path, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)

    logger.info(f"Figura FC salva: {out_path}")
    return out_path


def generate_fd_figure() -> Path:
    """Gera figura FD por fundo e setor.

    Stacked bar chart: FDNE, FDA, FDCO por setor
    Valores em R$ bilhões liberados.

    Returns:
        Caminho da figura salva
    """
    resumo_path = DATA_DIR / "resumo_fd.xlsx"
    df = pd.read_excel(resumo_path, sheet_name="por_fundo_setor")

    # Filtrar apenas dados por setor (excluir TOTAL)
    df = df[df["SETOR2"] != "TOTAL"].copy()

    # Converter para bilhões
    df["valor_bi"] = df["VALOR_LIBERADO"] / 1e9

    # Pivot: setor como colunas, fundo como linhas
    fundos = ["FDNE", "FDA", "FDCO"]
    setores = [s for s in df["SETOR2"].unique() if s != "Outro"]
    # Adicionar "Outro" no final se existir
    if "Outro" in df["SETOR2"].values:
        setores.append("Outro")

    pivot = df.pivot_table(
        index="FUNDO", columns="SETOR2", values="valor_bi", fill_value=0
    )
    pivot = pivot.reindex(fundos)  # Garantir ordem
    pivot = pivot.fillna(0)

    # Criar figura
    fig, ax = plt.subplots(figsize=(10, 5.5))

    x = np.arange(len(fundos))
    width = 0.6
    bottom = np.zeros(len(fundos))

    for setor in setores:
        if setor in pivot.columns:
            values = pivot[setor].values
            color = SECTOR_COLORS.get(setor, "#D9D9D9")
            ax.bar(x, values, width, bottom=bottom, label=setor, color=color, edgecolor="white", linewidth=0.5)
            bottom += values

    ax.set_xticks(x)
    ax.set_xticklabels(fundos, fontsize=14)
    ax.set_ylabel("Valor liberado (R$ bilhões)", fontsize=13)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(fmt_br))
    ax.set_ylim(0, max(bottom) * 1.1)

    # Estilo
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", alpha=0.3, linestyle="--")
    ax.tick_params(axis="both", labelsize=12)

    # Legenda
    ax.legend(
        loc="upper center",
        bbox_to_anchor=(0.5, -0.12),
        ncol=min(3, len(setores)),
        fontsize=11,
        frameon=False,
    )

    # Adicionar valores totais no topo das barras
    for i, total in enumerate(bottom):
        if total > 0:
            ax.text(i, total + 0.05, f"R$ {fmt_br(total)} bi",
                    ha="center", va="bottom", fontsize=10, fontweight="bold")

    plt.tight_layout()

    out_path = FIGURES_DIR / "fd_fundo_setor.png"
    fig.savefig(out_path, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)

    logger.info(f"Figura FD salva: {out_path}")
    return out_path


def generate_if_figure() -> Path:
    """Gera figura IF por órgão e setor.

    Stacked bar chart: SUDENE vs SUDAM, empilhado por setor.

    Returns:
        Caminho da figura salva
    """
    consolidado_path = DATA_DIR / "if_consolidado.xlsx"
    df = pd.read_excel(consolidado_path, dtype={"CNPJ": str})

    # Contar por órgão e setor
    counts = df.groupby(["ORGAO", "SETOR2"]).size().reset_index(name="QUANTIDADE")

    orgaos = ["SUDENE", "SUDAM"]
    setores_order = [
        "Indústria de transformação",
        "Infraestrutura",
        "Agroindústria",
        "Turismo",
        "Agricultura irrigada",
        "Indústria extrativa de minerais metálicos",
        "Outro",
    ]
    # Filtrar setores presentes
    setores = [s for s in setores_order if s in counts["SETOR2"].values]

    pivot = counts.pivot_table(
        index="ORGAO", columns="SETOR2", values="QUANTIDADE", fill_value=0
    )
    pivot = pivot.reindex(orgaos).fillna(0)

    fig, ax = plt.subplots(figsize=(10, 5.5))

    x = np.arange(len(orgaos))
    width = 0.5
    bottom = np.zeros(len(orgaos))

    for setor in setores:
        if setor in pivot.columns:
            values = pivot[setor].values
            color = SECTOR_COLORS.get(setor, "#D9D9D9")
            ax.bar(x, values, width, bottom=bottom, label=setor, color=color, edgecolor="white", linewidth=0.5)
            bottom += values

    ax.set_xticks(x)
    ax.set_xticklabels(orgaos, fontsize=14)
    ax.set_ylabel("Quantidade de incentivos", fontsize=13)
    ax.set_ylim(0, max(bottom) * 1.12)

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", alpha=0.3, linestyle="--")
    ax.tick_params(axis="both", labelsize=12)

    ax.legend(
        loc="upper center",
        bbox_to_anchor=(0.5, -0.12),
        ncol=min(3, len(setores)),
        fontsize=10,
        frameon=False,
    )

    # Totais
    for i, total in enumerate(bottom):
        if total > 0:
            ax.text(i, total + 20, f"{int(total):,}".replace(",", "."),
                    ha="center", va="bottom", fontsize=11, fontweight="bold")

    plt.tight_layout()

    out_path = FIGURES_DIR / "if_orgao_setor.png"
    fig.savefig(out_path, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)

    logger.info(f"Figura IF salva: {out_path}")
    return out_path


def generate_if_timeseries() -> Path:
    """Gera série temporal de IF por ano e órgão.

    Barras empilhadas: SUDENE + SUDAM por ano.

    Returns:
        Caminho da figura salva
    """
    consolidado_path = DATA_DIR / "if_consolidado.xlsx"
    df = pd.read_excel(consolidado_path, dtype={"CNPJ": str})

    counts = df.groupby(["ANO", "ORGAO"]).size().reset_index(name="QUANTIDADE")
    pivot = counts.pivot_table(index="ANO", columns="ORGAO", values="QUANTIDADE", fill_value=0)

    fig, ax = plt.subplots(figsize=(12, 5))

    anos = pivot.index
    x = np.arange(len(anos))
    width = 0.7

    # SUDENE na base, SUDAM em cima
    sudene_vals = pivot.get("SUDENE", pd.Series(0, index=anos)).values
    sudam_vals = pivot.get("SUDAM", pd.Series(0, index=anos)).values

    ax.bar(x, sudene_vals, width, label="SUDENE", color="#80B1D3", edgecolor="white", linewidth=0.5)
    ax.bar(x, sudam_vals, width, bottom=sudene_vals, label="SUDAM", color="#FB8072", edgecolor="white", linewidth=0.5)

    ax.set_xticks(x)
    ax.set_xticklabels([str(int(a)) for a in anos], fontsize=10, rotation=45)
    ax.set_ylabel("Quantidade de incentivos", fontsize=13)

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", alpha=0.3, linestyle="--")
    ax.tick_params(axis="both", labelsize=11)

    ax.legend(fontsize=12, frameon=False, loc="upper left")

    plt.tight_layout()

    out_path = FIGURES_DIR / "if_evolucao_anual.png"
    fig.savefig(out_path, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)

    logger.info(f"Figura IF série temporal salva: {out_path}")
    return out_path


def main() -> int:
    """Ponto de entrada principal."""
    parser = argparse.ArgumentParser(
        description="Gera figuras de política regional para o artigo"
    )
    parser.add_argument(
        "--only", choices=["fc", "fd", "if"], help="Gerar apenas um tipo de figura"
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Logging detalhado"
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s: %(message)s",
    )

    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    try:
        generated: list[Path] = []

        if args.only is None or args.only == "fc":
            logger.info("Gerando figura FC...")
            generated.append(generate_fc_figure())

        if args.only is None or args.only == "fd":
            logger.info("Gerando figura FD...")
            generated.append(generate_fd_figure())

        if args.only is None or args.only == "if":
            logger.info("Gerando figuras IF...")
            generated.append(generate_if_figure())
            generated.append(generate_if_timeseries())

        logger.info(f"\n{len(generated)} figuras geradas com sucesso")
        return 0

    except Exception:
        logger.exception("Erro ao gerar figuras")
        return 1


if __name__ == "__main__":
    import sys

    sys.exit(main())
