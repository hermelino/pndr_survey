# Roteiro — Seção 4.3: Avaliações de Impacto dos Incentivos Fiscais

## Visão geral

A seção 4.3 discute os estudos aprovados que avaliam explicitamente os incentivos fiscais (IF) da SUDENE/SUDAM ou incentivos fiscais estaduais (Prodepe). Na tese, essa subseção é breve (3 parágrafos, linhas 132-142 de `1-4-discussao-dos-resultados.tex`), cobrindo apenas 5 estudos no texto e 7 na tabela (`survey_artigos_if.tex`). O artigo deve expandir para incorporar 2 novos estudos (Prodepe), referenciar 2 estudos multi-instrumento já discutidos em outras subseções (Gondim2025, Souza2025), e corrigir erros de chaves BibTeX presentes na versão comentada.

**Contagem confirmada:** 35 estudos aprovados no total (`2-2-papers.json`), dos quais 9 avaliam IF-SUDENE, 1 avalia IF-SUDAM e 1 avalia Prodepe (com sobreposições). Total aprovado consistente com seções 4.1 e 4.2.

**Deduplicação resolvida:** `CostaCarneiroIrffi2023` (ANPEC 2023, DID dois estágios, vínculos +9,82%) NÃO está na base de estudos aprovados. É estudo distinto de `Costa2024` (Applied Economics Letters, Controle Sintético, +19,6%), que É o estudo aprovado. `CarneiroCostaIrffi2024b` (Cadernos de Finanças Públicas) e `CarneiroUmaNotaSobre` (RBE 2025) também NÃO estão na base. Portanto, o bloco 4.3.2 discute **3 estudos** (não 4), e a tabela da tese precisa ser ajustada.

**Decisões confirmadas pelo usuário:**
- Incluir Prodepe: **SIM** (os mesmos estudos também avaliam IF-SUDENE em PE)
- Usar `\subsubsection{}`: **NÃO** (parágrafos temáticos sem divisão formal)
- Contagem: usar **35** (valor confirmado em `2-2-papers.json`)

**Estudos identificados (9 primários + 2 multi-instrumento referenciados):**

| # | BibTeX Key | Método | Instrumento | Período | Variável resultado | Seção |
|---|-----------|--------|-------------|---------|-------------------|-------|
| 1 | Garsous2017 | DID | IF-SUDENE (turismo) | 1998-2009 | Emprego turismo | 4.3.2 |
| 2 | Braz2023 | DID escalonado (C&S) | IF-SUDENE | 2002-2021 | Emprego, renda | 4.3.2 |
| ~~3~~ | ~~CarneiroCostaIrffi2024b~~ | ~~DID dois estágios~~ | ~~IF-SUDENE~~ | ~~2011-2019~~ | ~~Vínculos, salário~~ | ~~removido~~ |
| 4 | Costa2024 | Controle Sintético Gen. | IF-SUDENE | 2006-2019 | Emprego (vínculos) | 4.3.2 |
| 5 | Carneiro2023a | DEA + SFA | IF-SUDENE | 2011-2019 | Massa salarial (efic.) | 4.3.3 |
| 6 | Carneiro2024 | DID dois estágios + C&S | FNE+FDNE+IF | 2002-2019 | PIB pc, VAB | 4.3.4 |
| 7 | FerreiraIrffiCarneiro2024 | Painel espacial (SAC) | FDNE+IF | 2010-2021 | IDM | 4.3.4 |
| 8 | Oliveira2020a | DID | Prodepe+IF+FNE+FDNE | 2000-2017 | Emprego, salário | 4.3.5 |
| 9 | Alves2024 | DID escalonado (C&S) | Prodepe+IF+FNE+FDNE | 2000-2017 | Emprego, salário, massa | 4.3.5 |
| — | *Gondim2025* | *Painel espacial (GNR)* | *FNE+FDNE+IF* | *2003-2019* | *PIB pc, VAB pc* | *4.3.4 (ref.)* |
| — | *Souza2025* | *Painel dinâmico GMM* | *Todos PNDR* | *2002-2021* | *PIB pc, emprego, renda* | *4.3.4 (ref.)* |

