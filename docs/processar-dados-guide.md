# Guia da Skill processar-dados

## Visão Geral

A skill `/processar-dados` converte scripts de manipulação de dados do projeto **tese** (R) para o contexto **pndr_survey** (Python), incluindo:

- ✅ Limpeza e transformação de dados
- ✅ Merge e join de datasets
- ✅ Criação de variáveis derivadas
- ✅ Estatísticas descritivas
- ✅ Geração de tabelas (LaTeX, Excel, CSV)
- ✅ Geração de gráficos descritivos
- ❌ Estimação de modelos econométricos (excluído)

## Comandos Disponíveis

### 1. Explorar Projeto Tese

Lista todos os scripts R disponíveis para conversão.

```bash
/processar-dados explorar
```

**Saída esperada:**
- Lista de scripts R categorizados por tipo
- Identificação de scripts de manipulação vs. econometria
- Sugestão de prioridades de conversão

---

### 2. Converter Script Específico

Converte um script R para Python equivalente.

```bash
/processar-dados converter fd_variables.R
```

**Workflow:**
1. Lê script R original
2. Identifica inputs/outputs
3. Propõe estrutura Python
4. Solicita aprovação do usuário
5. Implementa conversão
6. Testa com dados reais
7. Documenta mapeamento R→Python

**Exemplo:** Converter `descriptive_stats.R` → `regional_stats.py`

---

### 3. Gerar Estatísticas Descritivas

Calcula estatísticas descritivas para variáveis do dataset.

```bash
/processar-dados stats --vars ano,instrumento,metodo
```

**Saídas:**
- `data/stats/descriptive_stats_YYYYMMDD.xlsx`
- `latex/tabelas/descriptive_stats.tex`

**Estatísticas incluídas:**
- N (observações válidas)
- Média, desvio-padrão
- Mínimo, Q1, mediana, Q3, máximo
- Valores ausentes

---

### 4. Gerar Gráfico

Cria gráfico em estilo acadêmico.

```bash
/processar-dados plot distribuicao-ano
```

**Tipos disponíveis:**
- `distribuicao-ano` — Histograma de estudos por ano
- `distribuicao-instrumento` — Barras por instrumento PNDR
- `timeline` — Série temporal de publicações
- `regional` — Mapa coroplético por região

**Saídas:**
- `figures/nome_grafico.png` (300 DPI)
- `figures/nome_grafico.pdf` (vetorial)

---

### 5. Validar Dados

Executa validações de qualidade nos datasets processados.

```bash
/processar-dados validar
```

**Checagens:**
- Valores ausentes (NaN, None, "")
- Duplicatas (DOIs, IDs)
- Tipos de dados esperados
- Ranges válidos (anos, valores numéricos)
- Consistência entre datasets relacionados

**Saída:**
- Relatório de validação em `data/validation_report_YYYYMMDD.txt`

---

## Exemplos de Uso

### Caso 1: Converter Script de Variáveis do PIB

**Objetivo:** Converter `fd_variables.R` (projeto tese) para Python

```bash
# 1. Explorar projeto tese
/processar-dados explorar

# 2. Converter script específico
/processar-dados converter fd_variables.R

# 3. Validar conversão
/processar-dados validar
```

**Resultado:**
- Script Python criado em `scripts/data_processing/fd_variables.py`
- Documentação de mapeamento em `scripts/data_processing/README_fd_variables.md`
- Testes de equivalência executados

---

### Caso 2: Gerar Tabela de Estatísticas Descritivas

**Objetivo:** Criar tabela LaTeX com estatísticas dos estudos

```bash
/processar-dados stats --vars ano,tipo_estudo,instrumento --format latex
```

**Resultado:**
- Tabela LaTeX em `latex/tabelas/stats_estudos.tex`
- Pronta para `\input{}` no artigo

**Exemplo de saída:**

```latex
\begin{table}[htbp]
\caption{Estatísticas descritivas dos estudos incluídos}
\label{tab:stats_estudos}
\begin{tabular}{lrrrrrrr}
\toprule
Variável & N & Média & DP & Mín & Mediana & Máx & Ausentes \\
\midrule
Ano & 87 & 2014.3 & 5.2 & 2002 & 2015 & 2024 & 0 \\
... \\
\bottomrule
\end{tabular}
\end{table}
```

---

### Caso 3: Criar Gráfico de Distribuição Temporal

**Objetivo:** Visualizar distribuição de estudos por ano

```bash
/processar-dados plot distribuicao-ano
```

**Resultado:**
- `figures/distribuicao_ano.png` (para visualização rápida)
- `figures/distribuicao_ano.pdf` (para inclusão no artigo LaTeX)

**Estilo:**
- Fonte serifada (Times New Roman)
- Resolução 300 DPI
- Cores acessíveis (daltônicos)
- Grade discreta

