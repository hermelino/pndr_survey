# Templates Python — processar-dados

Templates de referência para scripts de processamento de dados do pndr_survey.
Referenciado por `/processar-dados`.

---

## Template: Tabela LaTeX (padrão C12)

```python
def generate_latex_table(
    df: pd.DataFrame,
    output_path: str,
    caption: str,
    label: str,
    fonte: str = "Elaboração própria.",
    nota: str = "",
    float_format: str = "%.2f"
) -> None:
    """Gera tabela LaTeX compatível com abntex2, padrão C12.

    Padrão C12 definido em `/revisor-latex` (verificações C5 e C12).

    Args:
        df: DataFrame com dados da tabela
        output_path: Caminho do arquivo .tex
        caption: Legenda da tabela
        label: Label para referência cruzada
        fonte: Texto da fonte (obrigatório)
        nota: Texto da nota (opcional)
        float_format: Formato de números decimais
    """
    n_cols = len(df.columns)
    footer_text = f"Nota: {nota} Fonte: {fonte}" if nota else f"Fonte: {fonte}"
    footer_line = (
        f"\\multicolumn{{{n_cols}}}{{l}}"
        f"{{\\footnotesize {footer_text}}} \\\\"
    )

    # Gerar corpo da tabela manualmente para inserir rodapé C12
    body = df.to_latex(
        index=False,
        escape=False,
        float_format=float_format,
    )
    # Inserir footer_line após \bottomrule
    body = body.replace("\\bottomrule", f"\\bottomrule\n{footer_line}")

    # Montar float completo
    latex_str = (
        f"\\begin{{table}}[htbp]\n"
        f"    \\centering\n"
        f"    \\caption{{{caption}}}\n"
        f"    \\label{{tab:{label}}}\n"
        f"    \\footnotesize\n"
        f"    \\renewcommand{{\\arraystretch}}{{1.2}}\n"
        f"    {body}"
        f"\\end{{table}}\n"
    )

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(latex_str)

    logging.info(f"Tabela LaTeX gerada (C12): {output_path}")
```

---

## Template: Gráfico acadêmico

```python
import matplotlib.pyplot as plt
import seaborn as sns

# Configuração global
plt.rcParams.update({
    'font.family': 'serif',
    'font.size': 11,
    'axes.labelsize': 11,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'legend.fontsize': 10,
    'figure.dpi': 300
})

def plot_time_series(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    output_path: str,
    title: str = "",
    xlabel: str = "",
    ylabel: str = ""
) -> None:
    """Gera gráfico de série temporal."""
    fig, ax = plt.subplots(figsize=(8, 5))

    ax.plot(df[x_col], df[y_col], linewidth=2, color='#2E86AB')
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.grid(alpha=0.3, linestyle='--')

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.savefig(output_path.replace('.png', '.pdf'), bbox_inches='tight')
    plt.close()

    logging.info(f"Gráfico gerado: {output_path}")
```

---

## Template: Estatísticas descritivas

```python
from dataclasses import dataclass
from typing import Dict, Any
import pandas as pd

@dataclass
class DescriptiveStats:
    """Estatísticas descritivas de uma variável."""
    n: int
    mean: float
    std: float
    min: float
    q25: float
    median: float
    q75: float
    max: float
    missing: int

    @classmethod
    def from_series(cls, series: pd.Series) -> 'DescriptiveStats':
        """Calcula estatísticas de uma Series."""
        return cls(
            n=series.notna().sum(),
            mean=series.mean(),
            std=series.std(),
            min=series.min(),
            q25=series.quantile(0.25),
            median=series.median(),
            q75=series.quantile(0.75),
            max=series.max(),
            missing=series.isna().sum()
        )

    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário."""
        return {
            'N': self.n,
            'Média': self.mean,
            'Desvio-padrão': self.std,
            'Mínimo': self.min,
            'Q1': self.q25,
            'Mediana': self.median,
            'Q3': self.q75,
            'Máximo': self.max,
            'Ausentes': self.missing
        }

def generate_descriptive_table(
    df: pd.DataFrame,
    variables: list[str],
    output_path: str
) -> pd.DataFrame:
    """Gera tabela de estatísticas descritivas."""
    stats = {}
    for var in variables:
        stats[var] = DescriptiveStats.from_series(df[var]).to_dict()

    stats_df = pd.DataFrame(stats).T
    stats_df.to_excel(output_path)

    return stats_df
```

---

## Template: Validação de dados

```python
def validate_dataset(df: pd.DataFrame, schema: Dict[str, Any]) -> list[str]:
    """Valida dataset contra schema esperado.

    Args:
        df: DataFrame a validar
        schema: Dict com especificações {col: {'type': type, 'required': bool}}

    Returns:
        Lista de erros encontrados
    """
    errors = []

    for col, specs in schema.items():
        if col not in df.columns:
            if specs.get('required', False):
                errors.append(f"Coluna obrigatória ausente: {col}")
            continue

        if specs.get('required') and df[col].isna().any():
            n_missing = df[col].isna().sum()
            errors.append(f"Coluna {col}: {n_missing} valores ausentes")

        expected_type = specs.get('type')
        if expected_type and not df[col].dtype == expected_type:
            errors.append(f"Coluna {col}: tipo esperado {expected_type}, encontrado {df[col].dtype}")

    return errors
```
