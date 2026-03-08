#!/usr/bin/env python3
"""
Gera tabelas derivadas para o artigo LaTeX a partir de 2-2-papers.json

Tabelas geradas:
- tab:estudos-ano (distribuição temporal)
- tab:instrumentos (menções por instrumento)
- tab:autores-todos (top-10 autores)
- tab:unidade-amostral (unidades de análise)
- tab:metodos (métodos econométricos mais frequentes)

Output: Fragmentos LaTeX prontos para inserção em 3-metodo.tex
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
        # BNDES is NOT a PNDR instrument — skip it

    return instrumentos


def normalizar_autor_ris(autor: str) -> str:
    """
    Normaliza nomes de autores para formato consistente: Sobrenome, Iniciais.
    Unifica variantes do mesmo autor (RIS, JSON bibliográfico e LLM).
    """
    if not autor:
        return ''

    autor = autor.strip()

    # Mapeamento manual de variantes conhecidas baseado em análise dos dados
    VARIANTES = {
        # Irffi
        'IRFFI, Guilherme': 'Irffi, G.D.',
        'Irffi, G.': 'Irffi, G.D.',
        'Irffi, Guilherme': 'Irffi, G.D.',
        'Irffi, Guilherme Diniz': 'Irffi, G.D.',
        'IRFFI, Guilherme Diniz': 'Irffi, G.D.',
        # Carneiro
        'CARNEIRO, Diego': 'Carneiro, D.R.F.',
        'Carneiro, D.R.F.': 'Carneiro, D.R.F.',
        'Carneiro, Diego': 'Carneiro, D.R.F.',
        'Carneiro, Diego Rafael Fonseca': 'Carneiro, D.R.F.',
        'CARNEIRO, Diego Rafael Fonseca': 'Carneiro, D.R.F.',
        # Resende
        'Mendes Resende, G.': 'Resende, G.M.',
        'Resende, Guilherme': 'Resende, G.M.',
        'Resende, Guilherme Mendes': 'Resende, G.M.',
        'RESENDE, Guilherme Mendes': 'Resende, G.M.',
        'Resend, Guilherme Mendes': 'Resende, G.M.',
        # Oliveira G.R.
        'Oliveira, Guilherme Resende': 'Oliveira, G.R.',
        'OLIVEIRA, Guilherme Resende': 'Oliveira, G.R.',
        'Oliveira, G.R.': 'Oliveira, G.R.',
        # Oliveira I.G.
        'Oliveira, Ierê Gondim': 'Oliveira, I.G.',
        # Oliveira T.G.
        'OLIVEIRA, Tássia Germano de': 'Oliveira, T.G.',
        # Veloso
        'VELOSO, Pedro': 'Veloso, P.A.S.',
        'Veloso, P.A.S.': 'Veloso, P.A.S.',
        'VELOOSO, Pedro Alexandre Santos': 'Veloso, P.A.S.',
        'VELOSO, Pedro Alexandre Santos': 'Veloso, P.A.S.',
        # Silveira Neto
        'SILVEIRA NETO, Raul da Mota': 'Silveira Neto, R.M.',
        'NETO, Raul da Mota Silveira': 'Silveira Neto, R.M.',
        # Costa
        'COSTA, Edward': 'Costa, E.M.',
        'Costa, E.M.': 'Costa, E.M.',
        'COSTA, Edward Martins': 'Costa, E.M.',
        # Braz
        'BRAZ, Marleton Souza': 'Braz, M.S.',
        'Braz, M.S.': 'Braz, M.S.',
        'BRAZ, Marleton': 'Braz, M.S.',
        # Bastos
        'BASTOS, Felipe': 'Bastos, F.S.',
        'BASTOS, Felipe de Sousa': 'Bastos, F.S.',
        'Bastos, Felipe de Sousa': 'Bastos, F.S.',
        'Bastos, Fabrício de Souza': 'Bastos, F.S.',
        'de Sousa Bastos, F.': 'Bastos, F.S.',
        # Alves
        'ALVES, Denis Fernandes': 'Alves, D.F.',
        # Shirasu
        'SHIRASU, Maitê': 'Shirasu, M.R.',
        'Shirasu, Maitê Rimekka': 'Shirasu, M.R.',
        # Soares
        'Ricardo Brito Soares': 'Soares, R.B.',
        'Soares, Ricardo Brito': 'Soares, R.B.',
        'Soares, R.B.': 'Soares, R.B.',
        # Souza
        'SOUZA, Hermelino': 'Souza, H.N.',
        'Souza, Hermelino Nepomuceno de': 'Souza, H.N.',
        # Nunes
        'NUNES, Erivelton': 'Nunes, E.S.',
        'NUNES, Erivelton de Souza': 'Nunes, E.S.',
        # Andrade
        'Andrade, V.': 'Andrade, V.',
        'ANDRADE, Vanessa': 'Andrade, V.',
        # Domingues
        'Domingues, E.P.': 'Domingues, E.P.',
        'DOMINGUES, Edson Paulo': 'Domingues, E.P.',
        # Silva Filho
        'Abel da Silva Filho, L.': 'Silva Filho, L.A.',
        'FILHO, Luis Abel da silva': 'Silva Filho, L.A.',
        'da Silva Filho, Luís Abel': 'Silva Filho, L.A.',
        'Silva Filho, Luis Abel': 'Silva Filho, L.A.',
        # Daniel
        'Daniel, Lindomar Pegorini': 'Daniel, L.P.',
        'DANIEL, Lindomar Pegorini': 'Daniel, L.P.',
        # Braga
        'Braga, Marcelo José': 'Braga, M.J.',
        'BRAGA, Marcelo José': 'Braga, M.J.',
    }

    return VARIANTES.get(autor, autor)


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
        'Abel da Silva Filho, L.': 'Silva Filho, L.A.',
    }

    # Casos especiais: registros mal formatados sem ponto-e-vírgula
    if raw == 'Ricardo Brito Soares, Jânia Maria Pinho Sousa, Antonio Pereira Da Silva Neto':
        # Retornar lista de autores extraídos manualmente
        return ['Soares, R.B.', 'Sousa, J.M.P.', 'Silva Neto, A.P.']

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
        return 'Estado'
    elif 'amc' in clean or 'área mínima' in clean:
        return 'Área Mínima Comparável'
    elif 'microrregião' in clean:
        return 'Microrregião'
    elif 'mesorregião' in clean:
        return 'Mesorregião'
    elif 'macrorregião' in clean or clean == 'região':
        return 'Macrorregião'
    else:
        return clean.capitalize()


def extrair_metodos(raw: str) -> list[str]:
    """
    Extract all econometric methods from a raw description via keyword matching.
    Returns list of canonical method names found.
    Order matters: more specific patterns come before generic ones.
    """
    if not raw or not isinstance(raw, str):
        return []

    from unidecode import unidecode
    text = unidecode(raw.lower())

    # (keywords, canonical_name)
    RULES: list[tuple[list[str], str]] = [
        # Staggered DiD (before plain DiD)
        (['escalonado', 'staggered', 'callaway', 'dois estagios', 'two-stage'],
         'Diferenças em Diferenças Escalonado'),
        # RDD
        (['descontinua', 'discontinuity', 'rdd', 'grdd'],
         'Regressão Descontínua (RDD)'),
        # GPS (before PSM)
        (['generalized propensity', 'gps', 'escore de propensao generalizado',
          'propensao generalizado', 'dose-response'],
         'Generalized Propensity Score (GPS)'),
        # PSM
        (['propensity score matching', 'psm', 'pareamento por escore'],
         'Propensity Score Matching (PSM)'),
        # Generalized Synthetic Control
        (['synthetic control', 'controle sintetico', 'sintetico generalizado'],
         'Controle Sintético Generalizado'),
        # IV
        (['instrumental', ' iv '],
         'Variáveis Instrumentais (IV)'),
        # DEA
        (['dea', 'envoltoria'],
         'Análise Envoltória de Dados (DEA)'),
        # SFA
        (['fronteira estocastica', 'sfa', 'stochastic frontier'],
         'Fronteira Estocástica (SFA)'),
        # Malmquist
        (['malmquist'],
         'Índice de Malmquist'),
        # Threshold
        (['limiar', 'threshold'],
         'Modelo de Efeito Limiar (Threshold)'),
        # DiD (plain)
        (['diferencas em diferencas', 'diff-in-diff', 'did', 'differences'],
         'Diferenças em Diferenças (DiD)'),
        # Spatial models: error + panel → unified category
        (['erro espacial', 'error espacial', 'sdem', 'sem ',
          'painel espacial', 'spatial durbin', 'sdm', 'espacial aplicada a dados em painel',
          'modelos espaciais de painel', 'espaciais de painel'],
         'Painel Espacial'),
        # AEDE
        (['exploratoria espacial', 'aede'],
         'Análise Exploratória Espacial (AEDE)'),
        # CGE
        (['equilibrio geral', 'cge', 'egc', 'computable general'],
         'Equilíbrio Geral Computável (EGC)'),
        # Dynamic panel (without GMM keyword)
        (['dinamico', 'dynamic'],
         'Painel Dinâmico'),
        # Random effects panel
        (['efeitos aleatorios', 'random effect'],
         'Painel de Efeitos Aleatórios'),
        # Fixed effects panel (after spatial panel)
        (['efeito fixo', 'efeitos fixos', 'fixed effect'],
         'Painel de Efeitos Fixos'),
        # First differences
        (['first-differenc', 'primeiras diferenc', ' fd '],
         'Primeiras Diferenças (FD)'),
        # OLS / MQO
        (['mqo', 'ols', 'minimos quadrados'],
         'MQO/OLS'),
        # Quantile regression
        (['quantilica', 'quantile'],
         'Regressão Quantílica'),
    ]

    found: list[str] = []
    for keywords, canonical in RULES:
        for kw in keywords:
            if kw in text:
                if canonical not in found:
                    found.append(canonical)
                break

    # Hierarchy: specific variant suppresses generic variant
    DID_ESC = 'Diferenças em Diferenças Escalonado'
    DID_PLAIN = 'Diferenças em Diferenças (DiD)'
    if DID_ESC in found and DID_PLAIN in found:
        found.remove(DID_PLAIN)

    return found


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
    ordem = ['FNE', 'FNO', 'FCO', 'FDNE', 'FDA', 'FDCO', 'IF -- Sudene', 'IF -- Sudam']
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
    # Extrair autores do JSON (campo 'autores' com fallback para 's1.autores')
    autores = Counter()

    for p in aprovados:
        raw = p.get('autores', '') or ''
        if not raw:
            s1 = p.get('s1', {})
            raw = s1.get('autores', '') if isinstance(s1, dict) else ''
        if not raw:
            continue
        # Limpar referências de página do LLM (ex: "[p. 1]")
        raw = re.sub(r'\s*\[p\.\s*\d+\]', '', raw)
        for parte in raw.split(';'):
            nome = parte.strip()
            if nome:
                autores[normalizar_autor_ris(nome)] += 1

    print("=== TAB:AUTORES-TODOS (TOP-10) ===")
    print("\\begin{table}[H]")
    print("\\footnotesize")
    print("\\renewcommand{\\arraystretch}{1.2}")
    print("\\centering")
    print("\\caption{Top-10 autores (autorias e coautorias)}")
    print("\\label{tab:autores-todos}")
    print("\\begin{tabular}{lr}")
    print("\\toprule")
    print("Autor & Qtd. estudos \\\\")
    print("\\midrule")

    top10 = sorted(autores.most_common(10), key=lambda x: (-x[1], x[0]))
    for autor, count in top10:
        # Escapar caracteres especiais do LaTeX
        autor_escaped = autor.replace('&', '\\&')
        print(f"{autor_escaped} & {count} \\\\")

    print("\\bottomrule")
    print("\\multicolumn{2}{l}{\\footnotesize Fonte: Elaboração própria.} \\\\")
    print("\\end{tabular}")
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
    # TAB: MÉTODOS (TOP-6) — multi-method extraction
    # ========================
    metodos = Counter()
    for p in aprovados:
        s2 = p.get('s2', {})
        if isinstance(s2, dict):
            raw = s2.get('metodo_econometrico', '')
            for m in extrair_metodos(raw):
                metodos[m] += 1

    # MSM scores (manual - baseado em conhecimento do método)
    msm_map = {
        'Diferenças em Diferenças Escalonado': 3,
        'Diferenças em Diferenças (DiD)': 3,
        'Propensity Score Matching (PSM)': 3,
        'Generalized Propensity Score (GPS)': 3,
        'Controle Sintético Generalizado': 3,
        'Painel de Efeitos Fixos': 3,
        'Painel Espacial': 3,
        'Painel Dinâmico': 3,
        'Painel de Efeitos Aleatórios': 3,
        'Primeiras Diferenças (FD)': 3,
        'MQO/OLS': 2,
        'Variáveis Instrumentais (IV)': 3,
        'Modelo de Efeito Limiar (Threshold)': 3,
        'Regressão Descontínua (RDD)': 4,
        'Regressão Quantílica': 3,
        'Equilíbrio Geral Computável (EGC)': 'n.c.',
        'Análise Envoltória de Dados (DEA)': 'n.c.',
        'Fronteira Estocástica (SFA)': 'n.c.',
        'Índice de Malmquist': 'n.c.',
        'Análise Exploratória Espacial (AEDE)': 'n.c.',
    }

    # Top-10 ordenados por frequência desc, depois nome asc
    top10 = sorted(metodos.most_common(10), key=lambda x: (-x[1], x[0]))
    msm_values = {msm_map.get(m, 'n.c.') for m, _ in top10}
    show_msm = len(msm_values) > 1  # omitir coluna se todos iguais

    print("=== TAB:METODOS (TOP-10) ===")
    print("\\begin{table}[h]")
    print("\\centering")
    print("\\small")
    print("\\caption{Top-10 métodos mais usados}")
    print("\\label{tab:metodos}")
    if show_msm:
        print("\\begin{tabular}{p{7cm}>{\centering\\arraybackslash}p{2.5cm}>{\centering\\arraybackslash}p{1.5cm}}")
        print("\\toprule")
        print("Método & Qtd. estudos & MSM \\\\")
    else:
        print("\\begin{tabular}{p{7cm}>{\centering\\arraybackslash}p{2.5cm}}")
        print("\\toprule")
        print("Método & Qtd. estudos \\\\")
    print("\\midrule")

    for metodo, count in top10:
        if show_msm:
            msm = msm_map.get(metodo, 'n.c.')
            print(f"{metodo} & {count} & {msm} \\\\")
        else:
            print(f"{metodo} & {count} \\\\")

    print("\\bottomrule")
    ncols = 3 if show_msm else 2
    if show_msm:
        print(f"\\multicolumn{{{ncols}}}{{p{{11cm}}}}{{\\setlength{{\\parindent}}{{0pt}}\\footnotesize Nota: MSM = \\textit{{Maryland Scientific Methods Scale}} \\cite{{Madaleno2016}}; n.c. = não classificável. Fonte: Elaboração própria.}} \\\\")
    else:
        print(f"\\multicolumn{{{ncols}}}{{p{{9.5cm}}}}{{\\footnotesize Fonte: Elaboração própria.}} \\\\")
    print("\\end{tabular}")
    print("\\end{table}")
    print()


if __name__ == '__main__':
    main()
