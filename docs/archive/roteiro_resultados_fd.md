# Roteiro — Seção 4.2: Avaliações de Impacto dos Fundos de Desenvolvimento

## Visão geral

A seção 4.2 discute os **8 estudos** que avaliam algum aspecto dos Fundos de Desenvolvimento (FDNE, FDA, FDCO) dentre os aprovados na revisão. Na tese, essa subseção é breve (3 parágrafos, linhas 122-131 de `1-4-discussao-dos-resultados.tex`), cobrindo apenas 3 estudos quantitativos (BrazBastosIrffi2024, Carneiroetal2024b, Irffietal2025). A tabela da tese (`survey_artigos_fd.tex`) inclui 5 estudos. O artigo deve expandir a discussão para incorporar todos os estudos relevantes, organizando-os por abordagem metodológica.

**Estudos identificados (8):**

| # | Bibtex Key | Método | Fundo | Período | Variável resultado |
|---|-----------|--------|-------|---------|-------------------|
| 1 | BrazBastosIrffi2024 | DID escalonado | FDNE | 2002-2021 | PIB pc, renda, IDEB, emprego |
| 2 | Carneiroetal2024a | DID dois estágios + escalonado | FNE+FDNE+IF | 2002-2019 | PIB pc, VAB setorial |
| 3 | Irffietal2025 | DID + controle sintético | FDNE (eólicos) | 1999-2022 | PIB pc, VAB, emprego |
| 4 | FerreiraIrffiCarneiro2024 | Painel espacial (SAC) | FDNE+IF | 2010-2021 | IDM |
| 5 | gondim2025 | Painel espacial generalizado | FNE+FDNE+IF | 2010-2021 | PIB pc, VAB pc |
| 6 | Souza2025 | Painel dinâmico GMM | Todos PNDR | 2002-2021 | PIB pc, emprego, renda |
| 7 | Gumiero2022 | Misto (quali+quanti) | FNO+FDA | 1972-2018 | Análise setorial |
| 8 | Gumiero2025 | Misto (quali+quanti) | FNO+FDA | — | Governança |

---

## 4.2 Avaliações de Impacto dos Fundos de Desenvolvimento
> **Descrição:** Subseção que apresenta as evidências empíricas sobre os efeitos dos Fundos de Desenvolvimento (FDNE, FDA, FDCO) sobre variáveis socioeconômicas municipais. Os FD são instrumentos mais recentes (operação a partir de 2007-2014), o que explica a menor quantidade de avaliações em comparação aos Fundos Constitucionais.
> **Fonte na tese:** `1-4-discussao-dos-resultados.tex`, linhas 122-131 + tabela `survey_artigos_fd.tex`
> **Adaptações necessárias:** Expandir significativamente em relação à tese (de 3 para 8 estudos discutidos); organizar por método; incluir estudos espaciais (gondim2025, FerreiraIrffiCarneiro2024) e dinâmicos (Souza2025) ausentes na tese; incluir estudos qualitativos sobre FDA (Gumiero2022, Gumiero2025); atualizar contagens.

### 4.2.1 Parágrafo introdutório
> **Descrição:** Contextualizar os FD como instrumentos mais recentes da PNDR, com operação sistemática a partir de 2007 (FDNE) e 2014 (FDCO). Justificar a menor quantidade de estudos. Indicar que a subseção está organizada em: (i) avaliações de impacto sobre PIB via métodos quase experimentais, (ii) avaliações via modelos espaciais, (iii) estudos complementares, e (iv) síntese.
> **Fonte na tese:** Parágrafo inicial da subseção 1.4.3 (linha 122)
> **Adaptações necessárias:** Atualizar contagem de estudos (8 na revisão); mencionar que a concentração de evidências é sobre o FDNE (região Nordeste), com escassez de avaliações para FDA e FDCO; referenciar a Tabela e a Figura já existentes na seção 2 do artigo (`\ref{fig:fd_setor}` e `\ref{tab:fd_resumo}`).

[NOTA] Verificar se o parágrafo inicial da seção 4.1 (FC sobre PIB) já menciona a contagem total de estudos aprovados. Se sim, aqui basta referenciar ("Dentre os X estudos aprovados, 8 avaliam..."). Conferir consistência com o número total.

