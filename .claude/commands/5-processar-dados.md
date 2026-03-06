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

**Período dos dados:** Todos os datasets serão atualizados até o ano **2023** (ampliação do período 2002-2021 da tese para 2002-2023).

**Regras de dados externos:**
1. **Sempre copiar para o projeto:** Dados de origens externas devem ser copiados para `data/external_data/` antes de serem usados. Scripts nunca referenciam paths externos diretamente.
2. **Dados indisponíveis → pendentes:** Se algum arquivo não estiver disponível, marcar como `# TODO: pendente` no código e prosseguir com os dados existentes.
3. **Documentar fontes:** Toda fonte de dados deve estar registrada em `docs/fontes_dados_pndr.md` com URL oficial, período e status.

## Dados Externos Disponíveis

### Fundos Constitucionais (FC)
Origem: `C:/OneDrive/DATABASES/FUNDOS CONSTITUCIONAIS/`
Destino: `data/external_data/fc/`

| Arquivo | Sheet | Período |
|---------|-------|---------|
| `FCO - Contratações 2000 a 2018.xlsx` | "FCO" | 2000-2018 |
| `FNE - Contratações 2000 a 2018.xlsx` | "FNE" | 2000-2018 |
| `FNO - Contratações 2000 a 2018.xlsx` | "FNO" | 2000-2018 |
| `Consolidado Dez_2019 - FCF.xlsx` | "Consolidado 2019" | 2019 |
| `Consolidado Dez_2020 - FCF.xlsx` | "Consolidado 2020" | 2020 |
| `Consolidado Dez_2021 - FCF.xlsx` | "Dezembro" | 2021 |
| Consolidados 2022-2023 (a obter) | — | 2022-2023 |

**Script R de referência:** `tese/bulding_dataset_R/source_code/fc_variables.R`

### Fundos de Desenvolvimento (FD)
Localização: `data/external_data/`

| Arquivo | Instrumento | Formato |
|---------|-------------|---------|
| `fdne_liberacoes_ate_jun_2023.xlsx` | FDNE | Excel |
| `fda_liberacoes_ate_2025.pdf` | FDA | PDF (requer extração) |
| `fds_contratacoes.xlsx` | FDS | Excel |

**Script R de referência:** `tese/bulding_dataset_R/source_code/fd_variables.R`

### Incentivos Fiscais (IF)
Localização: `data/external_data/`

| Arquivo | Instrumento | Formato |
|---------|-------------|---------|
| `if_sudam/Merged.xlsx` | SUDAM (consolidado) | Excel |
| `if_sudam/*.pdf` (14 PDFs: 2010-2020 + 2021-2023) | SUDAM (anuais) | PDF |
| `if_sudene.json` | SUDENE | JSON |

**Script R de referência:** `tese/bulding_dataset_R/source_code/if_variables.R`

### Dados Auxiliares
Destino: `data/external_data/`

| Arquivo | Descrição | Status |
|---------|-----------|--------|
| `populacao_municipios.csv` | População municipal (IBGE) | Disponível |
| `populacao_fc.rds` | População municipal (formato RDS, para scripts R) | Disponível |
| `br_ibge_ipca.anual_2002_2020.csv` | Deflator IPCA anual | Disponível |
| `tipologia_2007.xlsx` | Tipologia PNDR 2007 (Decreto nº 6.047/2007) | Disponível |
| `cod_municipios_IBGE.csv` | Códigos e nomes dos municípios | Disponível |
| `classif_incent_fiscais.xlsx` | Classificação ICF por superintendência, tipologia e setor | Disponível |
| `painel_icf.rds` | Painel de incentivos fiscais (formato RDS, para scripts R) | Disponível |
| `resumo_fd.xlsx` | Resumo FD por tipologia, instrumento e setor (20 obs) | Disponível |
| `painel_fd_agregado.rds` | Painel de fundos de desenvolvimento agregado (formato RDS) | Disponível |

**Fontes e URLs:** Ver `docs/fontes_dados_pndr.md`

### Scripts Python de Processamento (a criar)

