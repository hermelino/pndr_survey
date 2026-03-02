#!/usr/bin/env python3
"""Gera figuras para o artigo LaTeX a partir de scripts R.

Figuras geradas:
- distribuicao_pib_relativo_municipal.png (mapa PIB 2002-2021)
- tipologia_II_simples_com_legenda.png (mapa tipologia 2018)
- icf_superint_setor.png (gráfico incentivos fiscais)

Figuras externas (não geradas):
- tipologia_I.JPG (fonte: Decreto nº 6.047/2007)

Uso:
    python generate_figures.py              # Gera todas (incremental)
    python generate_figures.py --force      # Força regeneração
    python generate_figures.py --list       # Lista figuras e status
    python generate_figures.py --validate   # Valida dependências
    python generate_figures.py --verbose    # Logging DEBUG

Dependências:
- R instalado (auto-detecção ou configurado em config.yaml)
- Dados RDS do projeto tese (configurado em config.yaml)
- Shapefiles IBGE (configurado em config.yaml)

Configuração:
    Edite scripts/config.yaml, seção figures:
      external_data_dir: "C:/OneDrive/github/tese/bulding_dataset_R/output/data"
      external_shapefiles_dir: "C:/OneDrive/DATABASES"
      r_executable: ""  # Vazio = auto-detect
"""

from __future__ import annotations

import argparse
import logging
import sys
from datetime import datetime
from pathlib import Path

import yaml

from src.figure_generators import (
    ICFPlotGenerator,
    PIBMapGenerator,
    TipologiaMapGenerator,
)
from src.figure_generators.base import FigureGenerator
from src.utils.logger import setup_logging

logger = logging.getLogger("pndr_survey.figures")

SCRIPT_DIR = Path(__file__).parent


def load_config(config_path: Path) -> dict:
    """Carrega configuração YAML e resolve paths relativos.

    Args:
        config_path: Caminho para config.yaml

    Returns:
        Dicionário com configuração da seção figures:

    Raises:
        FileNotFoundError: Se config.yaml não existir
        ValueError: Se seção figures: estiver ausente
    """
    if not config_path.exists():
        raise FileNotFoundError(
            f"Config não encontrado: {config_path}\n"
            f"Copie config.example.yaml para config.yaml e edite as configurações."
        )

    with open(config_path, encoding="utf-8") as f:
        config = yaml.safe_load(f)

    if "figures" not in config:
        raise ValueError(
            "Seção 'figures:' ausente no config.yaml\n"
            "Adicione a seção conforme documentado em config.example.yaml"
        )

    fig_config = config["figures"]

    # Resolver paths relativos para absolutos
    for key in ["r_scripts_dir", "output_dir"]:
        if key in fig_config and not Path(fig_config[key]).is_absolute():
            fig_config[key] = str((SCRIPT_DIR / fig_config[key]).resolve())

    return fig_config


def get_generators(config: dict) -> list[FigureGenerator]:
    """Retorna lista de geradores de figuras.

    Args:
        config: Dicionário de configuração (seção figures:)

    Returns:
        Lista de instâncias de FigureGenerator (PIB, Tipologia, ICF)
    """
    return [
        PIBMapGenerator(config),
        TipologiaMapGenerator(config),
        ICFPlotGenerator(config),
    ]


def cmd_list(config: dict) -> int:
    """Lista figuras e status (existência, tamanho, modificação).

    Args:
        config: Dicionário de configuração

    Returns:
        Exit code 0
    """
    generators = get_generators(config)

    print("\n=== FIGURAS DO ARTIGO ===\n")

    for gen in generators:
        output_path = gen.output_dir / gen.FIGURE_NAME
        exists = output_path.exists()

        status = "[OK] Existe" if exists else "[--] Ausente"
        print(f"{status}  {gen.FIGURE_NAME}")

        if exists:
            size_kb = output_path.stat().st_size / 1024
            mtime = output_path.stat().st_mtime
            mtime_str = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M")
            print(f"         {size_kb:.1f} KB | Modificado: {mtime_str}")

        print()

    # Figura externa
    external = Path(config["output_dir"]) / "tipologia_I.JPG"
    status = "[OK] Existe (externa)" if external.exists() else "[ERRO] Ausente (externa)"
    print(f"{status}  tipologia_I.JPG")
    print("         Fonte: Decreto nº 6.047/2007 (não gerada por script)\n")

    return 0


