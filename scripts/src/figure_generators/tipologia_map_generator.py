"""Gerador de mapa de tipologia regional (PNDR 2018)."""

from __future__ import annotations

import logging
import shutil
from pathlib import Path

from .base import FigureGenerator, FigureMetadata
from .r_wrapper import RScriptRunner

logger = logging.getLogger("pndr_survey.figures")


class TipologiaMapGenerator(FigureGenerator):
    """Gera mapa de tipologia regional da PNDR 2018.

    Executa script R `mapa_tipologia_simples.R` que produz mapa com 9 categorias
    resultantes do cruzamento de renda (alta/média/baixa) e dinamismo
    (dinâmica/intermediária/estagnada), com ano-base 2020.

    Dependências:
    - Dados: painel_balanc_var_ln_pibrpc.rds
    - Shapefiles: BR_Municipios_2021.shp, BR_UF_2021.shp
    - Opcionais: LIM_Semiarido_Municipal_OFICIAL.shp, Mun_Amazonia_Legal_2022.shp

    Figura gerada:
    - tipologia_II_simples_com_legenda.png (mapa único, paleta multicolorida)
    """

    FIGURE_NAME = "tipologia_II_simples_com_legenda.png"
    SCRIPT_NAME = "mapa_tipologia_simples.R"

    def validate_dependencies(self) -> list[str]:
        """Valida existência de dados RDS e shapefiles necessários.

        Returns:
            Lista de mensagens de erro (vazia se todas as dependências OK).
        """
        errors = []

        # Dados RDS
        data_dir = Path(self.config["external_data_dir"])
        rds_file = data_dir / "painel_balanc_var_ln_pibrpc.rds"

        if not data_dir.exists():
            errors.append(
                f"Diretório de dados ausente: {data_dir}\n"
                f"  Configure 'external_data_dir' no config.yaml"
            )
        elif not rds_file.exists():
            errors.append(f"Dado RDS ausente: {rds_file}")

        # Shapefiles obrigatórios
        shp_base = Path(self.config["external_shapefiles_dir"])
        shapefiles_required = [
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
            for shp in shapefiles_required:
                if not shp.exists():
                    errors.append(f"Shapefile ausente: {shp}")

        # Shapefiles opcionais (sobreposições) - apenas avisar se ausentes
        shapefiles_optional = [
            shp_base
            / "DIVISÃO POLÍTICA E REGIONAL"
            / "LIM_Semiarido_Municipal_OFICIAL"
            / "LIM_Semiarido_Municipal_OFICIAL.shp",
            shp_base
            / "DIVISÃO POLÍTICA E REGIONAL"
            / "AMAZONIA LEGAL"
            / "Mun_Amazonia_Legal_2022_shp"
            / "Mun_Amazonia_Legal_2022.shp",
        ]

        for shp in shapefiles_optional:
            if not shp.exists():
                logger.warning(
                    f"Shapefile opcional ausente (sobreposições omitidas): {shp.name}"
                )

        return errors

    def generate(self, force: bool = False) -> FigureMetadata:
        """Executa script R para gerar mapa de tipologia regional.

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
            data_dir / "painel_balanc_var_ln_pibrpc.rds",
        ]

        # Verificar se precisa regenerar
        if not force and not self.needs_regeneration(output_path, dependencies):
            logger.info(f"{self.FIGURE_NAME} está atualizado, pulando geração")
            return FigureMetadata(
                name=self.FIGURE_NAME,
                output_path=output_path,
                script_path=script_path,
                dependencies=dependencies,
                description="Tipologia regional PNDR 2018 (9 categorias: renda × dinamismo)",
            )

        # Executar script R
        logger.info(f"Gerando {self.FIGURE_NAME}...")
        runner = RScriptRunner(self.config.get("r_executable"))
        runner.run(script_path, cwd=script_dir)

        # Script R salva como "tipologia_simples.png" em tese/output/maps/
        # Mas queremos renomear para "tipologia_II_simples_com_legenda.png"
        tese_output = (
            Path("C:/OneDrive/github/tese/bulding_dataset_R/output/maps")
            / "tipologia_simples.png"
        )

        if not tese_output.exists():
            raise RuntimeError(
                f"Script R não gerou tipologia_simples.png no local esperado: {tese_output}"
            )

        # Copiar e renomear para figures/
        shutil.copy2(tese_output, output_path)
        logger.info(f"Figura copiada de {tese_output} para {output_path}")

        return FigureMetadata(
            name=self.FIGURE_NAME,
            output_path=output_path,
            script_path=script_path,
            dependencies=dependencies,
            description="Tipologia regional PNDR 2018 (9 categorias: renda × dinamismo)",
        )
