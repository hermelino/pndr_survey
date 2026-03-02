"""Módulo de geração de figuras para o artigo LaTeX.

Este módulo fornece wrappers Python para scripts R de geração de figuras,
permitindo validação de dependências, geração incremental (baseada em timestamps)
e integração com o pipeline pndr_survey.

Classes principais:
- FigureGenerator: Classe base abstrata para geradores
- RScriptRunner: Executor de scripts R com auto-detecção
- PIBMapGenerator: Gera mapa de distribuição PIB per capita
- TipologiaMapGenerator: Gera mapa de tipologia regional
- ICFPlotGenerator: Gera gráfico de incentivos fiscais
"""

from .base import FigureGenerator, FigureMetadata
from .icf_plot_generator import ICFPlotGenerator
from .pib_map_generator import PIBMapGenerator
from .r_wrapper import RScriptRunner
from .tipologia_map_generator import TipologiaMapGenerator

__all__ = [
    "FigureGenerator",
    "FigureMetadata",
    "RScriptRunner",
    "PIBMapGenerator",
    "TipologiaMapGenerator",
    "ICFPlotGenerator",
]
