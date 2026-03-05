# Parecer de Avaliacao -- Metodo

**Data:** 2026-03-05
**Escopo:** Metodo
**Nivel:** secao
**Arquivo(s) avaliado(s):** latex/main.tex, latex/metodo.tex
**Trecho avaliado:** integral

---

## 1. Parecer geral

A secao Metodo do artigo "Avaliacao dos Instrumentos da PNDR" apresenta descricao competente e suficientemente detalhada do protocolo de revisao sistematica, cobrindo desde a estrategia de busca ate a descricao dos estudos selecionados. A organizacao em oito subsecoes segue logica sequencial coerente com as etapas do processo PRISMA 2020, e o texto logra equilibrar rigor tecnico com clareza expositiva na maioria dos trechos. A inclusao de inovacoes metodologicas -- classificacao assistida por LLM, deduplicacao em multiplas fases e indice de citacao cruzada -- confere originalidade relevante a secao e constitui contribuicao nao trivial para a literatura de revisoes sistematicas em economia.

Nao obstante, identificam-se fragilidades que comprometem parcialmente a publicabilidade do texto em sua versao atual. A principal delas e a divergencia entre o nome do modelo de linguagem reportado no artigo (Gemini 2.0 Flash) e o modelo efetivamente utilizado no pipeline (gemini-2.5-flash-lite), erro factual que afeta a reprodutibilidade e a credibilidade da descricao metodologica. Alem disso, o processo de deduplicacao e descrito como tendo "tres fases" no artigo, quando a documentacao do pipeline registra quatro fases (DOI, titulo fuzzy, PDF identico e manual TD/WP), sendo que os 28 removidos resultam da soma das quatro. A secao tambem carece de explicacao mais precisa sobre a contagem de registros: o texto afirma "146 registros" das bases, "28 duplicatas" removidas, resultando em "118 unicos", mas o diagrama PRISMA mostra "119 apos remocao de duplicatas", porque a inclusao manual (+1) e contabilizada antes da triagem. Embora a nota de rodape mencione o repositorio, nao ha descricao suficiente dos limiares computacionais empregados (e.g., o valor de corte de 80% no token sort ratio aparece apenas na documentacao interna, nao no artigo). Por fim, a Tabela do IC (tabela_ic.tex) emprega formato inconsistente com o padrao C12 da skill de escrita, e algumas tabelas descritivas usam posicionamento [H] em vez de [htbp].

Em termos de proporcionalidade, a secao Metodo representa aproximadamente 211 linhas LaTeX de um total de 616 (34% do corpo textual, excluindo preambulo), o que esta levemente acima da faixa recomendada de 20-25% para artigos de revisao. Considerando, porem, que as inovacoes metodologicas sao contribuicoes centrais do artigo, a extensao e justificavel, embora condensacoes pontuais sejam desejaveis nas subsecoes descritivas (bases de dados, descricao de estudos).

---

## 2. Quadro-resumo

| Dimensao | Nota | Resumo |
|----------|------|--------|
| D1. Coerencia logica | B | Encadeamento logico solido entre subsecoes, com transicoes adequadas, mas com lacunas pontuais na argumentacao sobre criterios de inclusao de DEA/EGC e na justificativa da contagem de duplicatas. |
| D2. Estrutura e organizacao | B | Arquitetura em 8 subsecoes bem delimitadas e sequenciais; proporcionalmente extensa mas justificavel pelas inovacoes; redundancia menor entre 3.1 e 3.6. |
| D3. Estilo e registro | A | Registro academico consistente, impessoal, preciso; boa variedade lexical; concisao adequada na maioria dos paragrafos. |
| D4. Convencoes de artigo | B | Protocolo PRISMA descrito e fluxograma presente; criterios de inclusao/exclusao claros; reprodutibilidade parcialmente comprometida por omissao de parametros computacionais e erro no nome do modelo LLM. |
| D5. Qualidade do LaTeX | B | Compilavel e funcional; inconsistencia no posicionamento de floats ([H] vs [htbp]); tabela IC fora do padrao C12; diagrama PRISMA bem construido em TikZ. |
| D6. Pontos fortes | -- | Originalidade metodologica expressiva: classificacao LLM com revisao humana integral, indice de citacao cruzada para literatura cinzenta e pipeline de deduplicacao sistematico sao contribuicoes relevantes para a area. |

