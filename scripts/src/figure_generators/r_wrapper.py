"""Wrapper para executar scripts R via subprocess."""

from __future__ import annotations

import logging
import shutil
import subprocess
from pathlib import Path

logger = logging.getLogger("pndr_survey.figures")


class RScriptRunner:
    """Executor de scripts R com auto-detecção e logging robusto.

    Localiza automaticamente o executável Rscript.exe via:
    1. Caminho explícito fornecido no construtor
    2. PATH do sistema (shutil.which)
    3. Paths comuns no Windows (C:/Program Files/R/R-*/bin/Rscript.exe)

    Executa scripts R com timeout, captura stdout/stderr e loga resultados.

    Attributes:
        r_executable: Path para o executável Rscript.exe

    Example:
        >>> runner = RScriptRunner()
        >>> runner.run(Path("script.R"), cwd=Path("scripts"))
    """

    def __init__(self, r_executable: str | None = None):
        """Inicializa runner R.

        Args:
            r_executable: Caminho explícito para Rscript.exe (auto-detect se None).

        Raises:
            RuntimeError: Se Rscript.exe não for encontrado.
        """
        self.r_executable = self._find_r_executable(r_executable)

    def _find_r_executable(self, explicit_path: str | None) -> Path:
        """Localiza executável Rscript.exe.

        Args:
            explicit_path: Caminho explícito fornecido pelo usuário.

        Returns:
            Path para Rscript.exe.

        Raises:
            RuntimeError: Se não encontrar Rscript.exe.
        """
        # Tentar caminho explícito primeiro
        if explicit_path:
            path = Path(explicit_path)
            if path.exists():
                logger.info(f"Usando Rscript explícito: {path}")
                return path
            logger.warning(
                f"Rscript não encontrado em {explicit_path}, tentando auto-detect"
            )

        # Auto-detect via PATH do sistema
        rscript = shutil.which("Rscript")
        if rscript:
            path = Path(rscript)
            logger.info(f"Rscript encontrado via PATH: {path}")
            return path

        # Procurar em paths comuns do Windows
        common_bases = [
            Path("C:/Program Files/R"),
            Path("C:/Program Files (x86)/R"),
        ]

        for base in common_bases:
            if not base.exists():
                continue

            # Procurar versões (ex: R-4.4.2), mais recente primeiro
            r_versions = sorted(base.glob("R-*"), reverse=True)
            for r_dir in r_versions:
                rscript_path = r_dir / "bin" / "Rscript.exe"
                if rscript_path.exists():
                    logger.info(f"Rscript encontrado em: {rscript_path}")
                    return rscript_path

        # Não encontrado
        raise RuntimeError(
            "Rscript.exe não encontrado.\n"
            "Instale R ou configure 'r_executable' no config.yaml.\n"
            "Download R: https://cran.r-project.org/bin/windows/base/\n"
            "\n"
            "Após instalar, configure em scripts/config.yaml:\n"
            "  figures:\n"
            '    r_executable: "C:/Program Files/R/R-4.4.2/bin/Rscript.exe"'
        )

    def run(
        self, script_path: Path, cwd: Path | None = None
    ) -> subprocess.CompletedProcess:
        """Executa script R.

        Args:
            script_path: Caminho do script .R
            cwd: Diretório de trabalho (default: dir do script)

        Returns:
            CompletedProcess com stdout/stderr.

        Raises:
            FileNotFoundError: Se script não existir.
            RuntimeError: Se script R falhar (exit code != 0) ou timeout.

        Example:
            >>> runner = RScriptRunner()
            >>> result = runner.run(Path("mapa.R"), cwd=Path("r_scripts"))
            >>> print(result.stdout)
        """
        if not script_path.exists():
            raise FileNotFoundError(f"Script R não encontrado: {script_path}")

        cwd = cwd or script_path.parent

        logger.info(f"Executando script R: {script_path.name}")
        logger.debug(f"  Executável: {self.r_executable}")
        logger.debug(f"  Diretório: {cwd}")

        try:
            result = subprocess.run(
                [str(self.r_executable), str(script_path)],
                cwd=str(cwd),
                capture_output=True,
                text=True,
                timeout=300,  # 5 minutos max
                check=True,  # Raise CalledProcessError se exit code != 0
            )

            # Logar stdout (output_helpers.R imprime paths salvos)
            if result.stdout:
                for line in result.stdout.strip().split("\n"):
                    if line.strip():
                        logger.debug(f"[R stdout] {line}")

            # Logar stderr (warnings do R)
            if result.stderr:
                for line in result.stderr.strip().split("\n"):
                    if line.strip():
                        logger.warning(f"[R stderr] {line}")

            logger.info(f"Script R concluído com sucesso: {script_path.name}")
            return result

        except subprocess.CalledProcessError as e:
            logger.error(f"Script R falhou: {script_path.name}")
            if e.stdout:
                logger.error(f"stdout:\n{e.stdout}")
            if e.stderr:
                logger.error(f"stderr:\n{e.stderr}")
            raise RuntimeError(
                f"Script R falhou: {script_path.name}\n"
                f"Exit code: {e.returncode}\n"
                f"Stderr: {e.stderr}"
            ) from e

        except subprocess.TimeoutExpired as e:
            logger.error(f"Timeout ao executar {script_path.name}")
            raise RuntimeError(
                f"Script R excedeu timeout de 5 minutos: {script_path.name}"
            ) from e
