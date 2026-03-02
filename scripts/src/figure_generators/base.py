"""Classe base abstrata para geradores de figuras."""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger("pndr_survey.figures")


@dataclass
class FigureMetadata:
    """Metadados de uma figura gerada.

    Attributes:
        name: Nome do arquivo da figura (ex: "distribuicao_pib_relativo_municipal.png")
        output_path: Caminho completo do arquivo gerado
        script_path: Caminho do script R que gera a figura (None se externa)
        dependencies: Lista de arquivos de dependência (dados, shapefiles, scripts)
        description: Descrição textual da figura
        is_external: True se figura é externa (sem script gerador)
    """
    name: str
    output_path: Path
    script_path: Path | None
    dependencies: list[Path]
    description: str
    is_external: bool = False


class FigureGenerator(ABC):
    """Classe base abstrata para geradores de figuras.

    Implementa padrão Template Method para validação de dependências,
    verificação de timestamps (geração incremental) e logging.

    Subclasses devem implementar:
    - validate_dependencies(): Verifica existência de dados/shapefiles
    - generate(): Executa script R e retorna metadados

    Attributes:
        config: Dicionário de configuração (seção figures: do config.yaml)
        output_dir: Diretório de saída (figures/)
        FIGURE_NAME: Nome do arquivo de saída (definido em subclasses)
        SCRIPT_NAME: Nome do script R (definido em subclasses)
    """

    # Constantes a serem definidas em subclasses
    FIGURE_NAME: str = ""
    SCRIPT_NAME: str = ""

    def __init__(self, config: dict):
        """Inicializa gerador.

        Args:
            config: Dicionário com configuração (seção figures: do YAML).
        """
        self.config = config
        self.output_dir = Path(config["output_dir"])
        self.output_dir.mkdir(parents=True, exist_ok=True)

    @abstractmethod
    def validate_dependencies(self) -> list[str]:
        """Valida dependências necessárias (dados, shapefiles, scripts).

        Returns:
            Lista de mensagens de erro (vazia se todas as dependências OK).

        Example:
            >>> errors = generator.validate_dependencies()
            >>> if errors:
            ...     for err in errors:
            ...         print(f"ERRO: {err}")
        """
        pass

    @abstractmethod
    def generate(self, force: bool = False) -> FigureMetadata:
        """Gera a figura executando script R.

        Args:
            force: Se True, regenera mesmo se arquivo já existe e está atualizado.

        Returns:
            Metadados da figura gerada.

        Raises:
            RuntimeError: Se validação falhar ou script R falhar.

        Example:
            >>> metadata = generator.generate(force=True)
            >>> print(f"Figura gerada: {metadata.output_path}")
        """
        pass

    def needs_regeneration(self, output_path: Path, dependencies: list[Path]) -> bool:
        """Verifica se figura precisa ser regenerada baseado em timestamps.

        Compara timestamp do arquivo de saída com timestamps das dependências.
        Se qualquer dependência for mais recente que o output, retorna True.

        Args:
            output_path: Caminho do arquivo de saída.
            dependencies: Lista de arquivos de dependência (dados, scripts).

        Returns:
            True se precisa regenerar, False caso contrário.

        Example:
            >>> deps = [Path("data.rds"), Path("script.R")]
            >>> if generator.needs_regeneration(output_path, deps):
            ...     print("Figura desatualizada, regenerando...")
        """
        if not output_path.exists():
            logger.debug(f"{output_path.name} não existe, precisa gerar")
            return True

        output_mtime = output_path.stat().st_mtime

        for dep in dependencies:
            if dep.exists() and dep.stat().st_mtime > output_mtime:
                logger.info(
                    f"{output_path.name} desatualizado "
                    f"(dependência {dep.name} modificada)"
                )
                return True

        logger.debug(f"{output_path.name} está atualizado")
        return False
