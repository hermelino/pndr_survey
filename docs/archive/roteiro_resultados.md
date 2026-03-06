# Roteiro: Seção 4 — Discussão dos Resultados

**Fonte na tese:** `c:\OneDrive\github\tese\arquivos_latex\latex_tese\2-textuais\1-survey\1-4-discussao-dos-resultados.tex` (144 linhas)

**Adaptações principais:**
- Atualizar contagem de estudos: 37 → 35 aprovados (34 das bases + 1 inclusão manual)
- Incorporar análise do índice de citação (IC) para contextualizar importância dos estudos
- Adicionar seção de síntese comparativa ao final
- Reescrever introduções de forma mais concisa (formato artigo)
- Atualizar números e referências conforme dados de `2-2-papers.json`

---

## Seção 4: Discussão dos Resultados

[REMOVER] **Subseção 4.1 "Panorama Geral"** — O usuário identificou que esta subseção repete informações que já devem estar cobertas na seção Método (distribuição temporal, distribuição por instrumento, metodologias). A seção "Discussão dos Resultados" deve focar nos achados dos estudos (efeitos estimados, magnitudes, significância), não nas características descritivas da amostra.

[NOTA] A introdução da seção 4 deve ser um parágrafo breve (3-5 linhas) contextualizando que a literatura sobre instrumentos da PNDR é assimétrica (FCs >> FDs > IFs) e que os resultados serão apresentados por instrumento. Não deve incluir tabelas ou contagens detalhadas (já cobertas no Método).

---

### 4.1 Avaliações de Impacto dos Fundos Constitucionais sobre o PIB

> **Descrição:** Sintetiza os resultados de 33 estudos que avaliam o efeito dos FCs sobre o PIB per capita municipal. Organiza os achados por abordagem metodológica: (i) modelos de efeitos fixos, (ii) modelos de painel espacial, (iii) modelos não lineares (threshold, quantílico), (iv) modelos de eficiência (DEA, fronteira estocástica), (v) modelos dinâmicos (GMM), (vi) modelos de equilíbrio geral, e (vii) modelos quase experimentais (RDD, DiD, DID escalonado). Cada subsubseção apresenta os principais estudos, magnitudes de efeito estimadas, significância e limitações metodológicas apontadas pelos autores.

> **Fonte na tese:** Linhas 7-88

> **Adaptações necessárias:**
> - Atualizar número de estudos que avaliam FCs: verificar contagem exata em `2-2-papers.json`
> - Incluir referências aos novos estudos identificados (2024-2026)
> - Adicionar parágrafo final de síntese comparativa destacando heterogeneidade de resultados conforme especificação metodológica
> - Manter estrutura de subsubseções (clara e didática)

[NOTA] A tese cita 33 estudos sobre FCs. No artigo, verificar contagem atualizada no JSON (`s1.instrumentos_pndr` contém FNE/FNO/FCO).

#### 4.1.1 Modelos de Efeitos Fixos (EF)

> **Descrição:** Apresenta estudos que usam painel com efeitos fixos municipais e temporais, principalmente da família Resende (2014a, 2014b) e Resende, Cravo & Pires (2014). Discute magnitudes estimadas (0,021 a 0,076), diferenças entre FNE, FNO e FCO, ausência de robustez em algumas especificações e limitações relacionadas à identificação causal.

> **Fonte na tese:** Linhas 20-30

> **Adaptações necessárias:**
> - Concisão: reduzir detalhes excessivos sobre cada estudo, manter apenas resultados principais
> - Manter números e coeficientes relevantes
> - Destacar limitações metodológicas (endogeneidade, seleção)

#### 4.1.2 Modelos de Painel Espacial

> **Descrição:** Revisa estudos que incorporam interdependência espacial (SDM, SAR, SAC) para captar transbordamentos (spillovers) e vazamentos de recursos entre municípios vizinhos. Apresenta evidências de efeitos diretos (0,03 a 0,14 p.p.) e indiretos (0,1 a 0,4 p.p.), heterogeneidade por tipologia PNDR e divergências sobre magnitude dos efeitos conforme tipo de matriz espacial e período.

