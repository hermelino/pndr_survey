#!/usr/bin/env python3
"""Gera as 4 tabelas de resultados (quadros survey) a partir de survey_results.json.

Tabelas geradas em latex/tabelas/:
- survey_artigos_fc_pib.tex   (Fundos Constitucionais → PIB)
- survey_artigos_fc_emprego.tex (Fundos Constitucionais → Mercado de Trabalho)
- survey_artigos_fd.tex        (Fundos de Desenvolvimento)
- survey_artigos_if.tex        (Incentivos Fiscais)

Uso: python generate_survey_tables.py
"""

from __future__ import annotations

import json
import logging
import sys
from dataclasses import dataclass, field
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
JSON_PATH = BASE_DIR / "data" / "2-papers" / "survey_results.json"
OUTPUT_DIR = BASE_DIR / "latex" / "tabelas"


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------

@dataclass
class ResultItem:
    texto: str
    valor: str | None = None
    sig: bool = False
    sub: bool = False


@dataclass
class Bloco:
    var_dependente: list[str]
    resultados: list[ResultItem]


@dataclass
class Study:
    cite_key: str
    amostragem: list[str]
    var_independente: list[str]
    blocos: list[Bloco]


@dataclass
class MethodGroup:
    method: str
    studies: list[Study]


@dataclass
class TableDef:
    id: str
    filename: str
    caption: str
    label: str
    siglas: str
    method_groups: list[MethodGroup] = field(default_factory=list)


# ---------------------------------------------------------------------------
# JSON → Dataclasses
# ---------------------------------------------------------------------------

def load_tables(path: Path) -> list[TableDef]:
    """Carrega survey_results.json e retorna lista de TableDef."""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    tables: list[TableDef] = []
    for t in data["tables"]:
        groups: list[MethodGroup] = []
        for mg in t["method_groups"]:
            studies: list[Study] = []
            for s in mg["studies"]:
                blocos: list[Bloco] = []
                for b in s["blocos"]:
                    items = [
                        ResultItem(
                            texto=r["texto"],
                            valor=r.get("valor"),
                            sig=r.get("sig", False),
                            sub=r.get("sub", False),
                        )
                        for r in b["resultados"]
                    ]
                    blocos.append(Bloco(var_dependente=b["var_dependente"], resultados=items))
                studies.append(Study(
                    cite_key=s["cite_key"],
                    amostragem=s["amostragem"],
                    var_independente=s["var_independente"],
                    blocos=blocos,
                ))
            groups.append(MethodGroup(method=mg["method"], studies=studies))
        tables.append(TableDef(
            id=t["id"],
            filename=t["filename"],
            caption=t["caption"],
            label=t["label"],
            siglas=t["siglas"],
            method_groups=groups,
        ))
    return tables


# ---------------------------------------------------------------------------
# Renderização LaTeX
# ---------------------------------------------------------------------------

def render_fc_cell(items: list[str], width: str) -> str:
    """Renderiza uma célula: texto direto se único item, \\fc se múltiplos."""
    if len(items) == 1:
        return items[0]
    inner = " ".join(f"\\item {it}" for it in items)
    return f"\\fc[{width}]{{{inner}}}"


def render_var_cell(var_ind: list[str], var_dep: list[str]) -> str:
    """Renderiza célula combinada de variáveis (política + resultado) com \\fcvar."""
    combined = var_ind + var_dep
    if len(combined) == 1:
        return combined[0]
    inner = " ".join(f"\\item {it}" for it in combined)
    return f"\\fcvar{{{inner}}}"


def render_result_item(item: ResultItem) -> str:
    """Renderiza um \\item de resultado."""
    prefix = "\\item[\\textbullet]" if item.sub else "\\item"
    if item.valor is None:
        return f"\t\t{prefix} {item.texto}"
    if item.valor == "":
        # Valor vazio com phantom para alinhamento
        return f"\t\t{prefix} {item.texto}\\hfill \\phantom{{\\textsuperscript{{*}}}}"
    sig_mark = "\\textsuperscript{*}" if item.sig else "\\phantom{\\textsuperscript{*}}"
    return f"\t\t{prefix} {item.texto} \\hfill {item.valor}{sig_mark}"


def render_result_cell(items: list[ResultItem], width: str) -> str:
    """Renderiza a célula de resultados completa."""
    lines = [render_result_item(it) for it in items]
    inner = "\n".join(lines)
    return f"\\fc[{width}]{{\n{inner}\n\t}}"