---

## 3. Avaliacao detalhada

### D1. Coerencia logica e argumentativa

| # | Sev. | Local | Descricao | Recomendacao |
|---|------|-------|-----------|--------------|
| 1.1 | [C] | Subsec. 3.4, L43-45 | O texto descreve "algoritmo automatizado em tres fases sequenciais" (DOI, titulo fuzzy, PDF hash), mas a documentacao do pipeline registra quatro fases, incluindo a remocao manual de versoes TD/WP (9 registros). As 28 duplicatas removidas resultam da soma das quatro fases (5+4+10+9=28), nao de tres. A omissao da quarta fase compromete a rastreabilidade do processo. | Descrever as quatro fases de deduplicacao, incluindo a fase manual de identificacao de versoes TD/congresso de artigos publicados. Alternativamente, esclarecer que as tres fases automatizadas removeram 19 duplicatas e que 9 adicionais foram identificadas manualmente. |
| 1.2 | [I] | Subsec. 3.3, L36 | A inclusao de estudos com DEA e EGC e justificada como excecao aos criterios de inclusao econometricos, porem a justificativa e vaga ("integram o corpo de evidencias quantitativas"). Nao se explica por que essas abordagens merecem excecao enquanto outras (Shift-Share, analise qualitativa) sao excluidas. | Fortalecer a justificativa: DEA e EGC sao incluidos porque permitem inferencias contrafactuais sobre eficacia/eficiencia dos instrumentos, embora por mecanismo distinto da econometria (fronteira de eficiencia e calibracao de parametros, respectivamente). Citar precedente na literatura de revisoes que inclui essas abordagens. |
| 1.3 | [M] | Subsec. 3.1, L12 | Afirma-se que "119 registros unicos foram submetidos a analise de elegibilidade", mas o paragrafo anterior menciona "146 registros" menos "28 duplicatas" = 118 unicos, mais 1 manual = 119. A transicao entre 118 e 119 nao e explicitada no mesmo paragrafo, exigindo que o leitor infira a aritmetica. | Tornar explicita a soma: "Apos a remocao de 28 duplicatas, restaram 118 registros unicos. Acrescentado 1 documento identificado manualmente fora das bases, 119 registros foram submetidos a analise de elegibilidade." |
| 1.4 | [M] | Subsec. 3.7, L81-83 | A conclusao sobre estudos com IC=0 afirma que "sete deles correspondem a trabalhos recentes (2024-2025)", mas a tabela mostra 8 estudos com IC=0 entre os nao publicados. A referencia a "um estudo de 2017" (Oliveira2017c) fecha a conta, porem o texto nao menciona explicitamente o oitavo caso recente vs. antigo. Verificar se sao 7+1=8 ou se ha erro de contagem. | Conferir contagem e tornar explicita: "Dos 8 estudos nao publicados com IC=0, 7 correspondem a trabalhos recentes (2024-2025) [...] e 1 estudo de 2017 [...]." |

### D2. Estrutura e organizacao

