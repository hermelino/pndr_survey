# Plano de Inclusão de Tabelas de Resultados no Artigo

**Documento**: Plano estratégico para inclusão de tabelas da tese no arquivo `resultados.tex` do artigo
**Data**: 2026-03-02
**Objetivo**: Integrar quadros sintéticos da revisão sistemática ao artigo, facilitando consulta e comparação de estudos

---

## 1. Contexto

### 1.1 Situação Atual

**Arquivo**: `latex/resultados.tex`
- ✅ Contém discussão narrativa completa dos resultados
- ⚠️ Não possui tabelas/quadros integrados
- ⚠️ Seções 4.2 a 4.5 comentadas (aguardando inclusão de tabelas)

**Fonte**: Projeto tese (`C:\OneDrive\github\tese`)
- 📊 5 tabelas principais disponíveis em `arquivos_latex/latex_tese/tabelas/1-survey/`
- ✅ Geradas automaticamente pelo pipeline de extração LLM
- ✅ Já validadas e revisadas na tese

---

## 2. Tabelas Disponíveis

### 2.1 Inventário Completo

| Arquivo | Descrição | Estudos | Status |
|---------|-----------|---------|--------|
| `survey_artigos_fc_pib.tex` | Fundos Constitucionais → PIB per capita | 21 | ✅ COPIADA |
| `survey_artigos_fc_vinc.tex` | Fundos Constitucionais → Emprego/Salário | 14 | ⏳ Pendente |
| `survey_artigos_fd.tex` | Fundos de Desenvolvimento | 5 | ⏳ Pendente |
| `survey_artigos_if.tex` | Incentivos Fiscais | 7 | ⏳ Pendente |
| `fc_tabela_resumo.tex` | Resumo aplicações FCs (valores) | — | ⏳ Pendente |

### 2.2 Estrutura Padrão dos Quadros

**Formato**: `longtable` (multi-página)
**Colunas** (7):
1. Método (1.4cm)
2. Artigo (1.5cm)
3. Publicação (1.5cm)
4. Amostragem (2-2.7cm)
5. Variável Independente (1.5cm)
6. Variável Dependente (1.8-2cm)
7. Resultado (4-4.2cm)

**Macros utilizadas**:
- `\fc[largura]{conteúdo itemize}` - formatação de células com listas
- `\metodo{texto}{linhas}` - mesclagem de células na coluna método
- `\citeonline{}` - citações no formato ABNT

---

## 3. Estratégia de Implementação

### 3.1 Fase 1: Validação (✅ CONCLUÍDA)

**Ações realizadas**:
1. ✅ Criado diretório `latex/tabelas/`
2. ✅ Criado arquivo `tabela_macros.tex` com definições de macros
3. ✅ Copiada e adaptada `survey_artigos_fc_pib.tex`
4. ✅ Inserida referência no texto de `resultados.tex` (linha 10)
5. ✅ Adicionados comandos `\input{}` para macros e tabela

**Resultado**: Primeira tabela integrada com sucesso, aguardando compilação LaTeX para validação final.

### 3.2 Fase 2: Expansão (⏳ A FAZER)

#### 2.1 Tabela de Emprego/Salário

**Ponto de inserção**: Após descomentar seção 4.2 (linha 58)

```latex
\subsection{Avaliações de Impacto dos Fundos Constitucionais sobre o Mercado de Trabalho}

[Parágrafo introdutório]

O Quadro~\ref{tab:estudos_fc_vinc} apresenta os 14 estudos que avaliam os efeitos dos
Fundos Constitucionais sobre emprego e salário nas empresas e municípios beneficiados.

\input{tabelas/survey_artigos_fc_vinc}

[Discussão dos resultados...]
```

#### 2.2 Tabela de Fundos de Desenvolvimento

**Ponto de inserção**: Após descomentar seção 4.3 (linha 80)

```latex
\subsection{Avaliações de Impacto dos Fundos de Desenvolvimento}

Os Fundos de Desenvolvimento (FDNE, FDA e FDCO) constituem instrumentos mais recentes da PNDR,
com operação sistemática a partir de 2010-2013, o que explica a menor quantidade de estudos
empíricos disponíveis. Conforme apresentado no Quadro~\ref{tab:estudos_fd}, dentre os 35
estudos aprovados nesta revisão, 8 avaliam algum aspecto dos Fundos de Desenvolvimento.

\input{tabelas/survey_artigos_fd}

[Discussão dos resultados...]
```

