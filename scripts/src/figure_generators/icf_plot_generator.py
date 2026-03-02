"""Gerador de gráfico de incentivos fiscais por superintendência e setor."""

from __future__ import annotations

import logging
import shutil
from pathlib import Path

from .base import FigureGenerator, FigureMetadata
from .r_wrapper import RScriptRunner

logger = logging.getLogger("pndr_survey.figures")


class ICFPlotGenerator(FigureGenerator):
    """Gera gráfico de incentivos fiscais por superintendência e setor.

    Executa script R `grafico_resumo_icf.R` que produz gráfico de barras
    empilhadas com facetas SUDENE/SUDAM, categorizado por tipologia 2007
    (Alta/Baixa Renda, Dinâmica/Estagnada) e breakdown por 6 setores
    (Indústria de Transformação, Infraestrutura, etc.), com linha vermelha
    sobreposta mostrando média per capita.

    Dependências:
    - Dados: classif_incent_fiscais.xlsx, painel_icf.rds, populacao_fc.rds
    - Auxiliar: tipologia_2007.xlsx

    Figura gerada:
    - icf_superint_setor.png (barras empilhadas + linha per capita)
    """

    FIGURE_NAME = "icf_superint_setor.png"
    SCRIPT_NAME = "grafico_resumo_icf.R"

    def validate_dependencies(self) -> list[str]:
        """Valida existência de dados RDS, Excel e auxiliares.

        Returns:
            Lista de mensagens de erro (vazia se todas as dependências OK).
        """
        errors = []

        # Dados RDS e Excel
        data_dir = Path(self.config["external_data_dir"])
        data_files = [
            data_dir / "classif_incent_fiscais.xlsx",
            data_dir / "painel_icf.rds",
            data_dir / "populacao_fc.rds",
        ]

        if not data_dir.exists():
            errors.append(
                f"Diretório de dados ausente: {data_dir}\n"
                f"  Configure 'external_data_dir' no config.yaml"
            )
        else:
            for data_file in data_files:
                if not data_file.exists():
                    errors.append(f"Dado ausente: {data_file}")

        # Tipologia 2007 (localização diferente)
        tipologia_2007 = (
            Path(self.config["external_shapefiles_dir"]) / "MUNICÍPIOS" / "tipologia_2007.xlsx"
        )

        if not tipologia_2007.exists():
            errors.append(f"Tipologia 2007 ausente: {tipologia_2007}")

        return errors

    def generate(self, force: bool = False) -> FigureMetadata:
        """Executa script R para gerar gráfico de incentivos fiscais.

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
            data_dir / "classif_incent_fiscais.xlsx",
            data_dir / "painel_icf.rds",
            data_dir / "populacao_fc.rds",
        ]

        # Verificar se precisa regenerar
        if not force and not self.needs_regeneration(output_path, dependencies):
            logger.info(f"{self.FIGURE_NAME} está atualizado, pulando geração")
            return FigureMetadata(
                name=self.FIGURE_NAME,
                output_path=output_path,
                script_path=script_path,
                dependencies=dependencies,
                description="Incentivos fiscais por superintendência e setor (SUDENE/SUDAM)",
            )

        # Executar script R
        logger.info(f"Gerando {self.FIGURE_NAME}...")
        runner = RScriptRunner(self.config.get("r_executable"))
        runner.run(script_path, cwd=script_dir)

        # Script R salva em tese/output/plots/ (não maps/) via save_plot()
        tese_output = (
            Path("C:/OneDrive/github/tese/bulding_dataset_R/output/plots")
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
            description="Incentivos fiscais por superintendência e setor (SUDENE/SUDAM)",
        )
