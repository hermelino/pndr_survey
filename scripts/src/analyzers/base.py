"""Interface abstrata para analisadores LLM."""

from __future__ import annotations

import json
import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List

from src.models import PaperRecord

logger = logging.getLogger("pndr_survey")


class BaseAnalyzer(ABC):
    """Interface comum para analisadores LLM (Gemini, OpenAI, etc.)."""

    @abstractmethod
    def analyze(
        self, paper: PaperRecord, questionnaire: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analisa um paper usando o questionário fornecido.

        Args:
            paper: PaperRecord com texto extraído (via _extracted_text).
            questionnaire: Dicionário do questionário JSON.

        Returns:
            Dicionário com respostas mapeadas por question_id.
        """

    def analyze_batch(
        self,
        papers: List[PaperRecord],
        questionnaire: Dict[str, Any],
    ) -> List[PaperRecord]:
        """Analisa uma lista de papers com o questionário.

        Args:
            papers: Lista de PaperRecords com texto extraído.
            questionnaire: Dicionário do questionário JSON.

        Returns:
            Lista de PaperRecords com stage preenchido.
        """
        stage = questionnaire.get("metadata", {}).get("stage", 1)
        stage_key = f"stage_{stage}"

        logger.info(
            "Analisando %d papers (Stage %d: %s)",
            len(papers),
            stage,
            questionnaire.get("metadata", {}).get("name", ""),
        )

        for i, paper in enumerate(papers):
            try:
                result = self.analyze(paper, questionnaire)
                setattr(paper, stage_key, result)
                logger.debug(
                    "OK: %s (Stage %d)", paper.bib.citation_key, stage
                )
            except Exception as e:
                paper.processing_errors.append(
                    f"Stage {stage}: {e}"
                )
                logger.warning(
                    "Falha ao analisar %s (Stage %d): %s",
                    paper.bib.citation_key, stage, e,
                )

            if (i + 1) % 10 == 0:
                logger.info(
                    "Progresso Stage %d: %d/%d papers",
                    stage, i + 1, len(papers),
                )

        ok = sum(1 for p in papers if getattr(p, stage_key) is not None)
        logger.info(
            "Stage %d concluído: %d/%d papers analisados",
            stage, ok, len(papers),
        )

        return papers


def load_questionnaire(path: str | Path) -> Dict[str, Any]:
    """Carrega questionário JSON.

    Args:
        path: Caminho para o arquivo .json.

    Returns:
        Dicionário com o conteúdo do questionário.

    Raises:
        FileNotFoundError: Se o arquivo não existe.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Questionário não encontrado: {path}")

    with open(path, encoding="utf-8") as f:
        return json.load(f)
