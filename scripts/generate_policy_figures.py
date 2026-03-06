#!/usr/bin/env python3
"""Gera figuras de política regional para o artigo LaTeX.

Produz gráficos de barras empilhadas para os instrumentos da PNDR:
  - FC (Fundos Constitucionais) por fundo, setor e tipologia
  - FD (Fundos de Desenvolvimento) por fundo, setor e tipologia
  - IF (Incentivos Fiscais) por superintendência, tipologia e setor

Entrada (todos locais em data/external_data/):
    resumo_fc.xlsx              (resumo FC)
    resumo_fd.xlsx              (resumo FD: tipologia, setor, % PIB)
    classif_incent_fiscais.xlsx (classificação ICF por superintendência)
    if_consolidado.xlsx         (IF detalhado, série temporal)

Saída:
    figures/fc_setor_tipologia.png   (FC por setor/tipologia)
    figures/fd_fundo_setor.png       (FD por fundo/setor/tipologia + % PIB)
    figures/icf_superint_setor.png   (IF por superintendência/tipologia/setor)
    figures/if_evolucao_anual.png    (IF série temporal por órgão)

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

plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Times New Roman", "DejaVu Serif"],
})

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
    return f"{x:,.0f}".replace(",", ".")


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
    """Gera figura FD por fundo, setor e tipologia (3 painéis: FDNE, FDA, FDCO).

    Barras empilhadas por tipologia, coloridas por setor.
    Linha vermelha de participação % média no PIB local no eixo secundário.
    Layout inspirado em ggplot2 theme_minimal (grafico_resumo_fd.R).

    Referência R: grafico_resumo_fd.R

    Returns:
        Caminho da figura salva
    """
    resumo_path = DATA_DIR / "resumo_fd.xlsx"
    setor_tip = pd.read_excel(resumo_path, sheet_name="por_fundo_setor_tipologia")
    medias_pib = pd.read_excel(resumo_path, sheet_name="medias_pib_tipologia")

    fundos = ["FDNE", "FDA", "FDCO"]
    tipologias = ["Alta Renda", "Baixa Renda", "Dinâmica", "Estagnada"]
    tip_labels = {"Alta Renda": "Alta\nRenda", "Baixa Renda": "Baixa\nRenda",
                  "Dinâmica": "Dinâmica", "Estagnada": "Estagnada"}

    # RColorBrewer Set3 (mesma paleta do R)
    set3_colors = [
        "#8DD3C7", "#FFFFB3", "#BEBADA", "#FB8072", "#80B1D3", "#FDB462",
        "#B3DE69", "#FCCDE5", "#D9D9D9", "#BC80BD", "#CCEBC5", "#FFED6F",
    ]

    # Escala Y comum (fixed, como ggplot facet_wrap scales="fixed")
    max_vals = []
    for fundo in fundos:
        df_f = setor_tip[setor_tip["INSTR"] == fundo]
        for tip in tipologias:
            total = df_f[df_f["tipologia2007"] == tip]["valor_bi"].sum()
            if total > 0:
                max_vals.append(total)
    limite_y = max(max_vals) * 1.05 if max_vals else 1

    # Escala participação PIB comum
    max_pib = medias_pib["pib_media"].max() if len(medias_pib) > 0 else 0.001
    limite_pib = max_pib * 1.1

    # LaTeX textwidth=155mm (~6.1in). Escala = 6.1/14 ≈ 0.44
    # fs=20 → ~8.7pt no documento; fs_x=16 → ~7pt (x-labels menores
    # evitam sobreposição nos 3 painéis, mesmo tamanho da versão R)
    fs = 20
    fs_x = 16  # x-labels precisam de fonte menor nos 3 painéis

    fig, axes = plt.subplots(1, 3, figsize=(14, 6), sharey=True)

    for ax_idx, fundo in enumerate(fundos):
        ax = axes[ax_idx]
        df_f = setor_tip[setor_tip["INSTR"] == fundo]

        # Todas as tipologias (fixed scale como ggplot facet_wrap)
        tips_presentes = tipologias

        # Setores ordenados por valor total (decrescente)
        setores_order = (
            df_f.groupby("SETOR")["valor_bi"].sum()
            .sort_values(ascending=False)
            .index.tolist()
        )

        # Atribuir cores via SECTOR_COLORS (consistente com outros gráficos)
        cores_setor = {}
        fallback_idx = 0
        for s in setores_order:
            if s in SECTOR_COLORS:
                cores_setor[s] = SECTOR_COLORS[s]
            else:
                cores_setor[s] = set3_colors[fallback_idx % len(set3_colors)]
                fallback_idx += 1

        x = np.arange(len(tips_presentes))
        x_labels = [tip_labels.get(t, t) for t in tips_presentes]
        width = 0.8
        bottom = np.zeros(len(tips_presentes))

        for setor in setores_order:
            values = []
            for tip in tips_presentes:
                val = df_f[(df_f["tipologia2007"] == tip) & (df_f["SETOR"] == setor)]["valor_bi"].sum()
                values.append(val)
            values = np.array(values)
            ax.bar(x, values, width, bottom=bottom, label=setor,
                   color=cores_setor[setor], edgecolor="white", linewidth=0.5)
            bottom += values

        # Linha participação PIB (eixo secundário via escala)
        pib_data = medias_pib[medias_pib["INSTR"] == fundo]
        pib_vals = []
        for tip in tips_presentes:
            row = pib_data[pib_data["tipologia2007"] == tip]
            pib_vals.append(float(row["pib_media"].iloc[0]) if len(row) > 0 else 0)

        # Escalar participação PIB para o eixo Y principal
        pib_scaled = [max(0, v / limite_pib * limite_y) for v in pib_vals]
        ax.plot(x, pib_scaled, color="red", linewidth=1.2, marker="o",
                markersize=3, zorder=5)

        ax.set_xticks(x)
        ax.set_xticklabels(x_labels, fontsize=fs_x, ha="center")
        ax.set_title(fundo, fontsize=fs, pad=8)
        ax.set_ylim(0, limite_y)
        ax.set_axisbelow(True)

        for spine in ax.spines.values():
            spine.set_visible(True)
            spine.set_color("black")
            spine.set_linewidth(0.5)
        ax.grid(axis="y", alpha=0.4, linestyle="-", color="gray", linewidth=0.5)
        ax.tick_params(axis="both", labelsize=fs_x)

        if ax_idx == 0:
            ax.set_ylabel("R$ bilhões", fontsize=fs_x)
            ax.yaxis.set_major_formatter(mticker.FuncFormatter(fmt_br))

        # Eixo secundário participação PIB (apenas no último painel)
        if ax_idx == 2:
            ax2 = ax.twinx()
            ax2.set_ylim(0, limite_pib * 100)
            ax2.set_ylabel("% do PIB", fontsize=fs_x)
            for spine in ax2.spines.values():
                spine.set_visible(True)
                spine.set_color("black")
                spine.set_linewidth(0.5)
            # Alinhar ticks do eixo direito com os ticks do eixo esquerdo
            left_ticks = [t for t in axes[0].get_yticks()
                          if 0 <= t <= limite_y]
            right_ticks = [(t / limite_y) * (limite_pib * 100)
                           for t in left_ticks]
            ax2.set_yticks(right_ticks)
            ax2.yaxis.set_major_formatter(mticker.FuncFormatter(
                lambda v, p: f"{v:,.1f}".replace(",", "X").replace(".", ",").replace("X", ".")
            ))
            ax2.tick_params(axis="y", labelsize=fs_x)

    # Legenda: coletar handles/labels únicos de todos os painéis
    handle_map: dict[str, object] = {}
    for ax in axes:
        handles, labels = ax.get_legend_handles_labels()
        for h, l in zip(handles, labels):
            if l not in handle_map:
                handle_map[l] = h

    # Linha 1: setores em ordem explícita
    setor_order = ["Infraestrutura", "Indústria de transformação",
                   "Indústria extrativa", "Serviços"]
    setor_handles = []
    setor_labels = []
    for s in setor_order:
        if s in handle_map:
            setor_handles.append(handle_map[s])
            setor_labels.append(s)

    leg1 = fig.legend(
        setor_handles, setor_labels,
        loc="lower center",
        bbox_to_anchor=(0.5, 0.06),
        ncol=len(setor_handles),
        fontsize=fs,
        frameon=False,
        columnspacing=1.5,
        handletextpad=0.5,
    )

    # Linha 2: indicador PIB
    red_line = plt.Line2D([0], [0], color="red", linewidth=1.2, marker="o", markersize=4)
    fig.legend(
        [red_line], ["Partic. % média no PIB local"],
        loc="lower center",
        bbox_to_anchor=(0.5, 0.0),
        ncol=1,
        fontsize=fs,
        frameon=False,
        handletextpad=0.5,
    )
    fig.add_artist(leg1)  # manter ambas as legendas visíveis

    fig.subplots_adjust(wspace=0.08, bottom=0.28, top=0.93, left=0.07, right=0.93)

    out_path = FIGURES_DIR / "fd_fundo_setor.png"
    fig.savefig(out_path, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)

    logger.info(f"Figura FD salva: {out_path}")
    return out_path


def _compute_icf_per_capita() -> pd.DataFrame:
    """Calcula incentivos fiscais por 100 mil hab. por tipologia e superintendência.

    Usa painel_icf.rds (contagens municipais) e populacao_fc.rds.

    Returns:
        DataFrame com tipologia2007, icf_sudene_pc_media, icf_sudam_pc_media
    """
    try:
        import pyreadr
    except ImportError:
        logger.warning("pyreadr não instalado — per capita IF não calculado")
        return pd.DataFrame()

    painel_path = DATA_DIR / "painel_icf.rds"
    pop_path = DATA_DIR / "populacao_fc.rds"
    tip_path = DATA_DIR / "tipologia_2007.xlsx"

    for p in [painel_path, pop_path, tip_path]:
        if not p.exists():
            logger.warning(f"Arquivo não encontrado: {p}")
            return pd.DataFrame()

    painel = list(pyreadr.read_r(str(painel_path)).values())[0]
    populacao = list(pyreadr.read_r(str(pop_path)).values())[0]

    tip = pd.read_excel(tip_path, sheet_name="Table 1")
    tip = tip.iloc[:, [0, 5]].copy()
    tip.columns = ["id_municipio", "tipologia2007"]
    tip["id_municipio"] = pd.to_numeric(tip["id_municipio"], errors="coerce").astype("Int64")

    merged = (
        painel
        .merge(tip, left_on="COD", right_on="id_municipio", how="left")
        .merge(populacao, left_on=["COD", "ANO"], right_on=["CD_MUN", "ano"], how="left")
    )
    valid = merged[
        merged["tipologia2007"].notna()
        & merged["populacao"].notna()
        & (merged["populacao"] > 0)
    ].copy()

    valid["icf_sudene_pc"] = (valid["icf_sudene"] / valid["populacao"]) * 100_000
    valid["icf_sudam_pc"] = (valid["icf_sudam"] / valid["populacao"]) * 100_000

    medias = (
        valid.groupby("tipologia2007")
        .agg(
            icf_sudene_pc_media=("icf_sudene_pc", "mean"),
            icf_sudam_pc_media=("icf_sudam_pc", "mean"),
        )
        .reset_index()
    )

    logger.info(f"Per capita ICF por tipologia:\n{medias.round(4).to_string(index=False)}")
    return medias


def generate_if_figure() -> Path:
    """Gera figura IF por superintendência, tipologia e setor (2 painéis).

    Barras empilhadas por tipologia, coloridas por setor.
    Linha vermelha de incentivos por 100 mil hab. no eixo secundário.
    Layout inspirado em ggplot2 (grafico_resumo_icf.R).

    Returns:
        Caminho da figura salva
    """
    # Dados de tipologia/setor/superintendência
    classif_path = DATA_DIR / "classif_incent_fiscais.xlsx"
    classif = pd.read_excel(classif_path)

    # Per capita
    medias_pc = _compute_icf_per_capita()

    orgaos = ["SUDENE", "SUDAM"]
    tipologias = ["Alta Renda", "Baixa Renda", "Dinâmica", "Estagnada"]
    tip_labels = {"Alta Renda": "Alta\nRenda", "Baixa Renda": "Baixa\nRenda",
                  "Dinâmica": "Dinâmica", "Estagnada": "Estagnada"}

    setores_order = [
        "Indústria de transformação",
        "Infraestrutura",
        "Indústria extrativa de minerais metálicos",
        "Turismo",
        "Agroindústria",
        "Agricultura irrigada",
    ]

    # RColorBrewer Set3
    set3_colors = [
        "#8DD3C7", "#FFFFB3", "#BEBADA", "#FB8072", "#80B1D3", "#FDB462",
        "#B3DE69", "#FCCDE5", "#D9D9D9", "#BC80BD", "#CCEBC5", "#FFED6F",
    ]

    # Pivotar classif para long format: tipologia, setor, orgao, quantidade
    rows: list[dict] = []
    for _, r in classif.iterrows():
        tip = r["tipologia2007"]
        setor = r["SETOR2"]
        for orgao in orgaos:
            val = r.get(orgao, 0)
            if pd.notna(val) and val > 0:
                rows.append({"tipologia2007": tip, "SETOR2": setor,
                             "orgao": orgao, "quantidade": val})
    dados = pd.DataFrame(rows)

    # Escala Y comum
    max_vals = []
    for orgao in orgaos:
        df_o = dados[dados["orgao"] == orgao]
        for tip in tipologias:
            total = df_o[df_o["tipologia2007"] == tip]["quantidade"].sum()
            if total > 0:
                max_vals.append(total)
    limite_y = max(max_vals) * 1.10 if max_vals else 1

    # Escala per capita
    if not medias_pc.empty:
        max_pc = max(medias_pc["icf_sudene_pc_media"].max(),
                     medias_pc["icf_sudam_pc_media"].max())
        limite_pc = max_pc * 1.5
    else:
        limite_pc = 1

    # LaTeX textwidth=155mm (~6.1in). Escala = 6.1/12 ≈ 0.51
    # fs=20 → ~10pt (títulos, legenda); fs_x=16 → ~8pt (eixos)
    fs = 20
    fs_x = 16

    fig, axes = plt.subplots(1, 2, figsize=(12, 6), sharey=True)

    # Mapa orgao → coluna per capita
    pc_col_map = {"SUDENE": "icf_sudene_pc_media", "SUDAM": "icf_sudam_pc_media"}

    for ax_idx, orgao in enumerate(orgaos):
        ax = axes[ax_idx]
        df_o = dados[dados["orgao"] == orgao]

        # Setores presentes neste órgão, na ordem definida
        setores_presentes = [s for s in setores_order if s in df_o["SETOR2"].values]

        # Cores dos setores
        cores_setor = {s: set3_colors[i % len(set3_colors)]
                       for i, s in enumerate(setores_order)}

        x = np.arange(len(tipologias))
        x_labels = [tip_labels.get(t, t) for t in tipologias]
        width = 0.9
        bottom = np.zeros(len(tipologias))

        for setor in setores_presentes:
            values = []
            for tip in tipologias:
                val = df_o[(df_o["tipologia2007"] == tip) & (df_o["SETOR2"] == setor)]["quantidade"].sum()
                values.append(val)
            values = np.array(values)
            ax.bar(x, values, width, bottom=bottom, label=setor,
                   color=cores_setor[setor], edgecolor="white", linewidth=0.5)
            bottom += values

        ax.set_xticks(x)
        ax.set_xticklabels(x_labels, fontsize=fs_x, ha="center")
        ax.set_title(orgao, fontsize=fs, pad=8)
        ax.set_ylim(0, limite_y)
        ax.set_axisbelow(True)

        for spine in ax.spines.values():
            spine.set_visible(True)
            spine.set_color("black")
            spine.set_linewidth(0.5)
        ax.grid(axis="y", alpha=0.4, linestyle="-", color="gray", linewidth=0.5)
        ax.tick_params(axis="both", labelsize=fs_x)

        if ax_idx == 0:
            ax.set_ylabel("Quantidade", fontsize=fs_x)
            ax.yaxis.set_major_locator(mticker.MaxNLocator(nbins=5, integer=True))
            ax.yaxis.set_major_formatter(mticker.FuncFormatter(fmt_br))

    # Legenda unificada (com labels abreviadas para legibilidade)
    legend_renames = {
        "Indústria extrativa de minerais metálicos": "Ind. extr. de minerais metálicos",
    }
    all_handles: list = []
    all_labels: list[str] = []
    seen: set[str] = set()
    for ax in axes:
        handles, labels = ax.get_legend_handles_labels()
        for h, l in zip(handles, labels):
            if l not in seen:
                seen.add(l)
                all_handles.append(h)
                all_labels.append(legend_renames.get(l, l))

    fig.legend(
        all_handles, all_labels,
        loc="lower center",
        bbox_to_anchor=(0.5, 0.0),
        ncol=3,
        fontsize=fs,
        frameon=False,
        columnspacing=1.5,
        handletextpad=0.5,
    )

    fig.subplots_adjust(wspace=0.10, bottom=0.28, top=0.93, left=0.08, right=0.97)

    out_path = FIGURES_DIR / "icf_superint_setor.png"
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