| # | Sev. | Local | Descricao | Recomendacao |
|---|------|-------|-----------|--------------|
| 2.1 | [I] | Subsec. 3.2 (L23-29) | A subsecao "Bases de dados consultadas" repete parcialmente informacoes ja presentes na subsecao 3.1 (nomes das bases, justificativa de multiplas fontes). Os paragrafos sobre Google Scholar e Web of Science tambem poderiam ser condensados ou integrados em nota de rodape. | Condensar 3.2 em 2-3 paragrafos focados no criterio de selecao de cada base, eliminando a repeticao de informacoes ja expostas em 3.1. Mover justificativa de exclusao de Google Scholar/Web of Science para nota de rodape. |
| 2.2 | [M] | Subsec. 3.8 (L86-210) | A subsecao "Descricao dos estudos obtidos" contem 4 tabelas (estudos-ano, unidade-amostral, autores, instrumentos) e 1 tabela de metodos, alem de texto descritivo. A proporcionalidade e elevada para uma subsecao descritiva, podendo ser subdividida em "Perfil dos estudos" e "Abordagens metodologicas". | Considerar dividir a subsecao 3.8 em duas: 3.8a (perfil temporal, autores, instrumentos, unidades amostrais) e 3.8b (metodos e escala MSM), facilitando a navegacao e a referencia cruzada. |
| 2.3 | [S] | Subsec. 3.6 e 3.1 | A subsecao 3.6 (Triagem final) reitera informacoes sobre o papel do LLM ja discutidas em 3.5 e sobre a inclusao manual ja mencionada em 3.1. Ha sobreposicao funcional. | Considerar fundir 3.5 e 3.6 em uma unica subsecao "Triagem: classificacao assistida por LLM e revisao manual", eliminando redundancia. |
| 2.4 | [S] | Tabelas 3-4, L94-181 | As tabelas de estudos-ano e unidade-amostral, bem como autores e instrumentos, estao dispostas em pares lado a lado via minipage. Embora funcional, os pares nao agrupam informacoes tematicamente afins (estudos-ano com unidade-amostral; autores com instrumentos). | Considerar reagrupar: estudos-ano com instrumentos (ambos sobre a composicao da amostra) e autores com unidade-amostral (ambos sobre caracteristicas estruturais dos estudos). |

### D3. Estilo e registro academico

| # | Sev. | Local | Descricao | Recomendacao |
|---|------|-------|-----------|--------------|
| 3.1 | [M] | Subsec. 3.5, L50 | "tem se difundido" -- a forma correta com enfase no Brasil e "tem-se difundido" (proclise obrigatoria com pronome apassivador). | Corrigir para "tem-se difundido". |
| 3.2 | [M] | Subsec. 3.5, L56 | Paragrafo com 5 frases longas, totalizando cerca de 130 palavras, proximo do limite de 150. A ultima frase ("As alteracoes mais relevantes envolveram...") contem duas informacoes independentes (reclassificacao de aprovados e correcao de tipo de publicacao) e poderia ser dividida. | Dividir o paragrafo apos "verificacao posterior" e abrir novo paragrafo com as correcoes especificas. |
| 3.3 | [S] | Subsec. 3.8, L183 | "predominam analises em nivel municipal (20 estudos)" -- "predominam" seguido de lista de frequencias pode ser substituido por construcao mais direta: "A maioria dos estudos (20 de 34) adota o municipio como unidade de analise". | Reescrever para maior clareza. |
| 3.4 | [S] | Subsec. 3.1, L8 | "com o intuito de assegurar transparencia e reprodutibilidade" -- "com o intuito de" e locucao mais longa que "a fim de" ou "para". | Substituir por "a fim de assegurar" ou "para assegurar". |

### D4. Convencoes de artigo cientifico em economia