def cmd_validate(config: dict) -> int:
    """Valida dependências de todas as figuras.

    Args:
        config: Dicionário de configuração

    Returns:
        Exit code 0 se OK, 1 se houver dependências ausentes
    """
    generators = get_generators(config)

    print("\n=== VALIDAÇÃO DE DEPENDÊNCIAS ===\n")

    all_ok = True

    for gen in generators:
        print(f"Validando {gen.FIGURE_NAME}...")

        try:
            errors = gen.validate_dependencies()

            if errors:
                all_ok = False
                print("  [ERRO] PROBLEMAS ENCONTRADOS:")
                for err in errors:
                    # Indentar erros multi-linha
                    for line in err.split("\n"):
                        print(f"    {line}")
            else:
                print("  [OK] Todas as dependências OK")

        except Exception as e:
            all_ok = False
            print(f"  [ERRO] ERRO NA VALIDAÇÃO: {e}")

        print()

    if all_ok:
        print("[OK] Todas as dependências estão disponíveis.\n")
        return 0
    else:
        print("[ERRO] Algumas dependências estão ausentes. Veja erros acima.\n")
        return 1


def cmd_generate(config: dict, force: bool = False) -> int:
    """Gera todas as figuras.

    Args:
        config: Dicionário de configuração
        force: Se True, força regeneração (ignora timestamps)

    Returns:
        Exit code 0 se todas as figuras foram geradas, 1 se houver falhas
    """
    generators = get_generators(config)

    print("\n=== GERAÇÃO DE FIGURAS ===\n")

    if force:
        print("Modo --force: regenerando todas as figuras\n")

    success_count = 0
    failed = []

    for gen in generators:
        try:
            metadata = gen.generate(force=force)
            print(f"[OK] {metadata.name}")
            print(f"  Salvo em: {metadata.output_path}")
            print(f"  Descrição: {metadata.description}\n")
            success_count += 1

        except Exception as e:
            logger.error(f"Erro ao gerar {gen.FIGURE_NAME}", exc_info=True)
            print(f"[ERRO] {gen.FIGURE_NAME} FALHOU")
            print(f"  Erro: {e}\n")
            failed.append(gen.FIGURE_NAME)

    print(f"\n{success_count}/{len(generators)} figuras geradas com sucesso.")

    if failed:
        print(f"\nFalhas:")
        for name in failed:
            print(f"  - {name}")
        print()

    return 0 if success_count == len(generators) else 1


def main() -> int:
    """Ponto de entrada principal.

    Returns:
        Exit code (0 = sucesso, 1 = erro)
    """
    parser = argparse.ArgumentParser(
        description="Gera figuras para o artigo LaTeX",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--config", default="config.yaml", help="Arquivo de configuração (default: config.yaml)"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Força regeneração de todas as figuras (ignora timestamps)",
    )
    parser.add_argument(
        "--list", action="store_true", help="Lista figuras e status (existência, tamanho)"
    )
    parser.add_argument(
        "--validate", action="store_true", help="Valida dependências (R, dados, shapefiles)"
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Logging DEBUG")

    args = parser.parse_args()

    # Setup logging
    log_level = "DEBUG" if args.verbose else "INFO"
    setup_logging(console_level=log_level, file_level="DEBUG")

    try:
        # Carregar configuração
        config_path = SCRIPT_DIR / args.config
        config = load_config(config_path)

        # Executar comando
        if args.list:
            return cmd_list(config)
        elif args.validate:
            return cmd_validate(config)
        else:
            return cmd_generate(config, force=args.force)

    except Exception as e:
        logger.exception("Erro ao executar generate_figures")
        print(f"\n[ERRO] ERRO: {e}\n", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