> **Fonte na tese:** Linhas 32-56

> **Adaptações necessárias:**
> - Incluir estudo de Gondim (2025) se aprovado
> - Verificar se há novos estudos com modelos espaciais em 2024-2026
> - Manter síntese sobre relevância da dimensão espacial e necessidade de robustez

#### 4.1.3 Modelos Não Lineares e de Eficiência

> **Descrição:** Aborda estudos que investigam heterogeneidades no efeito dos FCs conforme nível inicial de renda (modelos threshold), distribuição de crescimento (regressão quantílica) e eficiência no uso dos recursos (DEA, fronteira estocástica). Destaca que efeitos são mais pronunciados em municípios de renda intermediária, inconclusivos em municípios de baixa renda e decrescentes em municípios de alta renda.

> **Fonte na tese:** Linhas 58-66

> **Adaptações necessárias:**
> - Unificar subsubseções "Modelos Não Lineares" e "Modelos de Eficiência" em uma única subsubseção para concisão
> - Manter achados principais: efeito threshold (Linhares et al., 2014), regressão quantílica (Irffi et al., 2016) e eficiência (Carneiro, 2018)

#### 4.1.4 Modelos Dinâmicos

> **Descrição:** Revisa estudos que usam painel dinâmico (GMM) para corrigir viés de endogeneidade em variável dependente defasada e variáveis explicativas. Destaca magnitude elevada do efeito estimado (2,96 p.p. em Cambota & Viana, 2019) e potencial sobreestimação decorrente de proliferação de instrumentos.

> **Fonte na tese:** Linhas 68-70

> **Adaptações necessárias:**
> - Manter conciso (1-2 parágrafos)
> - Destacar importância do controle de endogeneidade e limitações do método GMM

#### 4.1.5 Modelos de Equilíbrio Geral

> **Descrição:** Sintetiza resultados de simulações CGE (Computable General Equilibrium) que avaliam efeitos contrafactuais de retirada dos FCs. Apresenta evidências de que FCs têm papel relevante no crescimento de longo prazo via acumulação de capital e redução de concentração regional.

> **Fonte na tese:** Linhas 72-76

> **Adaptações necessárias:**
> - Manter conciso
> - Destacar diferenças entre efeitos de curto vs. longo prazo

#### 4.1.6 Modelos Quase Experimentais

> **Descrição:** Revisa estudos que empregam estratégias de identificação mais robustas: primeira diferença, diferenças-em-diferenças (DiD), DiD em dois estágios, DiD escalonado, e regressão descontínua geográfica (RDD). Contrasta resultados divergentes: ausência de efeito (Oliveira & Silveira Neto, 2020) vs. efeito positivo significativo (Carneiro et al., 2024). Discute heterogeneidades por gênero, tipo de tomador e magnitude do tratamento.

> **Fonte na tese:** Linhas 78-86

> **Adaptações necessárias:**
> - Incluir novos estudos de 2024-2026 com métodos quase experimentais
> - Destacar avanços metodológicos e persistência de divergências nos resultados
> - Mencionar estudo de Monte, Irffi, Bastos & Carneiro (2025) sobre heterogeneidades

[NOTA] Síntese final da subseção 4.1 (PIB): Adicionar parágrafo destacando heterogeneidade de resultados conforme método, condicionada a características locais (renda, tipologia PNDR), e a necessidade de maior comparabilidade entre especificações. Esta síntese não deve repetir a conclusão geral da seção 4, mas focar nos achados específicos sobre PIB.

---

### 4.2 Avaliações de Impacto dos Fundos Constitucionais sobre o Mercado de Trabalho

> **Descrição:** Sintetiza resultados de estudos que avaliam efeito dos FCs sobre emprego formal, massa salarial e salário médio. Apresenta evidências mais convergentes do que para o PIB: efeito positivo consistente do FNE sobre emprego nas empresas beneficiadas (7,96 a 132,23 p.p. ao longo de 5 anos), efeito crescente ao longo dos primeiros anos pós-tratamento, maior efeito em micro e pequenas empresas e na modalidade de crédito para investimento, mas ausência de efeito significativo sobre salário médio (sugerindo que novos postos são criados ao nível salarial vigente).