| # | Sev. | Local | Descricao | Recomendacao |
|---|------|-------|-----------|--------------|
| 4.1 | [C] | Subsec. 3.5, L50 | O texto reporta "Gemini 2.0 Flash, Google" como modelo utilizado na classificacao. A documentacao do pipeline (run_llm_all_papers.py, L100) registra "gemini-2.5-flash-lite" como modelo efetivamente empregado. Divergencia factual que compromete reprodutibilidade. | Corrigir para o nome correto do modelo: "Gemini 2.5 Flash Lite (Google)". Idealmente, reportar tambem a versao da API e a data de execucao. |
| 4.2 | [I] | Subsec. 3.4 | Os parametros computacionais da deduplicacao (limiar de 80% para token sort ratio, normalizacao lowercase de DOI, verificacao de "mesmo ano E (mesmo primeiro autor OU mesmo periodico)") nao sao reportados no artigo. Essas informacoes sao essenciais para reprodutibilidade. | Incluir no texto ou em nota de rodape: limiar de similaridade (80%), criterios adicionais de confirmacao (coincidencia de ano e de primeiro autor ou periodico), e tipo de hash criptografico utilizado na fase 3. |
| 4.3 | [I] | Subsec. 3.7 | O indice de citacao cruzada (IC) e formalmente definido, mas os parametros do algoritmo de matching (tolerancia de +/- 2 anos, similaridade por token sort ratio, restricao cronologica) nao sao suficientes para reproduzir exatamente os resultados. Falta mencionar: tratamento de autores com sobrenome unico, penalizacao de falsos positivos, comparacao com titulo LLM alem do titulo original. | Detalhar os parametros do algoritmo de matching do IC, incluindo as diferencas em relacao ao matching de citacoes cruzadas descrito na documentacao (tolerancia de anos, thresholds de similaridade, tratamento de sobrenomes). |
| 4.4 | [M] | Subsec. 3.1, L12 | O texto menciona que o protocolo "nao foi registrado previamente em plataforma de registro de revisoes", conforme recomendado pelo PRISMA 2020. Embora transparente, a ausencia de registro previo e uma limitacao que deveria ser reconhecida com breve justificativa (ex: ausencia de plataforma adequada para revisoes em economia, onde o PROSPERO nao se aplica). | Adicionar justificativa breve para a ausencia de registro previo. |
| 4.5 | [M] | Subsec. 3.3, L34 | A descricao dos blocos de busca lista os termos entre aspas, mas nao apresenta a query completa em formato reproduzivel. As queries exatas estao no pipeline_extraction.md mas nao no artigo. Para um artigo de revisao sistematica, a reprodutibilidade exige que as queries sejam integralmente apresentadas (em apendice ou material suplementar, se extensas). | Incluir as queries completas em material suplementar ou apendice, referenciando-as no texto. Alternativamente, indicar explicitamente que estao disponiveis no repositorio (ja feito na nota de rodape, mas poderia ser mais enfatico). |
| 4.6 | [M] | Geral | O diagrama PRISMA 2020 esta presente e corretamente formatado, porem nao inclui a fase de "pre-classificacao LLM" como etapa intermediaria, que e uma inovacao do artigo. O fluxo salta de "triagem (n=119)" para "avaliacao em texto completo (n=119)" sem diferenciar a contribuicao do modelo de linguagem. | Considerar adicionar caixa intermediaria no diagrama PRISMA indicando a etapa de classificacao LLM, diferenciando-a da triagem final humana, para refletir a inovacao metodologica. |
| 4.7 | [S] | Subsec. 3.5 | Nao ha referencia a prompts ou questionarios utilizados com o LLM. Embora os questionarios estejam disponiveis no repositorio, o artigo deveria mencionar explicitamente que os questionarios estao documentados e disponiveis, descrevendo ao menos a estrutura geral (tipos de campo, instrucoes de preenchimento). | Adicionar referencia explicita aos questionarios como material suplementar e descrever brevemente sua estrutura. |

### D5. Qualidade do LaTeX

