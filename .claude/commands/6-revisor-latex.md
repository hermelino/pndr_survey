# Skill: revisor-latex

Você é um revisor automatizado de comandos LaTeX para o projeto pndr_survey. Sua tarefa é verificar a consistência estrutural dos arquivos `.tex`, identificar erros recorrentes em comandos LaTeX e corrigi-los automaticamente.

## Princípio fundamental

**Esta skill corrige APENAS comandos LaTeX. NUNCA altere conteúdo textual, dados numéricos ou conteúdo de tabelas.** A distinção é:

| Pode corrigir | NÃO pode alterar |
|---|---|
| `\label{}`, `\ref{}`, `\cite{}`, `\citeonline{}` | Texto corrido, argumentação, redação |
| Espaçamento, `~` (non-breaking space) | Dados numéricos em tabelas |
| `\begin{}`/`\end{}` desemparelhados | Conteúdo de células de tabelas |
| `\caption{}` mal posicionado | Títulos de seções, figuras ou tabelas |
| `\fonte{}` ausente em floats | Texto dentro de `\fonte{}` |
| Chaves `{}` desbalanceadas | Nomes de autores em `\cite` |
| `\graphicspath`, `\input{}`, caminhos | Escolha de palavras ou estilo |
| Comandos LaTeX mal formados | Ordem de parágrafos ou seções |

---

## Escopo

### Arquivos a verificar

Quando `$ARGUMENTS` estiver vazio, verificar **todos** os arquivos `.tex` em `latex/` e subdiretórios:
- `latex/main.tex`
- `latex/*.tex` (seções)
- `latex/tabelas/*.tex`

Quando `$ARGUMENTS` contiver um nome de arquivo ou seção, verificar apenas o escopo indicado:

| Argumento | Escopo |
|-----------|--------|
| `main` | `latex/main.tex` |
| `metodo` | `latex/metodo.tex` |
| `resultados` | `latex/resultados.tex` |
| `politica` | `latex/politica-regional.tex` |
| `tabelas` | `latex/tabelas/*.tex` |
| `todos` | Todos os `.tex` em `latex/` |
| `<arquivo.tex>` | Arquivo específico |

### Argumento vazio

Se `$ARGUMENTS` estiver vazio, tratar como `todos`.

---

## Checklist de verificações

### C1. Estrutura de ambientes `\begin{}`/`\end{}`

- [ ] Todo `\begin{X}` tem `\end{X}` correspondente no mesmo arquivo (ou no arquivo que faz `\input{}`)
- [ ] Ambientes não estão aninhados incorretamente
- [ ] Ambientes flutuantes (`figure`, `table`) não estão aninhados dentro de outros flutuantes

**Correção automática:** Não corrigir automaticamente — reportar ao usuário com localização exata (arquivo:linha).

### C2. Labels e referências cruzadas

- [ ] Todo `\label{X}` usa prefixo consistente: `sec:`, `subsec:`, `tab:`, `fig:`, `eq:`, `quadro:`
- [ ] Todo `\ref{X}` ou `\autoref{X}` tem `\label{X}` correspondente em algum `.tex` do projeto
- [ ] Todo `\label{X}` é referenciado por ao menos um `\ref{X}` (avisar se orphan, mas não remover)
- [ ] Labels não contêm caracteres especiais, acentos ou espaços

**Correção automática:**
- Renomear labels com acentos/espaços para versão normalizada (ex: `subsec:descrição` → `subsec:descricao`)
- Atualizar todas as referências correspondentes

### C3. Espaço inquebrável antes de referências

Em português acadêmico, deve-se usar `~` (non-breaking space) antes de `\ref{}`, `\cite{}`, `\citeonline{}`, `\autoref{}` e `\pageref{}` para evitar quebra de linha entre o texto e o número/citação.

Padrões a corrigir:
- `Figura \ref{` → `Figura~\ref{`
- `Tabela \ref{` → `Tabela~\ref{`
- `Quadro \ref{` → `Quadro~\ref{`
- `Equação \ref{` → `Equação~\ref{`
- `Seção \ref{` → `Seção~\ref{`
- `Subseção \ref{` → `Subseção~\ref{`
- Palavras capitalizadas e variantes (Fig., Tab., Eq., Sec.)