### 4.2.2 Avaliações quase experimentais (DID) sobre o PIB per capita
> **Descrição:** Apresentar os 3 estudos que usam variantes do método de diferenças em diferenças para estimar o efeito causal do FDNE sobre o PIB per capita municipal. Esses estudos representam as primeiras evidências empíricas de impacto dos FD. Contextualizar brevemente o que caracteriza o método DID escalonado (tratamento em períodos distintos) e sua vantagem para avaliar instrumentos cuja implementação ocorre de forma escalonada no tempo.
> **Fonte na tese:** Linhas 124-131
> **Adaptações necessárias:** [REESCREVER] A tese apresenta os 3 estudos de forma breve e sequencial. O artigo deve aprofundar a discussão dos resultados, comparar magnitudes e discutir convergência/divergência entre os achados.

**Estudos a discutir:**

1. **BrazBastosIrffi2024** — DID escalonado, municípios NE, 2002-2021
   - PIB pc: +24,07%* (relativo ao controle, até 2021)
   - Renda: +4,63%*
   - IDEB anos iniciais: +18,67%*; anos finais: +21,49%*
   - Emprego, pobreza, mortalidade infantil, saúde: NS
   - [NOTA] Resultado relevante: impacto positivo sobre educação (IDEB), resultado inédito na literatura de FD