| # | Sev. | Local | Descricao | Recomendacao |
|---|------|-------|-----------|--------------|
| 5.1 | [I] | Tabelas em 3.8 (L94, 134, 187) e tabela_ic.tex | Todas as tabelas usam posicionamento `[H]` (float forçado), contrariando a pratica recomendada `[htbp]` e a regra da skill de escrita. O uso de `[H]` pode causar grandes espacos em branco e requer o pacote `float`. | Substituir `[H]` por `[htbp]` em todas as tabelas da secao. |
| 5.2 | [I] | tabela_ic.tex | A tabela IC nao segue o padrao C12: (a) caption e label estao antes do tabular (correto), mas (b) a nota/fonte esta como ultima linha dentro do tabular via multicolumn (correto na forma, mas o formato geral diverge das demais tabelas do artigo que usam \fonte{} como comando separado). Mais importante: a divisao em dois blocos (publicados / nao publicados) usa \midrule + \multicolumn para titulo de secao, quando seria mais adequado usar \cmidrule ou um ambiente separado. | Padronizar a tabela IC com o formato C12. Considerar dividir em duas tabelas ou usar ambiente mais adequado para a secao bipartida. |
| 5.3 | [M] | Subsec. 3.8, L111 | Rodape da tabela estudos-ano usa `\multicolumn{2}{l}{\footnotesize Fonte: ...}` dentro do tabular, enquanto a tabela de metodos (L204) usa `\multicolumn{3}{p{11cm}}{\footnotesize Nota: ... Fonte: ...}`. Inconsistencia no formato do rodape entre tabelas da mesma secao. | Padronizar todas as tabelas para o formato C12 com `\multicolumn{N}{l}{\footnotesize ...}`. |
| 5.4 | [M] | diagrama_prisma.tex | O diagrama PRISMA nao inclui etapa de "Registros excluidos por duplicacao", que e uma caixa recomendada pelo PRISMA 2020 na fase de Identificacao. A caixa "n=28" de duplicatas removidas esta implicita pela diferenca 146->119, mas nao visivel no diagrama. | Adicionar caixa lateral na fase Identificacao: "Registros removidos por duplicacao (n=28)". |
| 5.5 | [S] | Subsec. 3.8, L98 | As tabelas lado a lado usam `\begin{minipage}[t]{0.38\textwidth}` e `0.58\textwidth`, totalizando 0.96 da largura. A assimetria e intencional mas nao documentada. | Nenhuma acao necessaria, apenas observacao. |

### D6. Pontos fortes e contribuicao

| # | Sev. | Local | Descricao | Recomendacao |
|---|------|-------|-----------|--------------|
| 6.1 | -- | Subsec. 3.5 | A descricao da classificacao assistida por LLM com revisao humana integral e uma contribuicao metodologica relevante. A transparencia na reportagem de correcoes (125 campos em 78 registros, 35 reclassificacoes) confere credibilidade ao processo e constitui evidencia empirica sobre a acuracia de LLMs em triagem de revisoes sistematicas. | Potencializar esta contribuicao calculando e reportando metricas de acuracia do LLM (taxa de falsos positivos, falsos negativos, precisao e recall na triagem). |
| 6.2 | -- | Subsec. 3.7 | O indice de citacao cruzada (IC) e uma abordagem inovadora para justificar a inclusao de literatura cinzenta em revisoes sistematicas. A formalizacao matematica e a demonstracao empirica de que 10 dos 18 estudos nao publicados tem IC positivo fornecem base objetiva para a decisao de inclusao. | Considerar comparar o IC com metricas externas (Google Scholar citations) para validar a abordagem. |
| 6.3 | -- | Subsec. 3.4 | O pipeline de deduplicacao em multiplas fases (DOI, titulo, PDF, manual) e sistematico e bem documentado, superando a pratica comum de deduplicacao ad hoc. A ordem de prioridade de retencao por base e criterio transparente e reproduzivel. | Destacar mais enfaticamente esta contribuicao no texto, comparando com praticas de deduplicacao em outras revisoes sistematicas da area. |
| 6.4 | -- | Subsec. 3.8 | A inclusao da escala MSM (Maryland Scientific Methods Scale) para classificar a robustez dos metodos e uma pratica pouco comum em revisoes de economia regional, mas que agrega valor analitico significativo ao permitir comparacao transversal da qualidade das evidencias. | Manter e potencialmente expandir com referencia a outras aplicacoes da MSM em revisoes de politicas regionais. |