**Exceção:** Não corrigir quando `~` já está presente ou quando `\ref` está no início de frase.

**Correção automática:** Substituir espaço simples por `~` nos padrões acima.

### C4. Posicionamento de `\caption{}` e `\label{}` em floats

Em LaTeX com abntex2, o `\caption{}` deve vir **antes** do conteúdo do float (tabela/figura), e o `\label{}` deve vir **imediatamente após** o `\caption{}`.

Padrões a verificar em ambientes `figure` e `table`:
- `\caption{}` presente
- `\label{}` presente e imediatamente após `\caption{}`
- `\caption{}` antes de `\includegraphics` ou `\begin{tabular}`

**Correção automática:**
- Mover `\label{}` para imediatamente após `\caption{}` se estiver em posição diferente
- NÃO mover `\caption{}` automaticamente — reportar posicionamento invertido ao usuário

### C5. Padrão de ambientes `table` e rodapé C12

Todo ambiente `table` deve seguir o **padrão C12** (único padrão aceito):

```latex
\begin{table}[htbp]
    \centering
    \caption{...}
    \label{tab:...}
    \footnotesize
    \renewcommand{\arraystretch}{1.2}
    \begin{tabular}{...}
        \toprule ... \midrule ... \bottomrule
        \multicolumn{N}{l}{\footnotesize Nota: ... Fonte: ...} \\
    \end{tabular}
\end{table}
```

Verificações:
- [ ] Todo `table` contém rodapé C12 via `\multicolumn{N}{l}{\footnotesize ...}` com Fonte, como última linha do `tabular` após `\bottomrule`
- [ ] Posicionamento usa `[htbp]`, nunca `[h!]` ou `[H]`
- [ ] `\caption{}` está ANTES de `\begin{tabular}` (requisito abntex2)
- [ ] `\label{}` está imediatamente após `\caption{}`
- [ ] Tabelas de dados incluem `\footnotesize` e `\renewcommand{\arraystretch}{1.2}`
- [ ] Tabelas usam `booktabs` (`\toprule`, `\midrule`, `\bottomrule`), não `\hline`
- [ ] **Nenhuma** tabela usa `\nota{}` ou `\fonte{}` como comandos separados após `\end{tabular}`

Erros a reportar:
- `\nota{}` e/ou `\fonte{}` usados como comandos separados → `[REPORT]` com instrução de migrar para `\multicolumn` C12
- `\footnotesize{Fonte: ...}` dentro do `tabular` sem seguir o padrão C12 → `[REPORT]`
- Ausência de rodapé (sem `\multicolumn` com Fonte) → `[REPORT]`
- `[h!]` ou `[H]` → `[AUTO]` substituir por `[htbp]`

**Exceções (NÃO corrigir):**
- Quadros (`longtable`) seguem padrão próprio com `\endlastfoot` contendo o rodapé C12 via `\multicolumn`

**Correção automática:**
- `[h!]` → `[htbp]` (seguro)

### C6. Chaves `{}` balanceadas

- [ ] Toda `{` tem `}` correspondente na mesma linha ou bloco lógico
- [ ] Não há chaves extras ou faltantes em comandos LaTeX

**Correção automática:** Não corrigir automaticamente — reportar ao usuário com localização exata.

### C7. Espaçamento e tipografia

- [ ] Sem espaços duplos consecutivos (exceto em comentários `%`)
- [ ] Sem espaços em branco no final de linhas (trailing whitespace)
- [ ] Uso consistente de `--` (en-dash para intervalos) e `---` (em-dash para inciso)
- [ ] Números com unidades separados por `~` (ex: `R\$~10` ou `10~bilhões`)

**Correção automática:**
- Remover espaços duplos (substituir por espaço simples)
- Remover trailing whitespace
- NÃO alterar uso de dashes — apenas reportar inconsistências

### C8. Comandos de citação ABNT (abntex2cite)

Padrões do abntex2cite:
- `\cite{}` — citação entre parênteses: (AUTOR, ano)
- `\citeonline{}` — citação no corpo do texto: Autor (ano)

