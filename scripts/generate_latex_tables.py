#!/usr/bin/env python3
"""
Gera tabelas derivadas para o artigo LaTeX a partir de 2-2-papers.json

Tabelas geradas:
- tab:estudos-ano (distribuição temporal)
- tab:instrumentos (menções por instrumento)
- tab:autores-todos (top-10 autores)
- tab:unidade-amostral (unidades de análise)
- tab:metodos (métodos econométricos mais frequentes)

Output: Fragmentos LaTeX prontos para inserção em metodo.tex
"""

import json
import re
from collections import Counter
from pathlib import Path


def normalizar_instrumento(raw: str) -> list[str]:
    """
    Normaliza nomes de instrumentos, removendo referências de página
    e unificando variantes.

    Returns: lista de instrumentos normalizados
    """
    if not raw or not isinstance(raw, str):
        return []

    # Remover referências de página: [p. X], [impl.], etc.
    clean = re.sub(r'\s*\[.*?\]', '', raw)

    # Split por vírgula ou ponto-e-vírgula
    parts = re.split(r'[,;]', clean)

    instrumentos = []
    for part in parts:
        part = part.strip()
        if not part:
            continue

        # Normalizar variantes
        part_upper = part.upper()

        # Fundos constitucionais
        if 'FNE' in part_upper:
            instrumentos.append('FNE')
        elif 'FNO' in part_upper:
            instrumentos.append('FNO')
        elif 'FCO' in part_upper:
            instrumentos.append('FCO')
        # Fundos de desenvolvimento
        elif 'FDNE' in part_upper:
            instrumentos.append('FDNE')
        elif 'FDA' in part_upper and 'FDNE' not in part_upper:
            instrumentos.append('FDA')
        elif 'FDCO' in part_upper:
            instrumentos.append('FDCO')
        # Incentivos fiscais
        elif 'SUDENE' in part_upper or 'IF' in part_upper and 'SUDENE' in raw.upper():
            instrumentos.append('IF -- Sudene')
        elif 'SUDAM' in part_upper or 'IF' in part_upper and 'SUDAM' in raw.upper():
            instrumentos.append('IF -- Sudam')
        # BNDES (caso apareça)
        elif 'BNDES' in part_upper:
            instrumentos.append('BNDES')

    return instrumentos


def normalizar_autor(raw: str) -> list[str]:
    """
    Normaliza nomes de autores para formato consistente: Sobrenome, Iniciais
    Unifica variantes do mesmo autor (ex: "Mendes Resende, G." e "Resende, Guilherme")
    """
    if not raw or not isinstance(raw, str):
        return []

    # Mapeamento manual de variantes conhecidas baseado em análise dos dados
    VARIANTES = {
        'Mendes Resende, G.': 'Resende, G.M.',
        'Resende, Guilherme': 'Resende, G.M.',
        'Oliveira, Guilherme Resende': 'Oliveira, G.R.',
        'Oliveira, G.R.': 'Oliveira, G.R.',
        'Ricardo Brito Soares': 'Soares, R.B.',
        'Soares, Ricardo Brito': 'Soares, R.B.',
        'Soares, R.B.': 'Soares, R.B.',
    }

    # Casos especiais: registros mal formatados sem ponto-e-vírgula
    if raw == 'Ricardo Brito Soares, Jânia Maria Pinho Sousa, Antonio Pereira Da Silva Neto':
        # Retornar lista de autores extraídos manualmente
        return ['Soares, R.B.', 'Sousa, J.M.P.', 'Neto, A.P.S.']

    autores = []
    # Split por ponto-e-vírgula
    for parte in raw.split(';'):
        nome = parte.strip()
        if not nome:
            continue

        # Aplicar normalização de variantes conhecidas
        nome_norm = VARIANTES.get(nome, nome)
        autores.append(nome_norm)

    return autores


def normalizar_unidade_amostral(raw: str) -> str:
    """
    Normaliza unidades amostrais para categorias consistentes
    """
    if not raw or not isinstance(raw, str):
        return 'Não especificado'

    # Remover referências de página
    clean = re.sub(r'\s*\[.*?\]', '', raw).strip().lower()

    # Normalizar variantes
    if 'município' in clean or 'municipal' in clean:
        return 'Município'
    elif 'empresa' in clean or 'firma' in clean:
        return 'Empresa'
    elif 'uf' in clean or 'estado' in clean:
        return 'UF'
    elif 'amc' in clean or 'área mínima' in clean:
        return 'Área Mínima Comparável'
    elif 'microrregião' in clean:
        return 'Microrregião'
    elif 'mesorregião' in clean:
        return 'Mesorregião'
    else:
        return clean.capitalize()


