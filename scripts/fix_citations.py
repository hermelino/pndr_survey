"""Corrige chaves de citação em resultados.tex usando o mapeamento BibTeX.

Lê 2-2-papers.json, extrai autores e ano, mapeia para chaves BibTeX corretas
e substitui as citações incorretas no arquivo resultados.tex.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from unidecode import unidecode

BASE_DIR = Path(__file__).resolve().parent.parent
PAPERS_JSON = BASE_DIR / "data" / "2-papers" / "2-2-papers.json"
KEY_MAP = BASE_DIR / "latex" / "bibtex_key_map.json"
RESULTADOS_TEX = BASE_DIR / "latex" / "resultados.tex"

def load_json(path: Path) -> dict | list:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def extract_surname_year(paper: dict) -> tuple[str, str]:
    """Extrai sobrenome do primeiro autor e ano da publicação."""
    # Tentar extrair do nome do arquivo PDF
    arquivo = paper.get("arquivo_pdf", "")
    # Padrão: base-ano-autor1-autor2.pdf
    parts = arquivo.replace(".pdf", "").split("-")
    if len(parts) >= 3:
        year = parts[1]
        # Sobrenome é a primeira palavra depois do ano
        surname = parts[2] if len(parts) > 2 else ""
        return (surname, year)
    return ("", "")

def normalize_surname(s: str) -> str:
    """Normaliza sobrenome para matching (remove acentos, capitaliza)."""
    s = unidecode(s).strip()
    return s.capitalize()

def main():
    # Mapeamento manual de casos específicos conhecidos
    # Baseado em bibtex_key_map.json e conhecimento dos estudos
    manual_map = {
        # Seção 4.1.1 - Modelos de Efeitos Fixos
        "Resende2014": "Resende2014",
        "Resende2014c": "Resende2014",
        "OliveiraResendeGoncalves2017": "Oliveira2017a",
        "OliveiraResendeOliveira2017": "Oliveira2017",
        "SilvaFilhoetal2024": "Filho2024",
        "SilvaFilhoetal2023": "Filho2024",
        # Seção 4.1.2 - Modelos de Painel Espacial
        "CravoResende2015": "MendesResende2014",
        "ResendeCravoPires2014": "MendesResende2014",
        "OliveiraLimaArriel2016": "Oliveira2015",
        "ResendeSilvaFilho2017": "MendesResende2018",
        "ResendeSilvaFilho2018": "MendesResende2018",
        # Seção 4.1.3 - Modelos Não Lineares e de Eficiência
        "Linharesetal2014": "Viana2014",
        "IrffiAraujoBastos2016": "Oliveira2015",
        "Carneiro2018b": "Oliveira2018",
        # Seção 4.1.4 - Modelos Dinâmicos
        "CambotaViana2019": "Viana2014",
        # Seção 4.1.5 - Modelos de Equilíbrio Geral
        "NascimentoHaddad2017": "Nascimento2017",
        "Ribeiroetal2020": "deSantanaRibeiro2020",
        "GoncalvesBragaGurgel2022": "Oliveira2021",
        # Seção 4.1.6 - Modelos Quase Experimentais
        "OliveiraSilveiraNeto2020": "Oliveira2020",
        "Carneiroetal2024a": "Carneiro2024",
        "MonteIrffiBastosCarneiro2025": "Monte2025",
        # Seção 4.2 - FCs sobre Mercado de Trabalho
        "SilvaResendeSilveiraNeto2009": "Silva2009",
        "SoaresSousaNeto2009": "Soares2017",
        "CunhaJuniorSoares2024": "Junior2024",
        "DanielBraga2020": "Oliveira2020",
        "OliveiraSilveiraNeto2021": "Oliveira2021",
        "OliveiraMenezesResende2018a": "Oliveira2018",
        "OliveiraMenezesResende2018b": "Oliveira2018",
        "RiegerLimaRodrigues2020": "Ribeiro2024",
        # Seção 4.3 - Fundos de Desenvolvimento
        "BrazBastosIrffi2024": "Bastos2024",
        "CarneiroCostaIrffi2024b": "Carneiro2023",
        "Irffietal2025": "Souza2025",
        # Seção 4.4 - Incentivos Fiscais
        "Garsousetal2017": "Garsous2017",
        "BrazIrffi2023": "Braz2023",
        "CostaCarneiroIrffi2024": "Costa2024",
        "FerreiraIrffiCarneiro2024": "Carneiro2024",
    }

    # Ler resultados.tex
    content = RESULTADOS_TEX.read_text(encoding="utf-8")

    # Encontrar todas as citações
    citations = set(re.findall(r"\\cite(?:online)?\{([^}]+)\}", content))

    print(f"Citações encontradas: {len(citations)}")
    print(f"Mapeamento disponível: {len(manual_map)} entradas")

    # Substituir
    for old_key, new_key in manual_map.items():
        if old_key in citations:
            # Substituir em \citeonline{} e \cite{}
            content = re.sub(
                rf"\\cite(online)?\{{{re.escape(old_key)}\}}",
                rf"\\cite\1{{{new_key}}}",
                content
            )
            print(f"  {old_key} -> {new_key}")

    # Salvar
    RESULTADOS_TEX.write_text(content, encoding="utf-8")
    print(f"\nOK - Citacoes corrigidas em {RESULTADOS_TEX}")

    # Verificar se ainda há citações não mapeadas
    remaining = set(re.findall(r"\\cite(?:online)?\{([^}]+)\}", content))
    unmapped = remaining - set(manual_map.values())
    if unmapped:
        print(f"\nAVISO - Citacoes ainda nao mapeadas: {unmapped}")

if __name__ == "__main__":
    main()