*Itálicos: estudos discutidos em detalhe nas seções 4.1/4.2; aqui apenas referenciar resultados específicos de IF.*

---

## 4.3 Avaliações de Impacto dos Incentivos Fiscais

### 4.3.1 Parágrafo introdutório
> **Descrição:** Contextualizar os incentivos fiscais como a vertente menos desenvolvida da literatura sobre a PNDR. Justificar a escassez de evidências: concessões sistemáticas a partir de 2010, dificuldades de acesso a dados de renúncia fiscal em nível de empresa, operação mais recente em relação aos FC. Sem `\subsubsection{}` — usar parágrafos temáticos com conectivos.
> **Fonte na tese:** Parágrafo inicial da subseção (linhas 132-133)
> **Adaptações necessárias:** Contagem: "Dentre os 35 estudos aprovados nesta revisão, 9 avaliam explicitamente os incentivos fiscais". Mencionar que todos os estudos dedicados avaliam incentivos da SUDENE — não há avaliação dedicada de incentivos da SUDAM. Incluir menção aos 2 estudos que também avaliam incentivos fiscais estaduais (Prodepe) em interação com IF-SUDENE.

---

### 4.3.2 Efeitos sobre o mercado de trabalho (emprego e renda)
> **Descrição:** Apresentar os 3 estudos aprovados que avaliam diretamente o efeito dos incentivos fiscais da SUDENE sobre variáveis do mercado de trabalho (emprego, vínculos, renda). Essa é a vertente com maior volume de evidências dentro da literatura de IF. Contextualizar brevemente: "Diferentemente dos Fundos Constitucionais, cujo mecanismo de transmissão opera via crédito subsidiado às empresas, os incentivos fiscais atuam pela redução de 75% do Imposto de Renda de Pessoa Jurídica (IRPJ), diminuindo o custo tributário de operação em municípios da área da SUDENE."
> **Fonte na tese:** Linhas 134-137 (Garsous, Braz)
> **Adaptações necessárias:** [REESCREVER] A tese apresenta esses estudos de forma excessivamente breve. Expandir com detalhes metodológicos, magnitude dos efeitos, variáveis de controle e limitações. Incluir Costa2024 (Controle Sintético), ausente do texto da tese mas presente na tabela. Remover CostaCarneiroIrffi2023 (não aprovado na revisão; o estudo aprovado do mesmo grupo é Costa2024, com método distinto).

**Estudos a discutir:**

1. **Garsous2017** — DID com matching, BA/RJ/ES/MG, 1998-2009
   - Primeiro estudo a avaliar impacto de IF-SUDENE
   - Foco setorial: setor turístico (incentivos específicos a partir de 2002)
   - Emprego turismo: +30% (efeito acumulado 2002-2009)
   - Robusto a deslocamento e destruição de emprego em municípios vizinhos
   - Publicado: *World Development* (maior impacto acadêmico entre estudos de IF)
   - [NOTA] IC = 0,1000 (citado por Costa2024)

