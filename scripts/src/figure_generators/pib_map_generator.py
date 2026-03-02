"""Gerador de mapa de distribuição do PIB per capita relativo."""

from __future__ import annotations

import logging
import shutil
from pathlib import Path

from .base import FigureGenerator, FigureMetadata
from .r_wrapper import RScriptRunner

logger = logging.getLogger("pndr_survey.figures")


class PIBMapGenerator(FigureGenerator):
    """Gera mapa de distribuição do PIB per capita relativo municipal.

    Executa script R `mapa_distribuicao_pib_municipal.R` que produz 4 painéis
    (anos 2002, 2010, 2019, 2021) com classificação em 5 categorias de PIB
    per capita relativo, focando em municípios das superintendências regionais.

    Dependências:
    - Dados: dataset_completo_com_pib_relativo.rds
    - Shapefiles: BR_Municipios_2021.shp, BR_UF_2021.shp

    Figura gerada:
    - distribuicao_pib_relativo_municipal.png (4 mapas, paleta verde→azul)
    """

    FIGURE_NAME = "distribuicao_pib_relativo_municipal.png"
    SCRIPT_NAME = "mapa_distribuicao_pib_municipal.R"

    def validate_dependencies(self) -> list[str]:
        """Valida existência de dados RDS e shapefiles necessários.

        Returns:
            Lista de mensagens de erro (vazia se todas as dependências OK).
        """
        errors = []

        # Dados RDS
        data_dir = Path(self.config["external_data_dir"])
        rds_file = data_dir / "dataset_completo_com_pib_relativo.rds"

        if not data_dir.exists():
            errors.append(
                f"Diretório de dados ausente: {data_dir}\n"
                f"  Configure 'external_data_dir' no config.yaml"
            )
        elif not rds_file.exists():
            errors.append(f"Dado RDS ausente: {rds_file}")

        # Shapefiles
        shp_base = Path(self.config["external_shapefiles_dir"])
        shapefiles = [
            shp_base
            / "DIVISÃO POLÍTICA E REGIONAL"
            / "SHAPES"
            / "BR_Municipios_2021"
            / "BR_Municipios_2021.shp",
            shp_base
            / "DIVISÃO POLÍTICA E REGIONAL"
            / "SHAPES"
            / "BR_UF_2021"
            / "BR_UF_2021.shp",
        ]

        if not shp_base.exists():
            errors.append(
                f"Diretório de shapefiles ausente: {shp_base}\n"
                f"  Configure 'external_shapefiles_dir' no config.yaml"
            )
        else:
            for shp in shapefiles:
                if not shp.exists():
                    errors.append(f"Shapefile ausente: {shp}")

        return errors

    def generate(self, force: bool = False) -> FigureMetadata:
        """Executa script R para gerar mapa de PIB per capita.

        Args:
            force: Se True, regenera mesmo se arquivo já existe e está atualizado.

        Returns:
            Metadados da figura gerada.

        Raises:
            RuntimeError: Se validação falhar ou script R falhar.
        """
        script_dir = Path(self.config["r_scripts_dir"])
        script_path = script_dir / self.SCRIPT_NAME
        output_path = self.output_dir / self.FIGURE_NAME

        # Validar dependências
        errors = self.validate_dependencies()
        if errors:
            raise RuntimeError(
                f"Dependências ausentes para {self.FIGURE_NAME}:\n"
                + "\n".join(f"  - {e}" for e in errors)
            )

        # Validar script R existe
        if not script_path.exists():
            raise RuntimeError(f"Script R ausente: {script_path}")

        # Coletar dependências para timestamp
        data_dir = Path(self.config["external_data_dir"])
        dependencies = [
            script_path,
            data_dir / "dataset_completo_com_pib_relativo.rds",
        ]

        # Verificar se precisa regenerar
        if not force and not self.needs_regeneration(output_path, dependencies):
            logger.info(f"{self.FIGURE_NAME} está atualizado, pulando geração")
            return FigureMetadata(
                name=self.FIGURE_NAME,
                output_path=output_path,
                script_path=script_path,
                dependencies=dependencies,
                description="Distribuição do PIB per capita relativo (2002, 2010, 2019, 2021)",
            )

        # Executar script R
        logger.info(f"Gerando {self.FIGURE_NAME}...")
        runner = RScriptRunner(self.config.get("r_executable"))
        runner.run(script_path, cwd=script_dir)

        # Script R salva em tese/output/maps/ - precisamos copiar
        tese_output = (
            Path("C:/OneDrive/github/tese/bulding_dataset_R/output/maps")
            / self.FIGURE_NAME
        )

        if not tese_output.exists():
            raise RuntimeError(
                f"Script R não gerou {self.FIGURE_NAME} no local esperado: {tese_output}"
            )

        # Copiar para figures/
        shutil.copy2(tese_output, output_path)
        logger.info(f"Figura copiada de {tese_output} para {output_path}")

        return FigureMetadata(
            name=self.FIGURE_NAME,
            output_path=output_path,
            script_path=script_path,
            dependencies=dependencies,
            description="Distribuição do PIB per capita relativo (2002, 2010, 2019, 2021)",
        )