def render_table(table: TableDef) -> str:
    """Renderiza uma tabela completa como string .tex."""
    lines: list[str] = []
    a = lines.append

    # Cabeçalho do arquivo
    a(f"% Arquivo: latex/tabelas/{table.filename}")
    a(f"% Gerado automaticamente por scripts/generate_survey_tables.py")
    a(f"% Fonte: data/2-papers/survey_results.json")
    a("")
    a("% IMPORTANTE: Este arquivo requer:")
    a("% - Pacotes: longtable, multirow, afterpage, enumitem, array")
    a("% - Macros: \\fc e \\metodo (definidas em tabelas/tabela_macros.tex)")
    a("% - Comando \\citeonline (do pacote abntex2cite)")
    a("% - Contador: quadro (definido na classe abntex2)")
    a("")

    # Preamble
    a("\\afterpage{\\clearpage%")
    a("\\tiny%")
    a("\\setlength{\\extrarowheight}{1pt}%")
    a("\\setlength{\\tabcolsep}{2pt}%")
    a("\\linespread{0.9}\\selectfont%")
    a("\\renewcommand{\\arraystretch}{1.2}%")
    a("\\renewcommand{\\tablename}{\\quadroname}%")
    a("\\renewcommand{\\thetable}{\\arabic{quadro}}%")
    a("\\stepcounter{quadro}%")
    a("\\begin{longtable}{|>{\\raggedright\\arraybackslash}p{1.6cm}")
    a("\t\t|>{\\raggedright\\arraybackslash}p{1.7cm}")
    a("\t\t|>{\\raggedright\\arraybackslash}p{2cm}")
    a("\t\t|>{\\raggedright\\arraybackslash}p{3.5cm}")
    a("\t\t|>{\\raggedright\\arraybackslash}p{4.8cm}|}")
    a("")

    # Caption + label
    a(f"\t\\caption{{{table.caption}}} \\label{{{table.label}}} \\\\")
    a("")

    # First header
    a("\\hline")
    _add_header_row(lines)
    a("\t\\hline")
    a("\t\\endfirsthead")
    a("")

    # Continuation header
    a("\t\\multicolumn{5}{c}%")
    a("\t{{\\quadroname\\ \\thetable{} -- Continuação}} \\\\")
    a("\t\\hline")
    _add_header_row(lines)
    a("\t\\hline")
    a("\t\\endhead")
    a("")

    # Continuation footer
    a("\t\\hline")
    a("\t\\multicolumn{5}{r}{{Continua}} \\\\")
    a("\t\\endfoot")
    a("")

    # Last footer
    a("\t\\hline")
    a("\t\\multicolumn{5}{l}{")
    a("\t\t\\tiny")
    a("\t\t\\parbox{14.8cm}{%")
    a(f"\t\t\t\\vspace{{0.1cm}}")
    a(f"\t\t\tFonte: Elaborado pelo autor. Siglas: {table.siglas}")
    a("\t}}")
    a("\t\\endlastfoot")
    a("")

    # Body rows
    is_first_body_row = True
    for mg in table.method_groups:
        for i, study in enumerate(mg.studies):
            is_first_in_group = i == 0
            if is_first_in_group:
                # Skip \hline before very first body row (header already ends with \hline)
                if not is_first_body_row:
                    a("")
                    a("\t\\hline")
            else:
                a("\t\\cline{2-5}")
                a("")
            is_first_body_row = False

            method_col = mg.method if is_first_in_group else ""

            # First bloco: full 5-column row
            bloco0 = study.blocos[0]
            amostr = render_fc_cell(study.amostragem, "2cm")
            variaveis = render_var_cell(study.var_independente, bloco0.var_dependente)
            resultado = render_result_cell(bloco0.resultados, "4.5cm")

            a(f"{method_col}")
            a(f"\t& \\citeonline{{{study.cite_key}}}")
            a(f"\t& {amostr}")
            a(f"\t& {variaveis}")
            a(f"\t& {resultado}")
            a("\t\\\\")

            # Additional blocos (multi dep-var)
            for bloco in study.blocos[1:]:
                a("\t\\cline{4-5}")
                variaveis_extra = render_var_cell(study.var_independente, bloco.var_dependente)
                resultado_extra = render_result_cell(bloco.resultados, "4.5cm")
                a(f"\t& & ")
                a(f"\t& {variaveis_extra}")
                a(f"\t& {resultado_extra}")
                a("\t\\\\")

    a("")
    # Postamble
    a("\\end{longtable}%")
    a("\\normalsize%")
    a("\\setlength{\\extrarowheight}{0pt}%")
    a("\\setlength{\\tabcolsep}{6pt}%")
    a("\\linespread{1.5}\\selectfont%")
    a("\\renewcommand{\\tablename}{Tabela}%")
    a("\\renewcommand{\\thetable}{\\arabic{table}}%")
    a("}")

    return "\n".join(lines) + "\n"


def _add_header_row(lines: list[str]) -> None:
    """Adiciona a linha de cabeçalho das 5 colunas."""
    cols = [
        ("1.6cm", "Método"),
        ("1.7cm", "Artigo"),
        ("2cm", "Amostragem"),
        ("3.5cm", "Variáveis"),
        ("4.8cm", "Estimativa"),
    ]
    parts = []
    for width, title in cols:
        cell = (
            f"\\begin{{tabular}}[c]{{@{{}}>{{"
            f"\\centering\\arraybackslash}}m{{{width}}}@{{}}}}"
            f"{title}\\end{{tabular}}"
        )
        parts.append(cell)
    lines.append("\t" + "\n\t& ".join(parts) + " \\\\")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    if not JSON_PATH.exists():
        log.error("Arquivo não encontrado: %s", JSON_PATH)
        sys.exit(1)

    tables = load_tables(JSON_PATH)
    log.info("Carregadas %d tabelas de %s", len(tables), JSON_PATH.name)

    for table in tables:
        output_path = OUTPUT_DIR / table.filename
        content = render_table(table)
        output_path.write_text(content, encoding="utf-8")
        n_studies = sum(len(mg.studies) for mg in table.method_groups)
        log.info("Gerado %s (%d estudos)", table.filename, n_studies)


if __name__ == "__main__":
    main()
