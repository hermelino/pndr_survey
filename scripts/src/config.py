"""Carregamento e validação de configuração YAML.

Suporta resolução de variáveis de ambiente no formato ${VAR_NAME}.
Exemplo: api_key: "${GEMINI_API_KEY}" → lê de os.environ.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


# --- Dataclasses de configuração ---


@dataclass
class SearchConfig:
    """Configuração da fase de busca."""
    databases: List[str] = field(default_factory=lambda: ["econpapers"])
    keywords_dir: str = "keywords"
    date_start: int = 2000
    date_end: int = 2025
    max_results_per_db: int = 1000


@dataclass
class DedupConfig:
    """Configuração de deduplicação."""
    fuzzy_threshold: int = 90
    title_normalization: bool = True


@dataclass
class LLMConfig:
    """Configuração do provedor LLM."""
    provider: str = "gemini"
    model: str = "gemini-2.0-flash"
    api_key: str = ""
    temperature: float = 0.1
    max_tokens_input: int = 100_000
    rate_limit_seconds: float = 4.0


@dataclass
class PathsConfig:
    """Caminhos do projeto."""
    papers_dir: str = "../data/papers"
    questionnaires_dir: str = "questionnaires"


@dataclass
class OutputConfig:
    """Configuração de saída."""
    directory: str = "../data/processed"
    formats: List[str] = field(default_factory=lambda: ["excel", "csv", "json"])
    timestamp: bool = True


@dataclass
class LoggingConfig:
    """Configuração de logging."""
    level: str = "INFO"
    file_level: str = "DEBUG"


@dataclass
class Config:
    """Configuração raiz do projeto."""
    search: SearchConfig = field(default_factory=SearchConfig)
    dedup: DedupConfig = field(default_factory=DedupConfig)
    llm: LLMConfig = field(default_factory=LLMConfig)
    paths: PathsConfig = field(default_factory=PathsConfig)
    output: OutputConfig = field(default_factory=OutputConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)


# --- Resolução de variáveis de ambiente ---

_ENV_PATTERN = re.compile(r"\$\{([^}]+)\}")


def _resolve_env_vars(value: Any) -> Any:
    """Substitui ${VAR_NAME} pelo valor de os.environ[VAR_NAME].

    Percorre recursivamente dicts e lists.
    Retorna o valor original se não for string ou não contiver ${}.
    """
    if isinstance(value, str):
        def _replace(match: re.Match) -> str:
            var_name = match.group(1)
            env_value = os.environ.get(var_name, "")
            return env_value
        return _ENV_PATTERN.sub(_replace, value)

    if isinstance(value, dict):
        return {k: _resolve_env_vars(v) for k, v in value.items()}

    if isinstance(value, list):
        return [_resolve_env_vars(item) for item in value]

    return value


# --- Carregamento ---

# Instâncias sentinela para acessar defaults
_SEARCH = SearchConfig()
_DEDUP = DedupConfig()
_LLM = LLMConfig()
_PATHS = PathsConfig()
_OUTPUT = OutputConfig()
_LOGGING = LoggingConfig()


def _build_search_config(data: Dict) -> SearchConfig:
    raw = data.get("search", {})
    date_range = raw.get("date_range", {})
    return SearchConfig(
        databases=raw.get("databases", _SEARCH.databases),
        keywords_dir=raw.get("keywords_dir", _SEARCH.keywords_dir),
        date_start=date_range.get("start", _SEARCH.date_start),
        date_end=date_range.get("end", _SEARCH.date_end),
        max_results_per_db=raw.get("max_results_per_db", _SEARCH.max_results_per_db),
    )


def _build_dedup_config(data: Dict) -> DedupConfig:
    raw = data.get("dedup", {})
    return DedupConfig(
        fuzzy_threshold=raw.get("fuzzy_threshold", _DEDUP.fuzzy_threshold),
        title_normalization=raw.get("title_normalization", _DEDUP.title_normalization),
    )


def _build_llm_config(data: Dict) -> LLMConfig:
    raw = data.get("llm", {})
    return LLMConfig(
        provider=raw.get("provider", _LLM.provider),
        model=raw.get("model", _LLM.model),
        api_key=raw.get("api_key", _LLM.api_key),
        temperature=raw.get("temperature", _LLM.temperature),
        max_tokens_input=raw.get("max_tokens_input", _LLM.max_tokens_input),
        rate_limit_seconds=raw.get("rate_limit_seconds", _LLM.rate_limit_seconds),
    )


def _build_paths_config(data: Dict) -> PathsConfig:
    raw = data.get("paths", {})
    return PathsConfig(
        papers_dir=raw.get("papers_dir", _PATHS.papers_dir),
        questionnaires_dir=raw.get("questionnaires_dir", _PATHS.questionnaires_dir),
    )


def _build_output_config(data: Dict) -> OutputConfig:
    raw = data.get("output", {})
    return OutputConfig(
        directory=raw.get("directory", _OUTPUT.directory),
        formats=raw.get("formats", _OUTPUT.formats),
        timestamp=raw.get("timestamp", _OUTPUT.timestamp),
    )


def _build_logging_config(data: Dict) -> LoggingConfig:
    raw = data.get("logging", {})
    return LoggingConfig(
        level=raw.get("level", _LOGGING.level),
        file_level=raw.get("file_level", _LOGGING.file_level),
    )


def load_config(path: str | Path) -> Config:
    """Carrega configuração de um arquivo YAML.

    Args:
        path: Caminho para o arquivo config.yaml.

    Returns:
        Config populado com valores do YAML + variáveis de ambiente.

    Raises:
        FileNotFoundError: Se o arquivo não existe.
        ValueError: Se a configuração é inválida.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(
            f"Arquivo de configuração não encontrado: {path}\n"
            f"Copie config.example.yaml para config.yaml e preencha os valores."
        )

    with open(path, encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}

    # Resolver ${ENV_VARS} recursivamente
    data = _resolve_env_vars(raw)

    config = Config(
        search=_build_search_config(data),
        dedup=_build_dedup_config(data),
        llm=_build_llm_config(data),
        paths=_build_paths_config(data),
        output=_build_output_config(data),
        logging=_build_logging_config(data),
    )

    _validate(config)
    return config


def _validate(config: Config) -> None:
    """Validações básicas da configuração."""
    if not config.llm.api_key:
        raise ValueError(
            "Chave API do LLM não configurada.\n"
            "Defina a variável de ambiente GEMINI_API_KEY ou "
            "preencha llm.api_key no config.yaml."
        )

    valid_dbs = {"econpapers", "google_scholar", "capes", "scopus"}
    for db in config.search.databases:
        if db not in valid_dbs:
            raise ValueError(
                f"Base de dados desconhecida: '{db}'. "
                f"Opções válidas: {', '.join(sorted(valid_dbs))}"
            )

    if not 0 <= config.dedup.fuzzy_threshold <= 100:
        raise ValueError(
            f"fuzzy_threshold deve estar entre 0 e 100, "
            f"recebido: {config.dedup.fuzzy_threshold}"
        )