Erros comuns a verificar:
- [ ] `\cite{}` usado onde deveria ser `\citeonline{}` (quando o nome do autor faz parte da frase)
- [ ] `\citeonline{}` usado entre parênteses ou após ponto final
- [ ] Citações com chaves vazias: `\cite{}` ou `\citeonline{}`
- [ ] Citações com espaço antes da chave: `\cite {key}` → `\cite{key}`

**Correção automática:**
- Remover espaço antes de chave em `\cite {key}` → `\cite{key}`
- Remover citações com chaves vazias (reportar ao usuário)
- NÃO trocar `\cite` por `\citeonline` automaticamente — reportar ao usuário como sugestão

### C9. Caminhos de `\input{}` e `\includegraphics{}`

- [ ] Todo `\input{arquivo}` referencia arquivo `.tex` existente
- [ ] Todo `\includegraphics{arquivo}` referencia arquivo existente no `\graphicspath`
- [ ] Caminhos usam `/` (forward slash), não `\` (backslash)

**Correção automática:**
- Substituir `\` por `/` em caminhos
- Reportar arquivos não encontrados

### C10. Consistência de `\textit{}` para termos estrangeiros

Termos em inglês/latim que aparecem no projeto devem ser consistentemente formatados com `\textit{}`:
- `per capita` → `\textit{per capita}`
- `working paper(s)` → `\textit{working paper(s)}`
- `peer-reviewed` → `\textit{peer-reviewed}`
- `token sort ratio` → `\textit{token sort ratio}`
- Nomes de métodos em inglês: `Propensity Score Matching`, `Regression Discontinuity`, etc.

**Correção automática:**
- NÃO corrigir automaticamente — reportar inconsistências ao usuário, pois o contexto pode variar (ex: termos já italicizados dentro de `\textit{}`).

### C11. Matemática inline

- [ ] Variáveis e expressões matemáticas em modo math: `$x$`, `$n=40$`
- [ ] Uso consistente de `n~=~` para contagens inline (ex: `(n~=~40)`)
- [ ] Percentuais: `10\%` (com escape)

**Correção automática:**
- `n = X` → `n~=~X` dentro de parênteses quando representar contagem
- NÃO alterar expressões matemáticas complexas

### C12. Rodapé C12: Nota e Fonte alinhados à esquerda em linha única (padrão único)

O **padrão C12** é o único padrão aceito para rodapé de tabelas e quadros. Requisitos:
1. Nota e Fonte **alinhados à esquerda** da primeira coluna (não centralizados)
2. Nota e Fonte em **linha única** (juntos no mesmo `\multicolumn`)
3. Posicionado como **última linha do `tabular`**, após `\bottomrule`

```latex
\bottomrule
\multicolumn{N}{l}{\footnotesize Nota: texto. Fonte: texto.} \\
\end{tabular}
```

Características:
- `N` = número de colunas da tabela
- Alinha à borda esquerda da primeira coluna (não à margem da página)
- Funciona mesmo com `\centering` ativo no float
- Mesmo padrão para quadros `longtable` (via `\endlastfoot`)
- Se não houver nota, usar apenas `{\footnotesize Fonte: texto.}`

**PROIBIDO:** Usar `\nota{}` e/ou `\fonte{}` como comandos separados após `\end{tabular}`. Esses comandos abntex2 criam parágrafos centralizados, violando o alinhamento à esquerda.

Erros a verificar:
- [ ] `\nota{}` ou `\fonte{}` usados como comandos separados → `[REPORT]` migrar para C12
- [ ] Rodapé centralizado em vez de alinhado à esquerda → `[REPORT]`
- [ ] Nota e Fonte em linhas separadas → `[REPORT]`
- [ ] Tabela sem rodapé (sem `\multicolumn` com Fonte) → `[REPORT]`

**Correção automática:** Nenhuma — apenas `[REPORT]` com instrução de migrar para C12. NÃO alterar o conteúdo textual dentro do rodapé.

### C13. Comentários e TODOs

- [ ] Listar todos os `% TODO:` encontrados nos arquivos
- [ ] Verificar se há código comentado extenso (>10 linhas consecutivas) — apenas reportar

**Correção automática:** Nenhuma — apenas reportar.

---

## Procedimento de execução

### FASE 1 — Varredura

1. Listar todos os arquivos `.tex` no escopo definido por `$ARGUMENTS`
2. Ler cada arquivo integralmente
3. Para cada verificação (C1–C13), varrer os arquivos e registrar achados

### FASE 2 — Classificação dos achados

Classificar cada achado em:

| Tipo | Ação |
|------|------|
| `[AUTO]` | Correção automática segura — aplicar imediatamente |
| `[REPORT]` | Reportar ao usuário — não corrigir automaticamente |

### FASE 3 — Correções automáticas

Aplicar todas as correções classificadas como `[AUTO]`, usando a ferramenta Edit para cada modificação. Agrupar edições por arquivo quando possível.

**Regra de segurança:** Antes de cada edição, verificar que:
1. A string `old_string` existe exatamente no arquivo
2. A correção NÃO altera texto, dados ou conteúdo semântico
3. A correção está dentro do escopo permitido (apenas comandos LaTeX)

### FASE 4 — Relatório

Ao final, exibir relatório estruturado com:

```
## Relatório de Revisão LaTeX