---

## 4. Recomendacoes priorizadas

### Criticas [C]

1. **Corrigir o nome do modelo LLM** (achado 4.1): Substituir "Gemini 2.0 Flash" por "Gemini 2.5 Flash Lite" (gemini-2.5-flash-lite) em toda a secao. Erro factual que invalida a reproducao do protocolo.

2. **Corrigir descricao da deduplicacao** (achado 1.1): O artigo descreve 3 fases automatizadas, mas a contagem de 28 duplicatas inclui 9 identificadas manualmente (fase 4). Ou descrever 4 fases, ou separar explicitamente "19 automatizadas + 9 manuais = 28".

### Importantes [I]

3. **Reportar parametros computacionais** (achado 4.2): Incluir limiares de similaridade (80% token sort ratio), criterios de confirmacao (ano + autor/periodico) e tipo de hash. Essencial para reprodutibilidade.

4. **Detalhar parametros do IC** (achado 4.3): Descrever tolerancia de anos, thresholds de similaridade e tratamento de sobrenomes no algoritmo de matching do indice de citacao.

5. **Fortalecer justificativa de inclusao DEA/EGC** (achado 1.2): Explicar por que essas abordagens merecem excecao em relacao ao criterio econometrico, com referencia a precedentes.

6. **Condensar subsecao 3.2** (achado 2.1): Eliminar repeticoes com 3.1 e mover justificativas de exclusao (Google Scholar, Web of Science) para nota de rodape.

7. **Padronizar posicionamento de floats** (achado 5.1): Substituir `[H]` por `[htbp]` em todas as tabelas.

### Menores [M]

8. **Tornar explicita a aritmetica 118+1=119** (achado 1.3): Clarificar no texto que 146-28=118 das bases + 1 manual = 119 total.

9. **Verificar contagem IC=0** (achado 1.4): Confirmar "7 recentes + 1 de 2017 = 8 com IC=0" e explicitar no texto.

10. **Incluir queries completas** (achado 4.5): Em apendice ou material suplementar, apresentar as queries exatas usadas em cada base.

11. **Adicionar caixa de duplicatas no diagrama PRISMA** (achado 5.4): Incluir "Registros removidos por duplicacao (n=28)" como caixa lateral na fase Identificacao.

12. **Padronizar rodapes de tabelas** (achado 5.3): Unificar formato de notas/fonte em todas as tabelas da secao.

13. **Correcao pronominal** (achado 3.1): "tem se difundido" -> "tem-se difundido".

14. **Justificar ausencia de registro previo** (achado 4.4): Breve justificativa de por que o protocolo nao foi registrado em plataforma como PROSPERO.

### Sugestoes [S]

15. **Considerar fusao de 3.5 e 3.6** (achado 2.3): Eliminar redundancia sobre papel do LLM vs. revisao manual.

16. **Calcular metricas de acuracia do LLM** (achado 6.1): Reportar precisao, recall e F1-score da classificacao automatizada vs. revisao humana.

17. **Adicionar etapa LLM ao diagrama PRISMA** (achado 4.6): Diferenciar visualmente a pre-classificacao automatizada da triagem final.

18. **Referencia explicita aos questionarios LLM** (achado 4.7): Mencionar que os prompts/questionarios estao documentados como material suplementar.

19. **Subdividir subsecao 3.8** (achado 2.2): Separar "Perfil dos estudos" de "Abordagens metodologicas".

---

## 5. Retroalimentacao da skill de escrita