2. **Braz2023** — DID escalonado (Callaway & Sant'Anna, 2021), municípios SUDENE, 2002-2021
   - Avalia efeito agregado (todos os setores) sobre emprego e renda
   - Emprego: +3,2%*; renda nominal: +1,2%*
   - Resultado relevante: efeito crescente ao longo do tempo e duradouro ao longo de todo o período de recebimento do incentivo
   - Preocupação: efeitos concentrados em municípios grandes e já desenvolvidos, contrário ao objetivo redistributivo da PNDR
   - [NOTA] IC = 0,2857 (mais citado entre estudos de IF; citado por Gondim2025, Costa2024 e outros)

3. **Costa2024** — Controle Sintético Generalizado, NE, 2006-2019
   - Método mais robusto para identificação causal (constrói contrafactual sintético)
   - Dados microeconômicos (nível de empresa beneficiada)
   - Emprego geral: +19,6%*; manufatura: +18,3%* (intensivo em mão de obra)
   - Efeitos positivos por até 5 anos; demais setores NS
   - Publicado: *Applied Economics Letters*
   - [NOTA] Diferença metodológica importante: enquanto os estudos DID comparam municípios tratados vs. controle, o controle sintético constrói um contrafactual ponderado. A magnitude substancialmente maior que Braz2023 (+19,6% vs. +3,2%) pode refletir o nível de agregação (empresa vs. município) e o setor analisado (manufatura intensiva em mão de obra).

~~**REMOVIDO:** CostaCarneiroIrffi2023 / CarneiroCostaIrffi2024b — NÃO aprovado na revisão. O estudo usa DID dois estágios (vínculos +9,82%), método distinto de Costa2024 (Controle Sintético). Estava na tabela da tese mas não na base de estudos aprovados do pndr_survey. A tabela deve ser atualizada para removê-lo.~~

**Parágrafo de síntese parcial:**
> Os 3 estudos convergem em apontar efeitos positivos dos IF-SUDENE sobre o emprego formal, porém com magnitudes bastante distintas conforme o setor analisado, o método empregado e o nível de agregação dos dados. Os efeitos mais expressivos são observados em setores específicos — turismo (Garsous2017: +30%) e manufatura (Costa2024: +19,6%) — enquanto o efeito agregado sobre todos os setores é mais modesto (Braz2023: +3,2%). Destacar preocupação de Braz2023 sobre concentração dos efeitos em municípios mais desenvolvidos, o que contrasta com o objetivo redistributivo da PNDR.

---

### 4.3.3 Análise de eficiência das empresas beneficiadas
> **Descrição:** Apresentar o estudo de eficiência produtiva das empresas beneficiadas por IF-SUDENE, que adota abordagem distinta das avaliações de impacto (DEA e SFA em vez de métodos quase experimentais). Contextualizar: "Além da mensuração do impacto causal dos incentivos, a avaliação da eficiência com que as empresas beneficiadas utilizam os recursos constitui dimensão complementar relevante para o desenho da política."
> **Fonte na tese:** Referenciado apenas na tabela (survey_artigos_if.tex, linha 101-108), sem discussão textual detalhada.
> **Adaptações necessárias:** [NOVO] Incluir discussão textual, ausente na tese.

**Estudo a discutir:**

5. **Carneiro2023a** — DEA (não paramétrico) + SFA (paramétrico), NE+MG, 2011-2019
   - Variável: eficiência na geração de massa salarial a partir de vínculos e investimento
   - Achados principais:
     - Predominância de empresas intensivas em mão de obra entre as beneficiadas
     - Presença relevante de empresas eficientes no Semiárido
     - Ineficiência atribuída mais ao setor de atividade do que às empresas individualmente
     - Retornos decrescentes de escala na função de produção estimada
   - Implicação: possibilidade de priorizar setores com maior eficiência média e estabelecer metas progressivas de eficiência como contrapartida
   - [NOTA] Este estudo contribui com perspectiva distinta: em vez de medir o impacto do incentivo, avalia se as empresas beneficiadas são eficientes no uso dos recursos. Resultado complementar aos achados da subseção anterior.

---

### 4.3.4 Efeitos sobre PIB e indicadores de desenvolvimento
> **Descrição:** Apresentar resultados de IF sobre PIB per capita e outros indicadores de desenvolvimento (IDM), extraídos principalmente de estudos multi-instrumento que avaliam IF conjuntamente com FNE e FDNE. Esses estudos já foram discutidos em detalhe nas seções 4.1 (FC) e 4.2 (FD), portanto aqui o foco deve ser exclusivamente nos resultados específicos de IF, evitando redundância.
> **Fonte na tese:** Linhas 137-138 (Carneiro2024a sobre PIB) e linhas 139-141 (FerreiraIrffiCarneiro2024 sobre IDM)
> **Adaptações necessárias:** [REESCREVER] A tese confunde as chaves BibTeX (ver Alertas). Incluir Gondim2025 e Souza2025 como referências cruzadas à seção 4.2. Organizar por variável de resultado (PIB pc vs. IDM).

**Estudos a discutir:**

6. **Carneiro2024** — DID dois estágios + Callaway-Sant'Anna, NE+MG+ES, 2002-2019
   - Avalia simultaneamente FNE, FDNE e IF-SUDENE
   - **Resultado IF:** Sem efeitos significativos sobre PIB pc e VAB setorial
   - Contraste com efeitos positivos do FNE (seção 4.1.5) e FDNE (seção 4.2.2)
   - [NOTA] Já discutido em 4.1.5 (efeito FNE) e 4.2.2 (efeito FDNE). Aqui referenciar: "Quanto aos incentivos fiscais, \citeonline{Carneiro2024} não encontram significância estatística..."

7. **FerreiraIrffiCarneiro2024** — Painel espacial SAC estático, NE, 2010-2021
   - Avalia FDNE e IF-SUDENE simultaneamente
   - **Resultado IF (efeito direto):** IDM geral: +0,020*; IDM saúde: +0,024*; IDM renda: +0,012*; IDM educação: NS
   - **Resultado IF (efeito indireto/espacial):** IDM renda: +0,002* (transbordamento)
   - Autocorrelação espacial positiva na distribuição de IF
   - [NOTA] Já discutido em 4.2.3 (efeito FDNE). Aqui focar no resultado IF: "No âmbito dos indicadores de desenvolvimento, \citeonline{FerreiraIrffiCarneiro2024} obtêm efeito direto significativo dos IF sobre o IDM..."

8. **Gondim2025** (referência cruzada à seção 4.2.3)
   - **Resultado IF:** Efeito direto significativo sobre o crescimento do VAB agropecuário per capita
   - [NOTA] Breve menção (1-2 frases): "Complementarmente, \citeonline{Gondim2025} identificam efeito direto dos IF-SUDENE sobre o crescimento do valor adicionado agropecuário."

9. **Souza2025** (referência cruzada à seção 4.2.4)
   - **Resultado IF:** Avalia IF-SUDENE e IF-SUDAM (único estudo com IF-SUDAM)
   - Resultados variados por região e defasagem temporal
   - [NOTA] Breve menção (1-2 frases): destacar que é o único estudo que inclui IF-SUDAM.

**Parágrafo de síntese parcial:**
> As evidências sobre o efeito dos IF no PIB per capita são mais escassas e inconclusivas do que as relativas ao mercado de trabalho. Enquanto Carneiro2024 não encontra efeitos significativos em especificação DID, FerreiraIrffiCarneiro2024 e Gondim2025 identificam efeitos positivos em modelos espaciais sobre indicadores alternativos (IDM e VAB agropecuário). Essa divergência pode refletir diferenças na variável de resultado, no período amostral e na especificação econométrica. Destacar ausência de avaliações dedicadas exclusivamente ao efeito dos IF sobre o PIB (em todos os estudos, IF aparece como uma entre múltiplas variáveis de interesse).

---

### 4.3.5 Incentivos fiscais estaduais (Prodepe) [NOVO]
> **Descrição:** Apresentar os 2 estudos que avaliam o Programa de Desenvolvimento do Estado de Pernambuco (Prodepe), programa estadual de incentivos fiscais que opera em complementaridade com os instrumentos federais (FNE, FDNE, IF-SUDENE). Esses estudos são novidade em relação à tese, que não incluía avaliações de incentivos estaduais. Contextualizar: "Embora os instrumentos federais constituam o foco desta revisão, dois estudos identificados avaliam o Prodepe — programa estadual de incentivos fiscais de Pernambuco — em interação com políticas federais, fornecendo evidências complementares sobre os mecanismos de transmissão dos benefícios tributários."
> **Fonte na tese:** Ausente. Esses estudos NÃO aparecem na tese.
> **Adaptações necessárias:** [NOVO] Subseção inteiramente nova.

**Estudos a discutir:**

10. **Oliveira2020a** — DID com efeitos heterogêneos por exposição, Pernambuco, 2000-2017
   - Avalia Prodepe + FNE + FDNE + BNDES + IF-SUDENE simultaneamente
   - Emprego: +8,6%*
   - Salário médio: **-10,3%** (efeito negativo)
   - Massa salarial: sem efeito para empresas que recebem apenas Prodepe
   - Combinação com outras políticas altera os efeitos
   - [NOTA] Resultado importante: redução do salário médio em empresas beneficiadas exclusivamente pelo Prodepe, o que levanta questões sobre a qualidade dos empregos gerados.

11. **Alves2024** — DID escalonado (Callaway & Sant'Anna), Pernambuco, 2000-2017
   - Prodepe + interação com políticas federais
   - Emprego: +22,3%*; massa salarial: +15,1%*; salário médio: **-8,2%**
   - Efeitos melhores em: empresas do Semiárido, pequenas empresas, setor industrial
   - Temporalidade: efeitos positivos sobre emprego e massa salarial declinam ao longo do tempo; redução salarial também se dissipa
   - [NOTA] Padrão consistente com Oliveira2020a: geração de emprego acompanhada de redução do salário médio. Sugere que incentivos fiscais atraem ou expandem atividades de menor remuneração.

**Parágrafo de síntese parcial:**
> Os dois estudos sobre o Prodepe revelam padrão preocupante: embora os incentivos fiscais estaduais gerem empregos (+8,6% a +22,3%), esses novos postos são acompanhados de redução no salário médio (-8,2% a -10,3%). Esse resultado contrasta com os achados dos FC e dos IF-SUDENE, onde o salário médio tipicamente permanece inalterado (sem efeito significativo). A redução salarial pode indicar que os incentivos estaduais atraem atividades de menor valor agregado ou expandem contratações em faixas salariais inferiores. Os efeitos temporários (Alves2024) reforçam a preocupação sobre a sustentabilidade dos benefícios após o encerramento dos incentivos.

---

### 4.3.6 Parágrafo de síntese e lacunas
> **Descrição:** Sintetizar os achados, apontar convergências e divergências, e identificar lacunas na literatura sobre IF.
> **Fonte na tese:** Linhas 141-142 (breve e genérico)
> **Adaptações necessárias:** [REESCREVER] Expandir substancialmente. A tese se limita a dizer "evidências inconclusivas". O artigo deve ser mais analítico.

**Pontos a cobrir na síntese:**

- **Convergência:** Efeitos positivos sobre emprego formal são consistentes em todos os estudos de IF-SUDENE, com magnitudes de 3,2% a 30% conforme setor e método
- **Divergência 1:** Efeitos sobre PIB são inconclusivos (NS em Carneiro2024; positivo sobre IDM em FerreiraIrffiCarneiro2024)
- **Divergência 2:** Efeito sobre salário — nulo nos IF-SUDENE, negativo nos IF estaduais (Prodepe)
- **Padrão setorial:** Efeitos mais expressivos em setores intensivos em mão de obra (turismo, manufatura)
- **Padrão temporal:** Efeitos crescentes nos primeiros anos, com evidências de temporalidade nos IF estaduais

**Lacunas críticas:**
1. **IF-SUDAM:** Nenhuma avaliação dedicada; único registro é Souza2025 (multi-instrumento)
2. **PIB per capita:** Nenhum estudo avalia exclusivamente o efeito dos IF sobre o PIB; resultados disponíveis são derivados de modelos multi-instrumento
3. **Variáveis de resultado:** Ausência de avaliações sobre desigualdade, pobreza, produtividade, PIB setorial
4. **Métodos:** Predominância de DID; apenas 1 estudo com controle sintético e 1 com painel espacial dedicado a IF. Ausência de RDD, PSM e equilíbrio geral
5. **Dados:** Dificuldade de acesso a microdados de renúncia fiscal; todos os estudos usam proxy (presença de empresa beneficiada no município vs. montante real do incentivo)
6. **Efeito distributivo:** Braz2023 levanta preocupação sobre concentração de efeitos em municípios já desenvolvidos
7. **Custo-efetividade:** Nenhum estudo estima o custo fiscal por emprego gerado ou por unidade de PIB adicional

- Prioridades para agenda de pesquisa: avaliações de IF-SUDAM, estudos com microdados fiscais, análise de custo-efetividade, métodos com maior poder de identificação causal para efeitos sobre PIB.

---

## Elementos não textuais

[TABELA] Quadro X: Estudos de Impacto dos Incentivos Fiscais
- Fonte: `c:\OneDrive\github\tese\arquivos_latex\latex_tese\tabelas\1-survey\survey_artigos_if.tex`
- Descrição: Tabela-resumo dos estudos que avaliam impacto dos IF, organizada por método, com colunas para artigo, publicação, amostragem, variável independente, variável dependente e resultado.
- Adaptação: [REESCREVER] A tabela da tese tem 7 linhas. O artigo deve:
  - **Remover** CostaCarneiroIrffi2023 (não aprovado na revisão) → 6 linhas restantes da tese
  - **Adicionar** Oliveira2020a (Prodepe, 2020) e Alves2024 (Prodepe, 2024) → 8 linhas
  - Atualizar formato para o padrão do artigo (`booktabs`, `\fonte{}`)
  - Usar chaves BibTeX consistentes com as seções 4.1/4.2

---

## Checklist pré-escrita

- [x] Leu o arquivo da tese correspondente (`1-4-discussao-dos-resultados.tex`, subseção IF)
- [x] Leu tabela da tese (`survey_artigos_if.tex`)
- [x] Consultou `data/2-papers/2-2-papers.json` para contagens e detalhes dos estudos (9 aprovados com IF)
- [x] Verificou `data/3-ref-bib/citation_index_report.txt` para IC (Braz2023: IC 0,2857; Garsous2017: IC 0,1000)
- [x] Identificou todos os elementos não textuais (1 tabela a adaptar, 0 figuras novas)
- [x] Mapeou diferenças entre tese e artigo (9 estudos vs. 7 na tabela da tese; 2 estudos Prodepe novos)
- [x] Verificou chaves BibTeX em `references.bib`
- [x] Não incluiu nenhum texto definitivo sem aprovação

---

## Alertas e ações na redação

1. **Erros de chave na versão comentada do `resultados.tex` (linhas 122-127):**
   - `\citeonline{Carneiro2023}` referencia o estudo multi-instrumento DID → corrigir para `\citeonline{Carneiroetal2024a}`
   - `\citeonline{Carneiro2024}` referencia o estudo espacial SAC → corrigir para `\citeonline{FerreiraIrffiCarneiro2024}`
   - **Ação:** Corrigir ambas as referências na redação final.

2. **CostaCarneiroIrffi2023 REMOVIDO — RESOLVIDO:**
   - `CostaCarneiroIrffi2023` (ANPEC 2023, DID dois estágios, vínculos +9,82%) **NÃO está na base aprovada**
   - `Costa2024` (Applied Economics Letters, Controle Sintético, +19,6%) **É o estudo aprovado** (Study #1)
   - São estudos distintos (métodos e resultados diferentes), mas apenas Costa2024 foi aprovado
   - `CarneiroCostaIrffi2024b` (Cadernos Fin. Públicas) e `CarneiroUmaNotaSobre` (RBE 2025) também NÃO aprovados
   - **Ação:** Remover CostaCarneiroIrffi2023 do texto e da tabela. Discutir apenas Costa2024.

3. **Contagem — RESOLVIDA:** 35 estudos aprovados (confirmado em `2-2-papers.json`). Consistente com seções 4.1 e 4.2.

4. **Prodepe — DECIDIDO:** Incluir. Os mesmos estudos avaliam IF-SUDENE em Pernambuco.

5. **Subsubsections — DECIDIDO:** Não usar. Parágrafos temáticos com conectivos.

6. **Gondim2025 vs. Oliveira2026:** Usar `gondim2025` (chave usada na seção 4.2 escrita). Verificar capitalização.

7. **Versão comentada incompleta:** A redação deve expandir substancialmente, incluindo Carneiro2023a (DEA), Oliveira2020a e Alves2024 (Prodepe), Gondim2025 e Souza2025 (referências cruzadas).