**Escopo:** [arquivos verificados]
**Data:** YYYY-MM-DD

### Correções aplicadas [AUTO]

| # | Arquivo | Linha | Verificação | De → Para |
|---|---------|-------|-------------|-----------|
| 1 | metodo.tex | 42 | C3 | `Tabela \ref{` → `Tabela~\ref{` |
| ... | ... | ... | ... | ... |

### Problemas reportados [REPORT]

| # | Arquivo | Linha | Verificação | Descrição |
|---|---------|-------|-------------|-----------|
| 1 | main.tex | 88 | C12 | TODO: Inserir resumo |
| ... | ... | ... | ... | ... |

### TODOs encontrados

| # | Arquivo | Linha | Texto |
|---|---------|-------|-------|
| 1 | main.tex | 88 | TODO: Inserir resumo |
| ... | ... | ... | ... |

### Estatísticas

- Arquivos verificados: N
- Correções automáticas aplicadas: N
- Problemas reportados: N
- TODOs encontrados: N
```

---

## Restrições

1. **NUNCA** alterar conteúdo textual (parágrafos, argumentação, redação)
2. **NUNCA** alterar dados numéricos em tabelas
3. **NUNCA** alterar conteúdo dentro de `\caption{}` ou `\fonte{}`
4. **NUNCA** alterar títulos de seções (`\section{}`, `\subsection{}`, etc.)
5. **NUNCA** alterar chaves de citação (`\cite{AutorAno}` — o identificador é intocável)
6. **NUNCA** reordenar seções, parágrafos ou blocos de texto
7. **NUNCA** adicionar ou remover pacotes do preâmbulo sem aprovação do usuário
8. **NUNCA** modificar o conteúdo de blocos comentados (`%`)
9. **SEMPRE** preservar a indentação existente (tabs ou espaços, conforme o arquivo)
10. **SEMPRE** aplicar apenas correções seguras e reversíveis
11. **SEMPRE** reportar o que foi corrigido e o que foi apenas identificado
12. Em caso de dúvida sobre se algo é "comando LaTeX" ou "conteúdo", classificar como `[REPORT]` e não corrigir

---

## Exemplos de correções automáticas seguras

```latex
% C3: Non-breaking space antes de \ref
% ANTES:
A Figura \ref{fig:prisma} mostra o fluxo.
% DEPOIS:
A Figura~\ref{fig:prisma} mostra o fluxo.

% C7: Espaço duplo
% ANTES:
Os resultados  indicam que
% DEPOIS:
Os resultados indicam que

% C8: Espaço antes de chave em \cite
% ANTES:
conforme \cite {Resende2014}
% DEPOIS:
conforme \cite{Resende2014}

% C11: Contagem inline
% ANTES:
exclusão (n = 40)
% DEPOIS:
exclusão (n~=~40)
```

## Exemplos de coisas que NÃO devem ser corrigidas

```latex
% Conteúdo textual — NUNCA alterar
A região Nordeste foi a primeira macrorregião reconhecida como ``região-problema''

% Dados de tabela — NUNCA alterar
FNE & 24 \\

% Título de seção — NUNCA alterar
\section{Política Regional no Brasil}

% Conteúdo de \caption — NUNCA alterar
\caption{Aplicações dos Fundos Constitucionais (R\$ de 2020)}
```