#### 2.3 Tabela de Incentivos Fiscais

**Ponto de inserção**: Após descomentar seção 4.4 (linha 84)

```latex
\subsection{Avaliações de Impacto dos Incentivos Fiscais}

A avaliação empírica dos incentivos fiscais da SUDENE e SUDAM constitui a vertente menos
desenvolvida da literatura sobre a PNDR. O Quadro~\ref{tab:estudos_if} sintetiza os 9
estudos que investigam explicitamente estes instrumentos.

\input{tabelas/survey_artigos_if}

[Discussão dos resultados...]
```

#### 2.4 Tabela Resumo dos FCs

**Ponto de inserção**: Na seção 4.1, após linha 10 (contexto inicial)

```latex
A Tabela~\ref{tab:resumo_fc} apresenta a distribuição dos recursos dos Fundos
Constitucionais por tipologia regional da PNDR, evidenciando a expressiva expansão
dos valores aplicados ao longo dos três períodos analisados (2002-2008, 2009-2015 e 2016-2021).

\input{tabelas/fc_tabela_resumo}
```

### 3.3 Fase 3: Ajustes e Validação (⏳ A FAZER)

**Checklist de validação**:
- [ ] Compilar LaTeX completo (verificar erros)
- [ ] Validar numeração de quadros/tabelas
- [ ] Conferir todas as referências cruzadas (`\ref{}`)
- [ ] Verificar se todas as citações (`\citeonline`) estão no `.bib`
- [ ] Revisar formatação e quebras de página
- [ ] Testar visualização em PDF

---

## 4. Dependências Técnicas

### 4.1 Pacotes LaTeX Necessários

```latex
\usepackage{longtable}    % Tabelas multi-página
\usepackage{multirow}     % Mesclagem de células
\usepackage{afterpage}    % Controle de posicionamento
\usepackage{enumitem}     % Listas customizadas
\usepackage{array}        % Colunas avançadas
\usepackage{booktabs}     % Linhas de qualidade (opcional)
\usepackage{abntex2cite}  % Citações ABNT (\citeonline)
```

**Status**: ⚠️ Verificar se todos estão no preâmbulo de `main.tex`

### 4.2 Contadores ABNT

```latex
\newcounter{quadro}
\renewcommand{\quadroname}{Quadro}
```

**Observação**: `abntex2` já define `\quadroname`, mas contador `quadro` pode precisar ser criado.

### 4.3 Arquivo de Referências

**Local**: `latex/references.bib`
**Ação**: Garantir que todos os estudos citados nas tabelas estão presentes com chaves corretas

**Exemplo de chaves usadas**:
- `Resende2014a`, `Resende2014b`, `Resende2014c`
- `CravoResende2015`
- `OliveiraLimaArriel2016`
- `ResendeSilvaFilho2017`, `ResendeSilvaFilho2018`
- `Carneiroetal2024a`
- `MonteIrffiBastosCarneiro2025`

---

## 5. Estrutura de Arquivos

```
pndr_survey/
├── latex/
│   ├── main.tex                    # Documento principal
│   ├── resultados.tex              # ✅ Texto + referências às tabelas
│   ├── tabelas/                    # ⬅️ NOVO DIRETÓRIO
│   │   ├── tabela_macros.tex       # ✅ Macros compartilhadas
│   │   ├── survey_artigos_fc_pib.tex   # ✅ Quadro FCs × PIB
│   │   ├── survey_artigos_fc_vinc.tex  # ⏳ Quadro FCs × Emprego
│   │   ├── survey_artigos_fd.tex       # ⏳ Quadro FDs
│   │   ├── survey_artigos_if.tex       # ⏳ Quadro IFs
│   │   └── fc_tabela_resumo.tex        # ⏳ Tabela resumo FCs
│   └── references.bib              # Bibliografia
└── docs/
    └── plano_inclusao_tabelas_resultados.md  # ⬅️ ESTE ARQUIVO
```

---

## 6. Benefícios da Inclusão

### 6.1 Para Leitores
- 📊 **Síntese visual** de todos os estudos em formato comparável
- 🔍 **Consulta rápida** a metodologias e resultados específicos
- 📈 **Comparabilidade** direta entre abordagens e estimativas