> **Fonte na tese:** Linhas 90-120

> **Adaptações necessárias:**
> - Atualizar contagem de estudos conforme JSON
> - Incluir novos estudos de 2024-2026
> - Manter estrutura cronológica de apresentação dos estudos (Silva et al., 2009 → Soares & Sousa Neto, 2009 → ... → Daniel & Braga, 2020 → Oliveira & Silveira Neto, 2021)
> - Destacar maior convergência de resultados em relação ao PIB

[TABELA] Tabela 4.1: Resumo dos Estudos sobre FCs e Mercado de Trabalho
- Fonte: `tabelas/1-survey/survey_artigos_fc_vinc.tex` (tese) + `2-2-papers.json` (artigo)
- Descrição: Autor, ano, método, variável dependente, efeito estimado, significância
- Adaptação: Atualizar com estudos de 2024-2026; verificar se há novos estudos sobre emprego

[NOTA] A tese destaca que salário médio não apresenta variação significativa na maioria das especificações. Este achado deve ser mantido e discutido à luz da hipótese de que novos empregos são criados sem ganhos de produtividade.

---

### 4.3 Avaliações de Impacto dos Fundos de Desenvolvimento

> **Descrição:** Apresenta as primeiras evidências empíricas sobre efeito dos FDs (FDNE, FDA, FDCO) no PIB local. Revisa três estudos recentes (Braz, Bastos & Irffi, 2024; Carneiro, Costa & Irffi, 2024; Irffi et al., 2025) que usam DiD escalonado e encontram efeito positivo de 21-24% no PIB per capita municipal. Destaca que esta é a vertente mais recente da literatura e que há carência de avaliações sobre outros resultados (emprego, renda, desigualdade).

> **Fonte na tese:** Linhas 122-130

> **Adaptações necessárias:**
> - Verificar se há novos estudos de 2024-2026 sobre FDs
> - Destacar que FDs são instrumentos mais recentes (operação sistemática a partir de 2010-2013)
> - Mencionar escassez de estudos em relação aos FCs

[TABELA] Tabela 4.2: Resumo dos Estudos sobre Fundos de Desenvolvimento
- Fonte: `tabelas/1-survey/survey_artigos_fd.tex` (tese) + `2-2-papers.json` (artigo)
- Descrição: Autor, ano, instrumento (FDNE/FDA/FDCO), método, variável dependente, efeito estimado
- Adaptação: Atualizar com estudos de 2024-2026

---

### 4.4 Avaliações de Impacto dos Incentivos Fiscais

> **Descrição:** Sintetiza os 7 estudos que avaliam incentivos fiscais da SUDENE e SUDAM. Destaca que esta é a vertente menos desenvolvida da literatura sobre a PNDR, refletindo operação mais recente (concessões sistemáticas a partir de 2010) e dificuldades de acesso a dados. Apresenta evidências esparsas e inconclusivas: efeito positivo sobre emprego no turismo (Garsous et al., 2017) e vínculos totais (Braz & Irffi, 2023), mas ausência de significância para PIB per capita em modelos que incluem múltiplos instrumentos simultaneamente (Carneiro, Costa & Irffi, 2024).

> **Fonte na tese:** Linhas 132-142

> **Adaptações necessárias:**
> - Atualizar contagem de estudos conforme JSON
> - Verificar se há novos estudos de 2024-2026 sobre IFs
> - Destacar ausência completa de avaliações dos incentivos fiscais da SUDAM
> - Enfatizar que ampliação desta literatura é prioridade para a agenda de pesquisa

[TABELA] Tabela 4.3: Resumo dos Estudos sobre Incentivos Fiscais
- Fonte: `tabelas/1-survey/survey_artigos_if.tex` (tese) + `2-2-papers.json` (artigo)
- Descrição: Autor, ano, instrumento (IF Sudene/Sudam), método, variável dependente, efeito estimado
- Adaptação: Atualizar com estudos de 2024-2026