| Problema identificado | Secao da skill (2-escrever-artigo.md) | Sugestao de alteracao |
|----------------------|---------------------------------------|----------------------|
| Tabelas com [H] em vez de [htbp] | Regras de escrita, item 8 (Tabelas) | A regra ja especifica [htbp]; reforcar com nota: "Verificar tabelas existentes e corrigir [H] para [htbp]." |
| Divergencia no nome do modelo LLM | Checklist pre-escrita | Adicionar item: "Verificar nome do modelo LLM contra scripts/run_llm_all_papers.py e scripts/src/config.py antes de mencionar no texto." |
| Deduplicacao descrita com 3 fases quando sao 4 | Fontes de dados para consulta | Adicionar referencia a docs/pipeline_extraction.md secao "Deduplicacao" como fonte obrigatoria para descricao do processo. |
| Parametros computacionais omitidos | Regras de escrita, novo item | Adicionar regra: "Ao descrever algoritmos computacionais, reportar obrigatoriamente: nome do algoritmo, limiares numericos, criterios de confirmacao e software/versao utilizado." |
| Inconsistencia no padrao de rodape entre tabelas | Regras de escrita, item 8 (padrao C12) | Adicionar verificacao: "Apos redigir secao com multiplas tabelas, verificar que todas seguem o mesmo formato de rodape (C12)." |
| Contagem 118 vs 119 nao explicitada | Regras de escrita, item 11 (Consistencia numerica) | A regra ja existe; reforcar: "Verificar aritmetica de todas as contagens sequenciais (A-B=C, C+D=E) no mesmo paragrafo." |
| Ausencia de metricas de acuracia do LLM | Inovacoes metodologicas (tabela) | Adicionar na tabela de inovacoes: "Metricas de acuracia LLM (precisao, recall) = a calcular a partir dos dados de correcao manual." |
| MSM nao detalhada na skill | Estrutura esperada, Secao 3, item 8 | Adicionar menção a escala MSM como elemento esperado na subsecao de descricao dos estudos. |

---

## 6. Observacoes adicionais

1. **Inconsistencia no pipeline_extraction.md**: O documento de pipeline reporta "variaveis de resultado fora do escopo (1)" na secao de motivos de rejeicao, mas os proprios registros do pipeline (secoes 11 e 12) indicam dois estudos excluidos por esse motivo. O artigo (metodo.tex) corretamente reporta n=2. Recomenda-se corrigir o pipeline_extraction.md para consistencia.

2. **Nota sobre o modelo LLM no pipeline_extraction.md**: Ha tambem inconsistencia interna no pipeline: a secao principal diz "gemini-2.5-flash-lite" (correto, conforme codigo), mas a secao "Decisoes metodologicas" ao final diz "Gemini 2.0 Flash". Ambas as mencoes devem ser unificadas.

3. **Tabela IC com estudo Oliveira2026**: A tabela IC contem entrada para \citeonline{Oliveira2026} com IC marcado como "--" (N=0). Se o estudo foi publicado em 2026, o calculo com intervalo [2026, 2026] resulta em N=0 (nenhum artigo publicado no mesmo ano alem do proprio), tornando o IC indefinido. Este caso merece nota explicativa na tabela ou no texto.

4. **Proporção da secao no artigo**: Com 211 linhas de um total de 616 linhas de conteudo (excluindo preambulo e bibliografia), a secao Metodo ocupa 34% do corpo textual. Embora acima do padrao para artigos de economia (20-25%), a proporcao e justificavel dadas as inovacoes metodologicas centrais. Recomenda-se avaliar se as subsecoes 3.2 (bases) e 3.8 (descricao) podem ser condensadas sem perda de informacao.

5. **Ausencia de limitacoes metodologicas da revisao**: A secao Metodo nao discute limitacoes do proprio protocolo (ex: busca limitada a 5 bases, risco de viés de idioma, dependencia de LLM para pre-triagem, ausencia de segundo revisor independente). Essas limitacoes poderiam ser brevemente mencionadas ao final da secao ou na secao de Consideracoes Finais. A checklist PRISMA 2020 recomenda explicitamente a descricao de limitacoes do processo de revisao.
