# Skill: processar-dados

## Objetivo

Converter, escrever e revisar scripts de manipulação de dados do projeto **tese** para o contexto do **pndr_survey**, incluindo:
- Limpeza e transformação de dados
- Merge e join de datasets
- Criação de variáveis derivadas
- Estatísticas descritivas
- Geração de tabelas (LaTeX, Excel, CSV)
- Geração de gráficos descritivos

**Exclusão:** Estimação de modelos econométricos (regressões, painéis, etc.)

## Contexto dos Projetos

### Projeto Tese (Fonte)
- **Localização:** `C:\OneDrive\github\tese`
- **Linguagem:** R
- **Diretórios principais:**
  - `bulding_dataset_R/source_code/` — Scripts de construção de datasets
  - `arquivos_latex/latex_tese/figuras/` — Gráficos gerados
- **Padrões:** Scripts R modulares, uso de tidyverse, ggplot2, data.table

### Projeto pndr_survey (Destino)
- **Localização:** `c:\OneDrive\github\pndr_survey`
- **Linguagem:** Python 3.12+ (conversão R → Python)
- **Estrutura:**
  - `scripts/` — Pipeline Python
  - `data/` — Dados processados (JSON, Excel, CSV)
  - `figures/` — Gráficos para o artigo
  - `latex/` — Tabelas LaTeX geradas
- **Stack:** pandas, matplotlib, seaborn, openpyxl

## Regras de Operação

### 1. Análise Inicial (Sempre Começar Aqui)

Quando invocado, PRIMEIRO:

a) **Identificar scripts R relevantes no projeto tese:**
   - Explorar `C:\OneDrive\github\tese\bulding_dataset_R\source_code\`
   - Listar scripts de manipulação de dados (excluir estimação de modelos)
   - Documentar inputs, outputs e transformações

b) **Mapear para pndr_survey:**
   - Identificar dados equivalentes em `data/2-papers/2-2-papers.json`
   - Verificar necessidades específicas (tabelas LaTeX, figuras, exports)

c) **Apresentar plano ao usuário:**
   - Listar scripts R identificados
   - Propor estrutura Python equivalente
   - Solicitar aprovação antes de converter

### 2. Conversão R → Python

**Princípios:**
- R tidyverse → pandas idiomático
- ggplot2 → matplotlib + seaborn (estilo acadêmico)
- data.table → pandas otimizado
- Manter lógica de negócio idêntica

**Padrões de Conversão:**

```r
# R (tidyverse)
df %>%
  filter(ano >= 2002) %>%
  group_by(regiao) %>%
  summarise(media = mean(valor, na.rm = TRUE))
```

```python
# Python (pandas)
df_summary = (df
    .query('ano >= 2002')
    .groupby('regiao')
    .agg(media=('valor', 'mean'))
    .reset_index()
)
```

**Estrutura de Scripts Python:**
- Type hints em todas as funções
- Docstrings estilo Google
- Logging via `logging` stdlib
- Configuração via `config.yaml` quando aplicável

### 3. Geração de Tabelas

**Para LaTeX:**
- Usar pandas `.to_latex()` com parâmetros ABNT
- Salvar em `latex/tabelas/` com nomenclatura descritiva
- Formato compatível com `abntex2` (booktabs, threeparttable)

**Para Excel:**
- Usar openpyxl para formatação
- Salvar em `data/` com timestamp

**Exemplo de Função:**

```python
def generate_latex_table(
    df: pd.DataFrame,
    output_path: str,
    caption: str,
    label: str,
    float_format: str = "%.2f"
) -> None:
    """Gera tabela LaTeX compatível com abntex2.

    Args:
        df: DataFrame com dados da tabela
        output_path: Caminho do arquivo .tex
        caption: Legenda da tabela
        label: Label para referência cruzada
        float_format: Formato de números decimais
    """
    latex_str = df.to_latex(
        index=False,
        escape=False,
        float_format=float_format,
        caption=caption,
        label=f'tab:{label}',
        position='htbp'
    )

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(latex_str)

    logging.info(f"Tabela LaTeX gerada: {output_path}")
```

### 4. Geração de Gráficos

**Estilo Acadêmico:**
- Fonte: Times New Roman ou similar serifada
- Tamanho: 10-12pt para labels
- Paleta: cores distintas para daltônicos
- Formatos: PNG (300 DPI) + PDF (vetorial)

**Template Base:**

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

### 5. Estatísticas Descritivas

**Módulo Padrão:**

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

### 6. Validação de Dados

**Checagens Obrigatórias:**
- Valores ausentes (NaN, None, "")
- Duplicatas (IDs, DOIs)
- Tipos de dados esperados
- Ranges válidos (anos, valores numéricos)
- Consistência entre datasets relacionados

**Template:**

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

### 7. Integração com Pipeline pndr_survey

**Localização de Scripts:**
- Scripts de processamento: `scripts/data_processing/`
- Scripts de visualização: `scripts/figures/`
- Utilitários: `scripts/src/utils/stats.py`

**Integração com CLI:**
```python
# Adicionar em scripts/main.py
def add_stats_subcommand(subparsers):
    parser = subparsers.add_parser('stats', help='Gerar estatísticas descritivas')
    parser.add_argument('--output', default='data/stats/', help='Diretório de saída')
    parser.add_argument('--format', choices=['excel', 'latex', 'both'], default='both')
    parser.set_defaults(func=run_stats)