---

### 4.5 Síntese Comparativa dos Resultados

> **Descrição:** [NOVO] Subseção que integra os achados das subseções anteriores e oferece uma visão sintética da literatura. Compara: (i) volume de evidências por instrumento (FCs >> FDs > IFs), (ii) convergência/divergência de resultados por variável de resultado (emprego > PIB), (iii) heterogeneidade de efeitos conforme características locais (renda, tipologia PNDR, setor econômico), (iv) robustez metodológica (métodos quase experimentais vs. modelos observacionais), e (v) lacunas e prioridades para pesquisa futura. Esta subseção deve conectar os achados à pergunta de pesquisa e aos objetivos do artigo.

> **Fonte na tese:** Linhas 143-144 (parágrafo final, expandido)

> **Adaptações necessárias:**
> - [NOVO] Esta subseção não existe na tese; deve ser criada para o artigo
> - Integrar achados de todas as subseções anteriores
> - Destacar assimetria expressiva entre instrumentos
> - Enfatizar necessidade de avaliações que integrem simultaneamente os três instrumentos
> - Mencionar contribuições metodológicas do artigo (5 bases, LLM, IC) para mapear a literatura de forma mais abrangente

[NOTA] A síntese comparativa deve ser concisa (2-3 parágrafos), evitando repetição de detalhes já apresentados. Foco em padrões gerais, não em estudos individuais.

[NOVO] Incluir discussão sobre o papel do índice de citação na identificação de estudos não-publicados com relevância para a literatura (10 TDs/apresentações incluídos com IC > 0.10).

---

## Elementos Adicionais

[REMOVER] **Figura de rede de citações** — Esta figura seria mais adequada para a seção Método (descrição dos estudos), não para Discussão dos Resultados (achados dos estudos).
- Fonte: `data/3-ref-bib/citation_index_results.json`
- Descrição: Grafo direcionado mostrando citações entre os 35 estudos, com tamanho dos nós proporcional ao IC
- Adaptação: [NOVO] Figura não existe na tese; deve ser gerada via script (Python + networkx + matplotlib)

[REMOVER] **Figura de distribuição temporal** — Esta figura seria mais adequada para a seção Método (descrição dos estudos), não para Discussão dos Resultados (achados dos estudos).

[REMOVER] Tabelas excessivamente detalhadas da tese (ex: `tabela_empreendimentos_removidos.tex`, `tabela_fd_setores.tex`) devem ser excluídas ou movidas para apêndice, se necessário.

---

## Checklist de Verificação Pré-Redação

- [x] Arquivo da tese lido (`1-4-discussao-dos-resultados.tex`)
- [x] Pipeline extraction lido (`docs/pipeline_extraction.md`)
- [x] JSON enriquecido lido (`data/2-papers/2-2-papers.json`, primeiras 100 linhas)
- [x] Relatório IC lido (`data/3-ref-bib/citation_index_report.txt`)
- [ ] Contagem exata de estudos por instrumento extraída do JSON (deve ser feito durante redação)
- [ ] Tabelas derivadas verificadas no diretório `latex/tabelas/1-survey/` da tese
- [ ] Questionários LLM consultados (`scripts/questionnaires/`) para descrever metodologia de classificação (se necessário)

---

## Observações Finais

- Total de subseções: 5 (4.1 a 4.5)
- Total de subsubseções: 6 (4.1.1 a 4.1.6)
- Tabelas previstas: 3 (resumo FC-trabalho, resumo FD, resumo IF)
- Figuras previstas: 0 (figuras descritivas dos estudos devem estar na seção Método)
- Elementos novos: Subseção 4.5 (síntese comparativa dos resultados)

**Próximos passos:**
1. Usuário revisa e aprova o roteiro
2. Redação sequencial de cada subseção (uma por vez)
3. Apresentação ao usuário em blocos de código LaTeX
4. Aprovação antes de inserir em `main.tex`