def normalizar_metodo(raw: str) -> str:
    """
    Normaliza métodos econométricos para categorias consistentes
    """
    if not raw or not isinstance(raw, str):
        return 'Não especificado'

    # Remover referências de página
    clean = re.sub(r'\s*\[.*?\]', '', raw).strip()

    # Normalizar variantes comuns
    clean_lower = clean.lower()

    if 'did' in clean_lower or 'diferenças em diferenças' in clean_lower:
        if 'escalonado' in clean_lower or 'staggered' in clean_lower:
            return 'Diferenças em Diferenças Escalonado'
        else:
            return 'Diferenças em Diferenças (DiD)'
    elif 'psm' in clean_lower or 'propensity score matching' in clean_lower:
        return 'Propensity Score Matching (PSM)'
    elif 'gps' in clean_lower or 'generalized propensity' in clean_lower:
        return 'Generalized Propensity Score (GPS)'
    elif 'gscm' in clean_lower or 'generalized synthetic' in clean_lower:
        return 'Generalized Synthetic Control Method'
    elif 'egc' in clean_lower or 'equilíbrio geral' in clean_lower:
        return 'Equilíbrio Geral Computável (EGC)'
    elif 'dea' in clean_lower or 'análise envoltória' in clean_lower:
        return 'Análise Envoltória de Dados (DEA)'
    elif 'painel' in clean_lower and 'efeito' in clean_lower:
        return 'Painel de Efeitos Fixos'
    elif 'painel' in clean_lower and 'espacial' in clean_lower:
        return 'Painel Espacial'
    elif 'first-difference' in clean_lower:
        return 'First-Differences (FD)'
    elif 'mqo' in clean_lower or 'ols' in clean_lower:
        return 'Mínimos Quadrados Ordinários (MQO)'
    elif 'iv' in clean_lower or 'variáveis instrumentais' in clean_lower:
        return 'Variáveis Instrumentais (IV)'
    else:
        return clean