---

## Padrões de Conversão

### R Tidyverse → Python Pandas

| R (tidyverse) | Python (pandas) |
|---------------|-----------------|
| `df %>% filter(x > 10)` | `df.query('x > 10')` |
| `df %>% select(a, b)` | `df[['a', 'b']]` |
| `df %>% group_by(g) %>% summarise(m = mean(x))` | `df.groupby('g')['x'].mean()` |
| `df %>% mutate(y = x * 2)` | `df.assign(y=lambda d: d.x * 2)` |

### R ggplot2 → Python Matplotlib/Seaborn

```r
# R
ggplot(df, aes(x = ano, y = valor)) +
  geom_line() +
  theme_minimal()
```

```python
# Python
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_style("whitegrid")
plt.plot(df['ano'], df['valor'])
plt.xlabel('Ano')
plt.ylabel('Valor')
plt.tight_layout()
plt.savefig('output.pdf')
```

---

## Estrutura de Arquivos Gerados

```
scripts/
  data_processing/          ← Scripts convertidos de R
    fd_variables.py
    descriptive_stats.py
    README_*.md             ← Documentação de mapeamento
  figures/                  ← Scripts de visualização
    plot_timeline.py

data/
  stats/                    ← Estatísticas descritivas
    descriptive_stats_20260303.xlsx
  validation/               ← Relatórios de validação
    validation_report_20260303.txt

figures/                    ← Gráficos gerados
  distribuicao_ano.png
  distribuicao_ano.pdf

latex/
  tabelas/                  ← Tabelas LaTeX
    stats_estudos.tex
    summary_instruments.tex
```

---

## Checklist de Conversão

Antes de converter um script:

- [ ] Ler script R original completamente
- [ ] Identificar todos os inputs (arquivos, variáveis)
- [ ] Identificar todos os outputs (arquivos, tabelas, gráficos)
- [ ] Verificar se dados equivalentes existem em pndr_survey
- [ ] Propor estrutura Python ao usuário
- [ ] Receber aprovação explícita para proceder

Após converter:

- [ ] Script Python executa sem erros
- [ ] Outputs equivalentes ao R (validados)
- [ ] Type hints em todas as funções
- [ ] Docstrings completos
- [ ] Logging implementado
- [ ] Testes básicos passam
- [ ] Documentação criada (mapeamento R→Python)

---

## Limitações

**Esta skill NÃO converte:**
- Scripts de estimação econométrica (OLS, FE, RE, GMM, etc.)
- Modelos de regressão, painéis, séries temporais
- Testes de hipóteses econométricos
- Análises de causalidade (DID, IV, RDD, etc.)

**Para essas análises, consultar outra skill ou implementar manualmente.**

---

## Troubleshooting

### Problema: "Script R não encontrado"

**Solução:** Verificar caminho correto em `C:\OneDrive\github\tese`

```bash
# Listar scripts disponíveis
/processar-dados explorar
```

---

### Problema: "Dados não disponíveis em pndr_survey"

**Solução:** Executar extração de dados antes da conversão

```bash
# Verificar dados disponíveis
ls data/2-papers/2-2-papers.json
```

---

### Problema: "Conversão não trivial"

**Solução:** Skill apresentará alternativas e solicitará decisão do usuário

**Exemplo:** Script R usa pacote `sf` (spatial data) — requer `geopandas` em Python

---

### Problema: "Output não equivalente ao R"

**Solução:** Documentar diferenças e solicitar aprovação explícita

**Possíveis causas:**
- Diferenças numéricas (precisão float)
- Ordenação diferente (sort)
- Formatação de datas/strings

---

## Dependências Adicionais

Para processamento de dados e visualização:

```bash
pip install pandas matplotlib seaborn scipy scikit-learn geopandas
```

Adicionar em `scripts/requirements.txt`:

```
# Processamento de dados (skill processar-dados)
scipy>=1.10           # Estatísticas avançadas
scikit-learn>=1.3     # Algoritmos de ML (clustering, PCA)
geopandas>=0.14       # Dados espaciais (se necessário)
matplotlib>=3.7       # Gráficos base
seaborn>=0.13         # Gráficos estatísticos
```

---

## Referências

- **Skill definition:** `.claude/commands/5-processar-dados.md`
- **Projeto tese:** `C:\OneDrive\github\tese`
- **Scripts R originais:** `C:\OneDrive\github\tese\bulding_dataset_R\source_code\`
- **Pipeline pndr_survey:** `scripts/main.py`

---

## Suporte

Para reportar problemas ou sugerir melhorias:

1. Abrir issue no repositório
2. Incluir exemplo do script R que não converteu corretamente
3. Anexar logs de erro (se aplicável)