| Script | Entrada | Saída | Referência R |
|--------|---------|-------|-------------|
| `scripts/process_sudam_pdfs.py` | PDFs SUDAM anuais | `if_sudam/sudam_incentivos_consolidado.xlsx` | — |
| `scripts/process_if_data.py` | SUDENE JSON + SUDAM Excel | `painel_icf.parquet`, `classif_incent_fiscais.xlsx` | `if_variables.R` |
| `scripts/process_fd_data.py` | FDNE Excel + FDA PDF | `resumo_fd.xlsx`, `painel_fd_agregado.parquet` | `fd_variables.R` |
| `scripts/process_fc_data.py` | FC Excel (6 arquivos) | `painel_fc.parquet`, `fc_tabela_resumo.tex` | `fc_variables.R` |
| `scripts/generate_policy_figures.py` | Dados locais em `data/external_data/` | Figuras PNG (matplotlib) | `grafico_resumo_*.R` (referência apenas) |
| `scripts/generate_policy_tables.py` | Painéis processados | Tabelas LaTeX | `descritive_estats_tipologia.R` |

**Figuras geradas por `generate_policy_figures.py`** (todas com dados locais, sem dependência do projeto tese):

| Figura | Dados de entrada (em `data/external_data/`) | Saída |
|--------|----------------------------------------------|-------|
| FD — Fundos de Desenvolvimento | `resumo_fd.xlsx` (sheets: `por_fundo_setor_tipologia`, `medias_pib_tipologia`) | `figures/fd_fundo_setor.png` |
| IF — Incentivos Fiscais | `classif_incent_fiscais.xlsx` | `figures/icf_superint_setor.png` |
| FC — Fundos Constitucionais | `resumo_fc.xlsx` (sheets: `por_fundo_setor_tipologia`, `medias_pc_tipologia`) | `figures/fc_setor_tipologia.png` |

**Execução:** `python scripts/generate_policy_figures.py` (todas) ou `--only fd`, `--only if`, `--only fc`.

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
- Formato compatível com `abntex2` (booktabs)
- Rodapé: seguir **padrão C12** definido em `/revisor-latex` (verificações C5 e C12). Resumo: `\multicolumn{N}{l}{\footnotesize Fonte: texto.} \\` após `\bottomrule`. Nunca usar `\nota{}` + `\fonte{}` separados

**Para Excel:**
- Usar openpyxl para formatação
- Salvar em `data/` com timestamp

**Migração de tabelas existentes:** Ao encontrar tabelas `.tex` fora do padrão C12, seguir as instruções de migração em `/revisor-latex` (verificação C12). Reportar ao usuário antes de aplicar.

**Template:** Ver função `generate_latex_table()` em `.claude/commands/_templates_python.md`.

### 4. Geração de Gráficos

**Estilo Acadêmico:**
- Fonte: Times New Roman ou similar serifada
- Tamanho: 10-12pt para labels
- Paleta: cores distintas para daltônicos
- Formatos: PNG (300 DPI) + PDF (vetorial)

**Template:** Ver função `plot_time_series()` e configuração `plt.rcParams` em `.claude/commands/_templates_python.md`.

### 5. Estatísticas Descritivas

**Template:** Ver `DescriptiveStats` e `generate_descriptive_table()` em `.claude/commands/_templates_python.md`.

### 6. Validação de Dados

**Checagens Obrigatórias:**
- Valores ausentes (NaN, None, "")
- Duplicatas (IDs, DOIs)
- Tipos de dados esperados
- Ranges válidos (anos, valores numéricos)
- Consistência entre datasets relacionados

**Template:** Ver `validate_dataset()` em `.claude/commands/_templates_python.md`.

### 7. Rigor Estatístico na Construção de Variáveis

**Atenção especial** ao converter variáveis e indicadores do projeto tese:

- **Nível de agregação:** Verificar se médias, per capita e outras estatísticas são calculadas no nível correto (ex: município-ano vs transação individual). Médias no nível errado produzem valores enviesados.
- **Ponderação:** Confirmar se médias ponderadas usam os pesos corretos (ex: população, área, PIB).
- **Deflação:** Verificar ano-base do deflator e consistência temporal.
- **Denominadores:** Garantir que divisões (per capita, taxas) usam o denominador do período correto.

**Erros no projeto tese:** Se durante a conversão R → Python for identificado um erro metodológico ou estatístico no script R original do projeto tese, **reportar imediatamente ao usuário** antes de replicar o erro. Documentar o erro encontrado, explicar o impacto nos resultados, e implementar a versão correta no pndr_survey.

**Exemplo real:** `fc_variables.R:127-152` calculava per capita no nível de transação (~1,17M linhas) em vez de município-ano (~55K linhas), enviesando os valores pela quantidade de operações por município. Corrigido em `process_fc_data.py`. Nota: a tabela FC (`fc_tabela_resumo.tex`) agora usa participação média no PIB anual (%) em vez de per capita.

### 8. Integração com Pipeline pndr_survey

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

### 9. Documentação

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