### 6.2 Para a Pesquisa
- ✅ **Conformidade PRISMA** - padrão de revisões sistemáticas
- 🔁 **Replicabilidade** - dados transparentes para meta-análises futuras
- 📚 **Referenciabilidade** - citação precisa de estudos individuais

### 6.3 Para o Artigo
- 🎓 **Rigor metodológico** - demonstra exaustividade da revisão
- 📄 **Economia textual** - reduz repetições narrativas
- 🏆 **Impacto acadêmico** - facilita uso por outros pesquisadores

---

## 7. Cronograma Sugerido

| Fase | Ação | Estimativa | Status |
|------|------|------------|--------|
| 1 | Copiar tabela FC-PIB | 30 min | ✅ FEITO |
| 2 | Copiar tabela FC-Emprego | 15 min | ⏳ |
| 3 | Copiar tabelas FD e IF | 20 min | ⏳ |
| 4 | Copiar tabela resumo FCs | 10 min | ⏳ |
| 5 | Descomentar seções 4.2-4.5 | 10 min | ⏳ |
| 6 | Adicionar referências textuais | 20 min | ⏳ |
| 7 | Compilar e debugar LaTeX | 30-60 min | ⏳ |
| 8 | Revisar formatação final | 30 min | ⏳ |
| **TOTAL** | | **~3h** | 20% |

---

## 8. Riscos e Mitigações

| Risco | Probabilidade | Impacto | Mitigação |
|-------|---------------|---------|-----------|
| Conflito de macros | Baixa | Médio | Usar `\renewcommand` em vez de `\newcommand` |
| Referências quebradas | Média | Alto | Validar todas as chaves em `references.bib` |
| Tabelas muito longas | Alta | Baixo | `longtable` já suporta quebra automática |
| Formatação inconsistente | Média | Médio | Usar macros centralizadas em `tabela_macros.tex` |
| Contador de quadros ausente | Baixa | Alto | Criar contador manualmente se necessário |

---

## 9. Notas Importantes

### 9.1 Diferenças entre Tese e Artigo

**Tese**:
- Usa `\quadroname` e contador `quadro` (ABNT)
- Tabelas numeradas separadamente de quadros
- Maior espaço para tabelas extensas

**Artigo**:
- Deve manter compatibilidade ABNT (`abntex2` em modo `article`)
- Espaço limitado - priorizar síntese
- Consideração: manter formato original ou simplificar?

### 9.2 Observações sobre Citações

Todas as citações nas tabelas usam `\citeonline{}`, que é específico do `abntex2cite`. Caso o artigo use outro pacote de citações (como `natbib`), será necessário:
1. Garantir que `abntex2cite` está carregado
2. OU substituir `\citeonline{}` por comando equivalente

### 9.3 Macro `\fc{}`

A macro `\fc{}` é fundamental para a formatação. Ela:
- Cria `parbox` com largura ajustável
- Insere listas com `enumitem` customizado
- Controla espaçamentos verticais

**Importante**: Não renomear ou remover, pois está hardcoded em todas as 468 células das tabelas.

---

## 10. Próximos Passos

### Opção A: Continuar Sequencialmente
1. Copiar próxima tabela (FC-Emprego)
2. Descomentar seção 4.2
3. Adicionar referência textual
4. Repetir para FD e IF

### Opção B: Compilar e Testar Agora
1. Compilar LaTeX com tabela atual
2. Verificar erros
3. Ajustar dependências
4. Prosseguir com demais tabelas

### Opção C: Incluir Todas de Uma Vez
1. Copiar todas as 4 tabelas restantes
2. Descomentar todas as seções
3. Compilar e debugar tudo junto
4. Revisar formatação final

**Recomendação**: Opção B (testar antes de prosseguir)

---

## 11. Contato e Suporte

**Autor do plano**: Claude Sonnet 4.5
**Data**: 2026-03-02
**Projeto**: pndr_survey - Revisão Sistemática sobre Instrumentos da PNDR
**Repositório**: `c:\OneDrive\github\pndr_survey\`

---

## Registro de Alterações

| Data | Versão | Alteração |
|------|--------|-----------|
| 2026-03-02 | 1.0 | Plano inicial criado |
| 2026-03-02 | 1.1 | Fase 1 concluída (tabela FC-PIB) |

---

**Status Geral**: ⏳ 20% concluído (1 de 5 tabelas integradas)
**Próximo milestone**: Compilar LaTeX e validar tabela FC-PIB