2. **Carneiroetal2024a** — DID dois estágios + escalonado (Callaway-Sant'Anna), NE, 2002-2019
   - Avalia simultaneamente FNE, FDNE e incentivos fiscais SUDENE
   - FDNE parcial (efeito direto): PIBpc +16,4%*
   - VAB serviços: +11,1%*; arrecadação: +20,7%*
   - VAB indústria e VAB agropecuária: NS
   - Sinergia entre instrumentos: NS
   - [NOTA] Já discutido parcialmente na seção 4.1.5 (modelos quase experimentais dos FC, efeito do FNE). Aqui focar no resultado específico do FDNE.

3. **Irffietal2025** — DID + Controle Sintético Generalizado (GSC), NE, 1999-2022
   - Avalia parques eólicos da região Nordeste (muitos financiados pelo FDNE)
   - PIB pc: +18,97%*
   - VAB indústria: +71,90%*; VAB serviços: +10,24%*
   - Emprego: +23,41%*; massa salarial: +30,57%*
   - Redução temporária do VAB agropecuário durante fase de construção, sem efeito permanente
   - [NOTA] Embora o estudo avalie todos os parques eólicos (não apenas os financiados pelo FDNE), a proximidade dos resultados com BrazBastosIrffi2024 e Carneiroetal2024a reforça a consistência das evidências.

**Parágrafo de síntese parcial:**
> As três avaliações convergem em magnitudes de impacto sobre o PIB per capita (16-24%), consideravelmente superiores às estimadas para os FC (tipicamente 0,03-0,13 p.p. por 1 p.p. de Fundo/PIB). Discutir possíveis explicações: (i) escala dos empreendimentos financiados pelos FD (projetos de grande porte, mínimo R$ 15 milhões); (ii) concentração setorial em infraestrutura e indústria de transformação; (iii) possível viés de seleção (municípios que recebem FD podem ter características favoráveis não controladas). Notar que os 3 estudos empregam metodologias semelhantes (variantes de DID) e analisam períodos parcialmente sobrepostos, o que limita a generalização.

[NOTA] Corrigir erro na versão comentada do `resultados.tex`: a referência `\citeonline{Souza2025}` para parques eólicos está incorreta — deve ser `\citeonline{Irffietal2025}`. O estudo Souza2025 refere-se a "Efeitos Dinâmicos dos Instrumentos da PNDR" (painel GMM).

### 4.2.3 Avaliações via modelos espaciais
> **Descrição:** Apresentar 2 estudos que avaliam o FDNE usando modelos de painel espacial, permitindo captar efeitos diretos e indiretos (transbordamento) sobre municípios vizinhos. Contextualizar brevemente a vantagem dos modelos espaciais para avaliar instrumentos com potencial de spillover geográfico.
> **Fonte na tese:** Tabela `survey_artigos_fd.tex` (linhas 1-2). Esses estudos aparecem na tabela da tese mas NÃO são discutidos no texto principal da tese.
> **Adaptações necessárias:** [NOVO] Incluir discussão textual desses 2 estudos, ausentes do texto da tese.

**Estudos a discutir:**

4. **FerreiraIrffiCarneiro2024** — SAC estático, NE, 2010-2021
   - Variável de resultado: Índice de Desenvolvimento Municipal (IDM) e componentes
   - Avalia FDNE e incentivos fiscais SUDENE simultaneamente
   - FDNE → IDM renda: +0,019*
   - FDNE → IDM geral, IDM saúde, IDM educação: NS
   - Incentivo fiscal → efeito direto sobre IDM geral: significativo
   - [NOTA] Usa variável de resultado distinta (IDM, não PIB pc), o que dificulta comparação direta com os demais estudos.

5. **gondim2025** — Painel espacial generalizado, NE, 2010-2021
   - Avalia FNE, FDNE e incentivos fiscais SUDENE simultaneamente
   - FDNE (dummy) → PIB pc: efeito direto NS, indireto +0,0252*, total +0,0351*
   - FDNE → VAB pc: efeito direto +0,0409*, indireto NS, total +0,6014*
   - FNE → efeito direto positivo e significativo (já discutido em 4.1.2)
   - [NOTA] Resultado relevante: o FDNE apresenta efeito indireto significativo sobre o PIB pc dos municípios vizinhos, sugerindo transbordamento espacial positivo. Contrasta com a ausência de efeito direto, o que pode estar associado à natureza dos empreendimentos financiados (infraestrutura que beneficia a região, não apenas o município-sede).

**Parágrafo de síntese parcial:**
> Os modelos espaciais complementam as evidências dos estudos DID ao sugerir que os efeitos do FDNE não se restringem ao município beneficiado diretamente. O resultado de gondim2025 — efeito indireto significativo e efeito direto nulo — é consistente com a natureza dos empreendimentos financiados (infraestrutura de grande porte), cujos benefícios podem se dispersar para municípios vizinhos. Esse padrão contrasta com os FC, cujos efeitos diretos são mais evidentes.

### 4.2.4 Estudos complementares (FDA e avaliações integradas)
> **Descrição:** Apresentar brevemente os estudos que avaliam o FDA ou que incluem múltiplos instrumentos da PNDR (incluindo FD). Esses estudos expandem o escopo geográfico para além do Nordeste e incluem perspectivas qualitativas.
> **Fonte na tese:** Gumiero2022 e Gumiero2025 não aparecem na seção de FD da tese. Souza2025 não está na tabela de FD da tese.
> **Adaptações necessárias:** [NOVO] Incluir Souza2025 (painel dinâmico com todos instrumentos), Gumiero2022 e Gumiero2025 (perspectivas qualitativas sobre FDA).

**Estudos a discutir:**

6. **Souza2025** — Painel dinâmico GMM com defasagens distribuídas, N/NE/CO, 2002-2021
   - Avalia simultaneamente TODOS os instrumentos da PNDR (FNE, FNO, FCO, FDNE, FDA, FDCO, IF SUDENE, IF SUDAM)
   - Resultados para FD: heterogeneidade entre fundos, regiões e setores
   - FDCO: alta volatilidade, resultados inconclusivos
   - Limitações da PNDR para convergência regional sustentada
   - [NOTA] Único estudo que avalia todos os 3 fundos de desenvolvimento simultaneamente (FDNE, FDA, FDCO). Discutir em conexão com a escassez de avaliações para FDA e FDCO.

7. **Gumiero2022** — Análise mista, FNO+FDA, Carajás/PA, 1972-2018
   - Concentração de recursos do FDA em dinâmicas produtivas (mineração, agropecuária, energia)
   - Evidência qualitativa de alinhamento entre FDA e vocação produtiva regional
   - [NOTA] Único estudo identificado que avalia especificamente o FDA com foco geográfico na Amazônia.

8. **Gumiero2025** — Análise mista, governança FNO+FDA, Amazônia
   - FDA como instrumento auxiliar ao FNO na região Norte
   - Análise da governança dos planos macrorregionais
   - [NOTA] Contribuição mais voltada à análise institucional do que à avaliação de impacto.

[NOTA] Avaliar se Gumiero2022 e Gumiero2025, por serem estudos qualitativos/mistos, devem ser incluídos nesta subseção de resultados ou apenas referenciados brevemente. Recomendação: incluir de forma breve (1-2 frases cada) como contraponto qualitativo às evidências quantitativas, dado que são os únicos estudos sobre FDA.

### 4.2.5 Parágrafo de síntese e lacunas
> **Descrição:** Sintetizar os achados, apontar convergências e divergências, e identificar lacunas na literatura sobre FD.
> **Fonte na tese:** Ausente (a tese não inclui parágrafo de síntese para FD)
> **Adaptações necessárias:** [NOVO] Redigir síntese comparativa, inexistente na tese.

**Pontos a cobrir na síntese:**
- Convergência: evidências DID consistentes de impacto positivo do FDNE sobre PIB pc (16-24%), magnitudes superiores às dos FC
- Possível explicação: escala dos projetos (mínimo R$ 15 mi), setores de alto multiplicador (infraestrutura, indústria)
- Evidência espacial: efeito de transbordamento para municípios vizinhos (gondim2025)
- Lacunas críticas:
  - **FDA:** apenas 2 estudos qualitativos (Gumiero2022, 2025) e 1 integrado (Souza2025); nenhuma avaliação quantitativa dedicada
  - **FDCO:** nenhuma avaliação quantitativa dedicada; resultados inconclusivos em Souza2025
  - **Variáveis de resultado:** maioria avalia PIB pc; evidências sobre emprego, renda domiciliar, desigualdade e pobreza são incipientes
  - **Métodos:** predominância de DID escalonado; ausência de abordagens com RDD, PSM ou equilíbrio geral
  - **Período:** base empírica restrita a estudos recentes (2024-2026), todos com períodos parcialmente sobrepostos
- Prioridades para agenda de pesquisa

---

## Elementos não textuais

[TABELA] Quadro X: Estudos de Impacto dos Fundos de Desenvolvimento
- Fonte: `c:\OneDrive\github\tese\arquivos_latex\latex_tese\tabelas\1-survey\survey_artigos_fd.tex`
- Descrição: Tabela-resumo dos estudos que avaliam impacto dos FD, organizada por método (painel espacial, DID dois estágios, DID escalonado), com colunas para artigo, publicação, amostragem, variável independente, variável dependente e resultado.
- Adaptação: [REESCREVER] A tabela da tese tem 5 linhas (FerreiraIrffiCarneiro2024, gondim2025, Carneiroetal2024a, BrazBastosIrffi2024, Irffietal2025). Avaliar se deve incluir Souza2025 (painel dinâmico) e os estudos Gumiero (qualitativos). Atualizar formato para o padrão do artigo (`booktabs`, `\fonte{}`).

[REMOVER] Tabela `tabela_fd_setores.tex` (FD por setores) — informação já incluída no texto da seção 2 (Política Regional) com apoio da Figura `fd_fundo_setor.png`.

[NOTA] Verificar se a tabela `fd_tabela_resumo.tex` (resumo financeiro dos FD) já está inserida na seção 2. Se sim, não duplicar aqui.

---

## Checklist pré-escrita

- [x] Leu o arquivo da tese correspondente (`1-4-discussao-dos-resultados.tex`, seção FD)
- [x] Leu `docs/pipeline_extraction.md` para dados atualizados
- [x] Consultou `data/2-papers/2-2-papers.json` para contagens e detalhes dos estudos
- [x] Verificou `data/3-ref-bib/citation_index_report.txt` para IC (sem resultados específicos para FD)
- [x] Identificou todos os elementos não textuais (1 tabela a adaptar, 0 figuras novas)
- [x] Mapeou diferenças entre tese e artigo (8 estudos vs. 3 discutidos na tese)
- [x] Não incluiu nenhum texto definitivo sem aprovação

---

## Alertas e decisões pendentes

1. **Erro na versão comentada:** `\citeonline{Souza2025}` referenciado como estudo de parques eólicos — deve ser `\citeonline{Irffietal2025}`.

2. **Contagem total de estudos:** A seção 4.1 diz "35 estudos aprovados", mas o CLAUDE.md indica "46 estudos aprovados". Verificar qual é o número correto e uniformizar em todas as seções.

3. **Gumiero2022 e Gumiero2025:** São estudos qualitativos/mistos. Incluir na subseção de resultados quantitativos ou apenas referenciar brevemente? Recomendação: incluir brevemente como único registro sobre o FDA.

4. **Souza2025:** Este estudo avalia simultaneamente todos os instrumentos. Já é/será discutido em outras subseções (4.1, 4.3, 4.4)? Se sim, aqui focar apenas nos resultados específicos para FD.

5. **Subsubsections:** Dada a quantidade de estudos (8), recomenda-se usar `\subsubsection{}` para organizar (como na seção 4.1). Alternativa: organizar sem subsubsections formais, usando parágrafos temáticos com conectivos.