def main():
    # Carregar dados
    data_path = Path(__file__).parent.parent / 'data' / '2-papers' / '2-2-papers.json'
    with open(data_path, encoding='utf-8') as f:
        data = json.load(f)

    aprovados = [p for p in data if p.get('triagem') == 'APROVADO']

    print(f"Estudos aprovados: {len(aprovados)}")
    print()

    # ========================
    # TAB: ESTUDOS POR ANO
    # ========================
    anos = Counter(int(p['ano']) for p in aprovados if p.get('ano'))

    periodos = {
        '2005--2010': (2005, 2010),
        '2011--2015': (2011, 2015),
        '2016--2020': (2016, 2020),
        '2021--2026': (2021, 2026)
    }

    print("=== TAB:ESTUDOS-ANO ===")
    print("\\begin{table}[h]")
    print("\\small")
    print("\\centering")
    print("\\caption{Estudos por período}")
    print("\\label{tab:estudos-ano}")
    print("\\begin{tabular}{lr}")
    print("\\toprule")
    print("Período & Qtd. artigos \\\\")
    print("\\midrule")

    for periodo, (ini, fim) in periodos.items():
        count = sum(c for a, c in anos.items() if ini <= a <= fim)
        print(f"{periodo} & {count} \\\\")

    print("\\bottomrule")
    print("\\end{tabular}")
    print("\\fonte{Elaboração própria.}")
    print("\\end{table}")
    print()

    # ========================
    # TAB: INSTRUMENTOS
    # ========================
    instrumentos = Counter()
    for p in aprovados:
        s1 = p.get('s1', {})
        if isinstance(s1, dict):
            raw = s1.get('instrumentos_pndr', '')
            for inst in normalizar_instrumento(raw):
                instrumentos[inst] += 1

    print("=== TAB:INSTRUMENTOS ===")
    print("\\begin{table}[h]")
    print("\\centering")
    print("\\small")
    print("\\caption{Instrumento da PNDR avaliado}")
    print("\\label{tab:instrumentos}")
    print("\\begin{tabular}{lr}")
    print("\\toprule")
    print("Instrumento & Qtd. estudos \\\\")
    print("\\midrule")

    # Ordem fixa para consistência
    ordem = ['FNE', 'FNO', 'FCO', 'FDNE', 'FDA', 'FDCO', 'IF -- Sudene', 'IF -- Sudam', 'BNDES']
    for inst in ordem:
        if inst in instrumentos:
            print(f"{inst} & {instrumentos[inst]} \\\\")

    print("\\bottomrule")
    print("\\end{tabular}")
    print("\\fonte{Elaboração própria.}")
    print("\\end{table}")
    print()

    # ========================
    # TAB: AUTORES (TOP-10)
    # ========================
    autores = Counter()
    for p in aprovados:
        raw = p.get('autores', '')
        for autor in normalizar_autor(raw):
            autores[autor] += 1

    print("=== TAB:AUTORES-TODOS (TOP-10) ===")
    print("\\begin{table}[h]")
    print("\\small")
    print("\\centering")
    print("\\caption{Top-10 autores (autorias e coautorias)}")
    print("\\label{tab:autores-todos}")
    print("\\begin{tabular}{lr}")
    print("\\toprule")
    print("Autor & Qtd. estudos \\\\")
    print("\\midrule")

    for autor, count in autores.most_common(10):
        # Escapar caracteres especiais do LaTeX
        autor_escaped = autor.replace('&', '\\&')
        print(f"{autor_escaped} & {count} \\\\")

    print("\\bottomrule")
    print("\\end{tabular}")
    print("\\fonte{Elaboração própria.}")
    print("\\end{table}")
    print()

    # ========================
    # TAB: UNIDADE AMOSTRAL
    # ========================
    unidades = Counter()
    for p in aprovados:
        s2 = p.get('s2', {})
        if isinstance(s2, dict):
            raw = s2.get('unidade_espacial', '')
            unidade_norm = normalizar_unidade_amostral(raw)
            unidades[unidade_norm] += 1

    print("=== TAB:UNIDADE-AMOSTRAL ===")
    print("\\begin{table}[h]")
    print("\\small")
    print("\\centering")
    print("\\caption{Estudos por unidade amostral}")
    print("\\label{tab:unidade-amostral}")
    print("\\begin{tabular}{lr}")
    print("\\toprule")
    print("Unidade Amostral & Qtd. estudos \\\\")
    print("\\midrule")

    # Ordenar por frequência
    for unidade, count in unidades.most_common():
        if unidade != 'Não especificado':
            print(f"{unidade} & {count} \\\\")

    print("\\bottomrule")
    print("\\end{tabular}")
    print("\\fonte{Elaboração própria.}")
    print("\\end{table}")
    print()

    # ========================
    # TAB: MÉTODOS (TOP-6)
    # ========================
    metodos = Counter()
    for p in aprovados:
        s2 = p.get('s2', {})
        if isinstance(s2, dict):
            raw = s2.get('metodo_econometrico', '')
            metodo_norm = normalizar_metodo(raw)
            if metodo_norm != 'Não especificado':
                metodos[metodo_norm] += 1

    print("=== TAB:METODOS (TOP-6) ===")
    print("\\begin{table}[h]")
    print("\\centering")
    print("\\small")
    print("\\caption[Métodos mais frequentes]{Métodos mais frequentes\\footnote{MSM: \\textit{Maryland Scientific Methods Scale} \\cite{MadalenoWaights2016}; n.c.: não classificável.}}")
    print("\\label{tab:metodos}")
    print("\\begin{tabular}{lrc}")
    print("\\toprule")
    print("Método & Qtd. estudos & MSM \\\\")
    print("\\midrule")

    # MSM scores (manual - baseado em conhecimento do método)
    msm_map = {
        'Diferenças em Diferenças Escalonado': 3,
        'Diferenças em Diferenças (DiD)': 3,
        'Propensity Score Matching (PSM)': 3,
        'Generalized Propensity Score (GPS)': 3,
        'Generalized Synthetic Control Method': 3,
        'Painel de Efeitos Fixos': 3,
        'Painel Espacial': 3,
        'First-Differences (FD)': 3,
        'Mínimos Quadrados Ordinários (MQO)': 2,
        'Variáveis Instrumentais (IV)': 3,
        'Equilíbrio Geral Computável (EGC)': 'n.c.',
        'Análise Envoltória de Dados (DEA)': 'n.c.'
    }

    for metodo, count in metodos.most_common(6):
        msm = msm_map.get(metodo, 'n.c.')
        print(f"{metodo} & {count} & {msm} \\\\")

    print("\\bottomrule")
    print("\\end{tabular}")
    print("\\fonte{Elaboração própria.}")
    print("\\end{table}")
    print()


if __name__ == '__main__':
    main()
