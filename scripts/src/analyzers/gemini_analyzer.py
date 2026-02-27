"""Analisador LLM via Google GenAI SDK (google-genai).

Usa google.genai para enviar texto extraído de PDFs ao Gemini
e parsear respostas estruturadas baseadas em questionários.
"""

from __future__ import annotations

import logging
import re
import time
from typing import Any, Dict, List, Optional

from google import genai
from google.genai import types

from src.models import ScreeningStatus

from src.analyzers.base import BaseAnalyzer, load_questionnaire
from src.models import PaperRecord

logger = logging.getLogger("pndr_survey")

# Frases introdutórias que o modelo pode inserir antes das respostas
_INTRO_PHRASES = [
    "aqui estão as respostas",
    "baseado no estudo",
    "com base no documento",
    "analisando o documento",
    "para o questionário",
    "seguindo as instruções",
    "conforme solicitado",
    "here are the answers",
    "based on the study",
]


class GeminiAnalyzer(BaseAnalyzer):
    """Análise de papers via API Gemini (google.genai SDK)."""

    def __init__(
        self,
        *,
        api_key: str,
        model: str = "gemini-2.5-flash",
        temperature: float = 0.1,
        max_tokens_input: int = 100_000,
        rate_limit_seconds: float = 4.0,
        max_retries: int = 3,
    ):
        """
        Args:
            api_key: Chave da API Gemini.
            model: ID do modelo (ex: gemini-2.5-flash, gemini-2.5-pro).
            temperature: Temperatura de geração (0.0-1.0).
            max_tokens_input: Limite de tokens de entrada.
            rate_limit_seconds: Segundos entre chamadas à API.
            max_retries: Tentativas máximas por chamada.
        """
        self.model_name = model
        self.temperature = temperature
        self.max_tokens_input = max_tokens_input
        self.rate_limit_seconds = rate_limit_seconds
        self.max_retries = max_retries

        self._client = genai.Client(api_key=api_key)
        self._gen_config = types.GenerateContentConfig(
            temperature=temperature,
        )
        self._last_call_time = 0.0

    def analyze(
        self, paper: PaperRecord, questionnaire: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analisa um paper com o questionário via Gemini.

        Args:
            paper: PaperRecord com _extracted_text disponível.
            questionnaire: Questionário JSON com questions[].

        Returns:
            Dict mapeando question_id → resposta parseada.

        Raises:
            RuntimeError: Se todas as tentativas falharem.
        """
        text = getattr(paper, "_extracted_text", None) or paper.text_preview
        if not text:
            raise ValueError(
                f"Sem texto extraído para {paper.bib.citation_key}"
            )

        prompt = _build_prompt(text, questionnaire)
        response_text = self._call_api(prompt)

        question_ids = _extract_question_ids(questionnaire)
        result = _parse_response(response_text, question_ids)

        # Registrar metadados
        paper.model_used = self.model_name

        return result

    def analyze_batch(
        self,
        papers: List[PaperRecord],
        questionnaire: Dict[str, Any],
    ) -> List[PaperRecord]:
        """Analisa papers em lote com rate limiting entre chamadas."""
        stage = questionnaire.get("metadata", {}).get("stage", 1)
        stage_key = f"stage_{stage}"

        logger.info(
            "Analisando %d papers (Stage %d: %s) com %s",
            len(papers),
            stage,
            questionnaire.get("metadata", {}).get("name", ""),
            self.model_name,
        )

        ok = 0
        fail = 0

        for i, paper in enumerate(papers):
            try:
                result = self.analyze(paper, questionnaire)
                setattr(paper, stage_key, result)
                ok += 1
                logger.debug(
                    "OK: %s (Stage %d)", paper.bib.citation_key, stage
                )
            except Exception as e:
                paper.processing_errors.append(f"Stage {stage}: {e}")
                fail += 1
                logger.warning(
                    "Falha: %s (Stage %d): %s",
                    paper.bib.citation_key, stage, e,
                )

            if (i + 1) % 5 == 0:
                logger.info(
                    "Progresso Stage %d: %d/%d (%d ok, %d falhas)",
                    stage, i + 1, len(papers), ok, fail,
                )

        logger.info(
            "Stage %d concluído: %d ok, %d falhas de %d papers",
            stage, ok, fail, len(papers),
        )

        return papers

    def _call_api(self, prompt: str) -> str:
        """Chama a API Gemini com retry e rate limiting.

        Args:
            prompt: Texto completo do prompt (instruções + paper + questões).

        Returns:
            Texto da resposta do modelo.

        Raises:
            RuntimeError: Se todas as tentativas falharem.
        """
        self._wait_rate_limit()

        last_error: Optional[Exception] = None

        for attempt in range(1, self.max_retries + 1):
            try:
                response = self._client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                    config=self._gen_config,
                )
                self._last_call_time = time.time()
                return response.text.strip()

            except Exception as e:
                last_error = e
                if attempt < self.max_retries:
                    wait = 2 ** attempt
                    logger.warning(
                        "Tentativa %d/%d falhou: %s. Aguardando %ds...",
                        attempt, self.max_retries, e, wait,
                    )
                    time.sleep(wait)

        raise RuntimeError(
            f"API Gemini falhou após {self.max_retries} tentativas: "
            f"{last_error}"
        )

    def analyze_pipeline(
        self,
        papers: List[PaperRecord],
        questionnaires_dir: str,
    ) -> List[PaperRecord]:
        """Executa pipeline completo: Stage 1 → filtro → Stages 2+3.

        Sequência:
          1. Stage 1 (triagem) em todos os papers
          2. Filtrar: apenas papers com is_scientific_study=='Sim'
             e instrumentos_pndr != 'nenhum' avançam
          3. Stage 2 (metodologia) nos papers filtrados
          4. Stage 3 (resultados) nos papers filtrados

        Args:
            papers: Lista de PaperRecords com texto extraído.
            questionnaires_dir: Diretório com os 3 JSONs de questionário.

        Returns:
            Lista completa de PaperRecords (com stages preenchidos
            onde aplicável).
        """
        from pathlib import Path

        qdir = Path(questionnaires_dir)

        # --- Stage 1: Triagem ---
        q1 = load_questionnaire(qdir / "stage_1_screening.json")
        self.analyze_batch(papers, q1)

        # --- Filtro pós-triagem ---
        passed, rejected = filter_screening(papers)
        logger.info(
            "Filtro pós-triagem: %d passaram, %d rejeitados",
            len(passed), len(rejected),
        )

        if not passed:
            logger.warning("Nenhum paper passou na triagem.")
            return papers

        # --- Stage 2: Metodologia ---
        q2 = load_questionnaire(qdir / "stage_2_methods.json")
        self.analyze_batch(passed, q2)

        # --- Stage 3: Resultados ---
        q3 = load_questionnaire(qdir / "stage_3_results.json")
        self.analyze_batch(passed, q3)

        return papers

    def _wait_rate_limit(self) -> None:
        """Aguarda o rate limit entre chamadas."""
        elapsed = time.time() - self._last_call_time
        if elapsed < self.rate_limit_seconds:
            wait = self.rate_limit_seconds - elapsed
            time.sleep(wait)


# --- Filtragem pós-triagem ---


def filter_screening(
    papers: List[PaperRecord],
) -> tuple[List[PaperRecord], List[PaperRecord]]:
    """Filtra papers após Stage 1 (triagem).

    Critérios para passar (TODOS devem ser verdadeiros):
      - is_scientific_study contém "Sim"
      - instrumentos_pndr NÃO é apenas "nenhum" ou "[ne]"
      - uso_econometria contém "Sim"

    Preenche paper.is_empirical e paper.bib.screening_status.
    Hierarquia: is_study → has_instruments → uses_econometrics
    (primeira falha determina o motivo de exclusão).

    Args:
        papers: Lista de PaperRecords com stage_1 preenchido.

    Returns:
        Tupla (passed, rejected).
    """
    passed: List[PaperRecord] = []
    rejected: List[PaperRecord] = []

    for paper in papers:
        if paper.stage_1 is None:
            rejected.append(paper)
            continue

        s1 = paper.stage_1
        is_study = _answer_contains(s1.get("is_scientific_study", ""), "sim")
        instruments = s1.get("instrumentos_pndr", "")
        has_instruments = (
            instruments
            and not _answer_is_empty(instruments)
            and "nenhum" not in instruments.lower()
        )
        uses_econometrics = _answer_contains(
            s1.get("uso_econometria", ""), "sim"
        )

        if is_study and has_instruments and uses_econometrics:
            paper.is_empirical = True
            paper.pndr_instrument = _extract_first_instrument(instruments)
            paper.bib.screening_status = ScreeningStatus.INCLUDED
            passed.append(paper)
        else:
            paper.is_empirical = False
            if not is_study:
                paper.bib.screening_status = ScreeningStatus.EXCLUDED_DOCTYPE
                paper.bib.exclusion_reason = "LLM: não é estudo científico"
            elif not has_instruments:
                paper.bib.screening_status = ScreeningStatus.EXCLUDED_RELEVANCE
                paper.bib.exclusion_reason = "LLM: sem instrumentos PNDR"
            else:
                paper.bib.screening_status = ScreeningStatus.EXCLUDED_NO_ECONOMETRICS
                paper.bib.exclusion_reason = "LLM: sem método econométrico"
            rejected.append(paper)

    return passed, rejected


def _answer_contains(answer: str, value: str) -> bool:
    """Verifica se a resposta contém o valor (ignora referências [p.X])."""
    clean = re.sub(r"\[p\.\d+[;\d]*\]", "", answer).strip()
    return value.lower() in clean.lower()


def _answer_is_empty(answer: str) -> bool:
    """Verifica se a resposta é vazia ou [ne]."""
    clean = answer.strip().lower()
    return clean in ("", "[ne]", "ne", "n/a", "não se aplica")


def _extract_first_instrument(instruments_str: str) -> str:
    """Extrai o primeiro instrumento PNDR mencionado."""
    known = ["FNE", "FNO", "FCO", "FDA", "FDNE", "FDCO"]
    upper = instruments_str.upper()
    for inst in known:
        if inst in upper:
            return inst
    # Fallback: retornar a resposta limpa
    clean = re.sub(r"\[p\.\d+[;\d]*\]", "", instruments_str).strip()
    return clean[:50] if clean else ""


# --- Construção de prompt ---


def _build_prompt(paper_text: str, questionnaire: Dict[str, Any]) -> str:
    """Constrói o prompt completo: contexto + instruções + questionário + texto.

    Args:
        paper_text: Texto extraído do PDF.
        questionnaire: Dicionário do questionário JSON.

    Returns:
        Prompt formatado para envio ao LLM.
    """
    instructions = questionnaire.get("instructions", {})
    context = instructions.get(
        "context",
        "Você é um pesquisador na área de economia empírica com experiência "
        "em revisões sistemáticas de literatura.",
    )
    guidelines = instructions.get("guidelines", [])

    questions = questionnaire.get("questions", [])
    questions_text = _format_questions(questions)

    guidelines_text = "\n".join(f"    - {g}" for g in guidelines)

    prompt = f"""Contexto: {context}

Instruções:
{guidelines_text}
    - CRÍTICO: Responder APENAS com as respostas numeradas, uma por linha
    - NÃO incluir qualquer texto introdutório ou explicativo
    - NÃO repetir as perguntas nas respostas
    - Começar diretamente com "1. [sua resposta]"

Questionário (responder cada item em linha separada):
{questions_text}

Formato esperado:
1. [resposta]
2. [resposta]
...

--- TEXTO DO ESTUDO ---

{paper_text}"""

    return prompt


def _format_questions(questions: List[Dict[str, Any]]) -> str:
    """Formata a lista de questões para incluir no prompt."""
    lines = []
    for i, q in enumerate(questions, 1):
        title = q.get("title", f"Questão {i}")
        line = f"    {i}. {title}"

        q_type = q.get("type", "text")
        if q_type in ("select", "multiselect") and "options" in q:
            opts = ", ".join(q["options"])
            line += f"\n       Opções: {opts}"

        if "common_values" in q:
            vals = ", ".join(q["common_values"])
            line += f"\n       Valores comuns: {vals}"

        lines.append(line)

    return "\n".join(lines)


# --- Parsing de respostas ---


def _extract_question_ids(questionnaire: Dict[str, Any]) -> List[str]:
    """Extrai lista ordenada de question IDs do questionário."""
    questions = questionnaire.get("questions", [])
    return [q.get("id", f"q_{i}") for i, q in enumerate(questions, 1)]


def _parse_response(
    response_text: str, question_ids: List[str]
) -> Dict[str, str]:
    """Parseia resposta do LLM em dicionário {question_id: resposta}.

    Espera formato:
        1. resposta um
        2. resposta dois
        ...

    Args:
        response_text: Texto bruto retornado pelo modelo.
        question_ids: Lista de IDs das questões na ordem do questionário.

    Returns:
        Dicionário {question_id: resposta_limpa}.
    """
    lines = response_text.split("\n")
    lines = [line.strip() for line in lines if line.strip()]

    # Remover linhas introdutórias
    lines = _remove_intro_lines(lines)

    # Extrair respostas numeradas
    answers = _extract_numbered_answers(lines)

    # Mapear para question IDs
    result: Dict[str, str] = {}
    for i, qid in enumerate(question_ids):
        if i < len(answers):
            result[qid] = answers[i] if answers[i] else "[ne]"
        else:
            result[qid] = "[ne]"

    return result


def _remove_intro_lines(lines: List[str]) -> List[str]:
    """Remove linhas introdutórias do início da resposta."""
    while lines:
        first = lines[0].lower()
        if any(phrase in first for phrase in _INTRO_PHRASES):
            lines = lines[1:]
            continue
        break
    return lines


def _extract_numbered_answers(lines: List[str]) -> List[str]:
    """Extrai respostas de linhas numeradas (1. resposta, 2. resposta, ...).

    Lida com respostas multi-linha: se uma linha não começa com número,
    é concatenada à resposta anterior.
    """
    answers: List[str] = []
    current: Optional[str] = None
    number_pattern = re.compile(r"^\d+[\.\)]\s*")

    for line in lines:
        if number_pattern.match(line):
            if current is not None:
                answers.append(current.strip())
            # Remover numeração
            current = number_pattern.sub("", line)
        elif current is not None:
            # Continuação da resposta anterior
            current += " " + line

    if current is not None:
        answers.append(current.strip())

    return answers