```

### 8. Documentação

Para cada script convertido, criar:

1. **Docstring detalhado:**
   - Propósito do script
   - Script R original de referência
   - Inputs esperados
   - Outputs gerados
   - Dependências

2. **README.md no diretório:**
   - Mapeamento R → Python
   - Exemplos de uso
   - Diferenças importantes de implementação

## Workflow de Uso

### Modo 1: Conversão de Script Específico

```
User: /processar-dados converter fd_variables.R
```

**Ações:**
1. Ler script R original
2. Identificar inputs/outputs
3. Propor estrutura Python equivalente
4. Solicitar aprovação
5. Implementar conversão
6. Testar com dados reais
7. Documentar mapeamento

### Modo 2: Gerar Estatísticas Descritivas

```
User: /processar-dados stats --vars ano,instrumento,metodo
```

**Ações:**
1. Carregar `data/2-papers/2-2-papers.json`
2. Calcular estatísticas para variáveis especificadas
3. Gerar tabela Excel + LaTeX
4. Salvar em `data/stats/` e `latex/tabelas/`

### Modo 3: Gerar Gráfico

```
User: /processar-dados plot distribuicao-ano
```

**Ações:**
1. Identificar script R equivalente (se existir)
2. Carregar dados necessários
3. Gerar gráfico em estilo acadêmico
4. Salvar PNG + PDF em `figures/`

### Modo 4: Explorar Projeto Tese

```
User: /processar-dados explorar
```

**Ações:**
1. Listar todos os scripts R de manipulação de dados
2. Categorizar por tipo (limpeza, merge, transformação, viz)
3. Apresentar resumo ao usuário
4. Sugerir prioridades de conversão

## Checklist Pré-Conversão

Antes de converter qualquer script:

- [ ] Leu o script R original completamente
- [ ] Identificou todos os inputs (arquivos, variáveis)
- [ ] Identificou todos os outputs (arquivos, tabelas, gráficos)
- [ ] Verificou se dados equivalentes existem em pndr_survey
- [ ] Propôs estrutura Python ao usuário
- [ ] Recebeu aprovação explícita para proceder

## Checklist Pós-Conversão

Após implementar conversão:

- [ ] Script Python executa sem erros
- [ ] Outputs gerados são equivalentes ao R (validados)
- [ ] Type hints em todas as funções
- [ ] Docstrings completos
- [ ] Logging implementado
- [ ] Testes básicos passam
- [ ] Documentação criada (mapeamento R→Python)
- [ ] README atualizado

## Exemplo Completo

### Script R Original (tese)

```r
# C:\OneDrive\github\tese\bulding_dataset_R\source_code\descriptive_stats.R

library(tidyverse)

# Carregar dados
df <- read_csv("data/municipios.csv")

# Estatísticas descritivas
stats <- df %>%
  group_by(regiao) %>%
  summarise(
    n = n(),
    pib_medio = mean(pib, na.rm = TRUE),
    pib_sd = sd(pib, na.rm = TRUE)
  )

# Exportar
write_csv(stats, "output/stats_regiao.csv")
```

### Script Python Convertido (pndr_survey)

```python
# scripts/data_processing/regional_stats.py
"""
Estatísticas descritivas por região.

Script R original: C:/OneDrive/github/tese/bulding_dataset_R/source_code/descriptive_stats.R
Convertido para: pndr_survey
Data: 2026-03-03
"""

import logging
from pathlib import Path
import pandas as pd
from typing import Dict, Any

def calculate_regional_stats(input_path: str, output_dir: str) -> pd.DataFrame:
    """Calcula estatísticas descritivas por região.

    Args:
        input_path: Caminho para dados municipais (CSV ou JSON)
        output_dir: Diretório para salvar resultados

    Returns:
        DataFrame com estatísticas por região

    Raises:
        FileNotFoundError: Se input_path não existir
    """
    logging.info(f"Carregando dados de {input_path}")

    # Carregar dados
    if input_path.endswith('.json'):
        df = pd.read_json(input_path)
    else:
        df = pd.read_csv(input_path)

    # Calcular estatísticas por região
    stats = (df
        .groupby('regiao')
        .agg(
            n=('pib', 'count'),
            pib_medio=('pib', 'mean'),
            pib_sd=('pib', 'std')
        )
        .reset_index()
    )

    # Exportar
    output_path = Path(output_dir) / 'stats_regiao.csv'
    output_path.parent.mkdir(parents=True, exist_ok=True)
    stats.to_csv(output_path, index=False)

    logging.info(f"Estatísticas salvas em {output_path}")

    return stats


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    calculate_regional_stats(
        input_path='data/municipios.csv',
        output_dir='data/stats/'
    )
```

## Referências Importantes

- **Projeto tese:** `C:\OneDrive\github\tese`
- **Pipeline pndr_survey:** `scripts/main.py`
- **Dados processados:** `data/2-papers/2-2-papers.json`
- **Configuração:** `scripts/config.yaml`
- **Documentação pipeline:** `docs/pipeline_extraction.md`

## Limitações

**Esta skill NÃO deve:**
- Converter scripts de estimação econométrica (OLS, FE, RE, GMM, etc.)
- Modificar diretamente arquivos LaTeX em `latex/` (apenas gerar tabelas)
- Alterar dados originais sem backup
- Executar código sem validação prévia do usuário
- Criar dependências externas não listadas em `requirements.txt`

## Mensagens de Erro Comuns

1. **"Script R não encontrado"** → Verificar caminho em `C:\OneDrive\github\tese`
2. **"Dados não disponíveis em pndr_survey"** → Solicitar ao usuário extração prévia
3. **"Conversão não trivial"** → Apresentar alternativas ao usuário
4. **"Output não equivalente"** → Documentar diferenças e solicitar aprovação

---

**Invocação:** `/processar-dados [comando] [argumentos]`

**Comandos disponíveis:**
- `explorar` — Lista scripts R disponíveis no projeto tese
- `converter [script.R]` — Converte script R específico
- `stats` — Gera estatísticas descritivas
- `plot [tipo]` — Gera gráfico específico
- `validar` — Valida datasets processados
