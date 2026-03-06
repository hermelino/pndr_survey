# Parecer de Avaliação — Seção 3: Método

**Data:** 2026-03-04
**Escopo:** Seção Método (completa)
**Nível:** Seção
**Arquivo(s) avaliado(s):** `latex/metodo.tex`, `latex/tabela_ic.tex`, `latex/diagrama_prisma.tex`
**Trecho avaliado:** Integral (8 subseções, ~204 linhas)

---

## 1. Parecer geral

A seção Método apresenta qualidade geral compatível com submissão a periódico Qualis A2 de economia, com arquitetura lógica bem definida e detalhamento suficiente para reprodutibilidade. O texto segue as diretrizes PRISMA 2020, organiza-se em oito subseções com progressão natural — da estratégia de busca à descrição dos estudos obtidos — e incorpora duas contribuições metodológicas relevantes: a classificação assistida por modelo de linguagem (com transparência exemplar sobre as correções humanas) e o índice de citação cruzada para legitimação de estudos não publicados em periódicos. O padrão de escrita é predominantemente objetivo, impessoal e tecnicamente preciso.

Os principais pontos de atenção concentram-se em inconsistências numéricas internas entre o diagrama PRISMA e o texto narrativo (118 vs. 119 registros triados; 83 vs. 84 excluídos), um erro factual isolado (referência a "36 estudos" quando o artigo consistentemente reporta 35) e um erro de concordância verbal. Do ponto de vista estrutural, há desequilíbrio de extensão entre subseções: "Descrição dos estudos obtidos" concentra cinco tabelas e discussão sobre a escala MSM, enquanto "Processo de deduplicação" limita-se a um único parágrafo. Ademais, a tabela de IC está posicionada ao final da subseção "Triagem final", mas é discutida apenas na subseção subsequente, o que pode confundir o leitor.

**Recomendação geral:** Aceitar com revisões menores. Os problemas identificados são pontuais e corrigíveis sem reescrita substancial. Após resolução das inconsistências numéricas e ajustes estruturais, a seção estará pronta para submissão.

---

## 2. Quadro-resumo

| Dimensão | Nota | Resumo |
|----------|------|--------|
| D1. Coerência lógica | B | Fio condutor claro, mas com inconsistências numéricas internas e uma generalização argumentativa no IC |
| D2. Estrutura e organização | B | Progressão lógica adequada, porém com desequilíbrio de extensão e posicionamento inadequado da tabela IC |
| D3. Estilo e registro | B | Tom acadêmico bem mantido; erro de concordância verbal isolado e parágrafo denso na subseção de bases |
| D4. Convenções de artigo | B | Aderência ao PRISMA 2020, boa reprodutibilidade; falta registro de protocolo e equação IC usa notação informal |
| D5. Qualidade do LaTeX | B | Estrutura sólida com labels consistentes; tabela IC viola padrão interno de formatação |
| D6. Pontos fortes | — | Contribuições metodológicas inovadoras (LLM, IC), transparência nas correções e reprodutibilidade via repositório |

---

## 3. Avaliação detalhada

### D1. Coerência lógica e argumentativa

O fio condutor da seção é claro e bem articulado: parte-se da estratégia global de busca, detalham-se as bases consultadas, definem-se critérios de inclusão/exclusão, descrevem-se os processos de deduplicação e classificação, apresenta-se a triagem final e justifica-se a inclusão de estudos não publicados via IC, encerrando com a descrição da amostra. Cada subseção decorre logicamente da anterior.

Identificam-se, contudo, inconsistências internas que comprometem a coerência factual e uma fragilidade argumentativa pontual na justificativa do IC.

#### Achados

| # | Sev. | Local | Descrição | Recomendação |
|---|------|-------|-----------|--------------|
| 1 | [C] | subsec:metodo-indice-citacao, linha 76 | O texto refere "36 estudos incluídos na revisão", quando todo o restante do artigo (inclusive a mesma subseção, linha 78) reporta 35. Erro factual que será imediatamente notado por parecerista. | Corrigir para "35 estudos". |
| 2 | [C] | `diagrama_prisma.tex` vs. `metodo.tex` linhas 12, 59 | O diagrama PRISMA registra 119 registros após deduplicação (146 + 1 manual − 28) e 84 excluídos. O texto narrativo reporta 118 registros únicos e 83 excluídos. A diferença de 1 unidade decorre da inclusão manual descrita na subsec:metodo-triagem-final, que não está refletida nos totais do texto. | Harmonizar os números. Recomenda-se adotar 119 triados e 84 excluídos (consistente com o PRISMA) e atualizar as referências textuais a "118" e "83" em todo o `metodo.tex`. Alternativamente, ajustar o diagrama. Usar `/atualizar-artigo` para verificar qual valor é correto com base nos dados do pipeline. |
| 3 | [M] | subsec:metodo-indice-citacao, linha 78 | A frase "Como o índice de citação de estudos não publicados são comparáveis ao dos artigos publicados, indicando que exercem influência relevante sobre a literatura publicada, optou-se pela manutenção deles na amostra" generaliza a conclusão de 10 estudos com IC > 0 para os 18 não publicados, incluindo 8 com IC = 0. A justificativa para os 8 com IC = 0 (insuficiência de tempo) é plausível, mas a redação funde os dois grupos em uma única conclusão. | Separar explicitamente os dois argumentos: (a) 10 estudos não publicados com IC > 0 demonstram relevância comparável; (b) os 8 restantes, publicados em 2024–2025, não acumularam citações por insuficiência do intervalo de observação, e sua inclusão justifica-se pelo atendimento aos critérios de elegibilidade. |
| 4 | [M] | subsec:metodo-indice-citacao → subsec:metodo-descricao-estudos | A transição entre a conclusão sobre o IC e a descrição dos estudos é abrupta. Não há parágrafo-ponte que sinalize o encerramento da discussão metodológica e a abertura da descrição da amostra. | Adicionar 1–2 frases de transição ao final da subsec:metodo-indice-citacao ou ao início da subsec:metodo-descricao-estudos. |
| 5 | [S] | subsec:metodo-indice-citacao, equação (1) | A notação do IC usa $[X+1,\; 2026]$ no numerador e denominador, onde $X$ é o ano de publicação do estudo. Para $X = 2026$, o intervalo é vazio, gerando $IC = 0/0$. A tabela trata esse caso com "---", mas a equação não formaliza a exceção. | Acrescentar nota sob a equação: "Para estudos publicados no último ano do intervalo ($X = 2026$), o IC é indefinido ($N = 0$)." |

### D2. Estrutura e organização

A seção organiza-se em oito subseções que seguem a sequência natural de um protocolo PRISMA. A progressão é lógica e as subseções são autocontidas. Há, porém, desequilíbrio de extensão e um problema de posicionamento de elemento flutuante.

#### Achados

| # | Sev. | Local | Descrição | Recomendação |
|---|------|-------|-----------|--------------|
| 6 | [I] | subsec:metodo-descricao-estudos (linhas 80–204) | Subseção desproporcionalmente longa em relação às demais: contém 5 tabelas (estudos-ano, unidade amostral, autores, instrumentos, métodos), além de discussão sobre a escala MSM, totalizando ~120 linhas. As demais subseções variam de 4 a 35 linhas. | Considerar subdividir: (a) manter as tabelas descritivas e seus parágrafos acompanhantes como "Descrição dos estudos obtidos"; (b) separar a discussão sobre robustez metodológica (escala MSM, linhas 201–203) em subseção própria, e.g., "Robustez das estratégias empíricas". |
| 7 | [I] | subsec:metodo-triagem-final, linha 61 | A tabela IC (`\input{tabela_ic}`) está incluída ao final de "Triagem final", mas é discutida apenas na subseção seguinte ("Índice de citação cruzada"). O leitor encontra a tabela antes de conhecer a metodologia do IC. | Mover `\input{tabela_ic}` para dentro da subsec:metodo-indice-citacao, após a explicação do método de cálculo e antes da interpretação dos resultados. |
| 8 | [M] | subsec:metodo-deduplicacao (linhas 38–41) | Subseção com apenas um parágrafo (~100 palavras). Poderia ser expandida com mais detalhes sobre os limiares utilizados (e.g., similaridade mínima de título) ou incorporada como parágrafo na subseção de estratégia de busca. | Expandir com detalhes do algoritmo (limiares, métricas de similaridade) ou integrar à subsec:metodo-estrategia-busca como parágrafo final. |
| 9 | [S] | subsec:metodo-descricao-estudos, linhas 89–175 | As cinco tabelas descritivas estão dispostas em pares via `minipage`, ocupando considerável espaço vertical. A tabela de métodos (tab:metodos) fica isolada. | Considerar agrupar as informações em formato mais compacto, e.g., unificando estudos-ano e instrumentos em uma única tabela, ou usando formato paisagem para uma tabela-resumo consolidada. |

### D3. Estilo e registro acadêmico

O texto mantém tom impessoal e objetivo de forma consistente, com uso adequado de voz passiva e construções impessoais. A terminologia técnica é empregada com precisão. Não há coloquialismos nem gerundismo. Nenhum parágrafo inicia com citação.

#### Achados

| # | Sev. | Local | Descrição | Recomendação |
|---|------|-------|-----------|--------------|
| 10 | [I] | subsec:metodo-indice-citacao, linha 78 | Erro de concordância verbal: "Como o índice de citação de estudos não publicados **são** comparáveis ao dos artigos publicados". O sujeito é "o índice de citação" (singular), requerendo verbo no singular. | Corrigir para "Como o índice de citação de estudos não publicados **é** comparável ao dos artigos publicados" ou reestruturar para "Como os índices de citação de estudos não publicados **são** comparáveis aos dos artigos publicados". |
| 11 | [M] | subsec:metodo-bases-dados, linha 25 | Parágrafo denso (~155 palavras) que descreve todas as cinco bases de dados em bloco contínuo. Embora não exceda drasticamente o limite de 150 palavras, a informação é densa e beneficiaria de segmentação. | Dividir em dois parágrafos: (a) bases de dados indexadas (Scopus, SciELO, Portal CAPES); (b) fontes de literatura cinzenta e congressos (EconPapers, ANPEC). |
| 12 | [S] | subsec:metodo-estrategia-busca, linha 8 | Frase longa (~50 palavras) com múltiplas intercalações por travessão. Embora gramaticalmente correta, a leitura é pesada. | Considerar dividir em duas frases: uma para o objetivo da revisão e outra para o escopo dos instrumentos avaliados. |
| 13 | [S] | Geral | Repetição moderada do termo "registros" ao longo da seção (aparece ~15 vezes). | Variar com "documentos", "trabalhos identificados" ou "itens bibliográficos" quando o contexto permitir, sem sacrificar precisão. |

### D4. Conformidade com convenções de artigo científico

A seção demonstra boa aderência às convenções de revisão sistemática, seguindo o protocolo PRISMA 2020 com diagrama de fluxo e descrição detalhada de cada etapa. O detalhamento metodológico é suficiente para reprodutibilidade, reforçado pela disponibilização dos scripts em repositório público. As citações são pertinentes e integradas ao texto.

#### Achados

| # | Sev. | Local | Descrição | Recomendação |
|---|------|-------|-----------|--------------|
| 14 | [M] | subsec:metodo-estrategia-busca | Ausência de menção a registro prévio do protocolo da revisão (e.g., PROSPERO ou OSF). O PRISMA 2020 recomenda explicitamente o registro do protocolo (item 24a). Se não houve registro, é recomendável declarar esse fato. | Acrescentar frase indicando se o protocolo foi ou não registrado em plataforma de registro de revisões. |
| 15 | [M] | subsec:metodo-indice-citacao, equação (1) | A equação usa notação semi-formal com texto corrido dentro de `\text{}` e intervalos em colchetes. Para artigo de economia, notação mais compacta seria preferível. | Substituir por notação formal, e.g.: $IC_i = C_i / N_i$, onde $C_i$ é o número de citações recebidas por $i$ de artigos publicados em periódicos, e $N_i$ é o total de artigos publicados em periódicos no intervalo $(t_i, 2026]$. |
| 16 | [M] | Geral | As tabelas descritivas (tab:estudos-ano, tab:unidade-amostral, tab:autores-todos, tab:instrumentos, tab:metodos) usam `\fonte{Elaboração própria.}`, o que é adequado. Porém, não indicam explicitamente a base de dados de origem (e.g., "com base em 2-2-papers.json"). | Para artigo publicado, "Elaboração própria" é suficiente. Nenhuma ação necessária, mas garantir que os dados coincidam com o pipeline (tarefa de `/atualizar-artigo`). |
| 17 | [S] | subsec:metodo-classificacao-llm | O texto reporta que 35 registros foram reclassificados de aprovado para rejeitado pelo revisor humano, indicando precisão do LLM de ~50% na classe "elegível". Esse dado é reportado factualmente, mas não é interpretado em termos de limitações ou implicações para a metodologia. | Considerar acrescentar 1–2 frases discutindo a taxa de concordância LLM-humano e suas implicações para a confiabilidade da pré-triagem automatizada. |

### D5. Qualidade do LaTeX

A estrutura LaTeX é sólida, com labels padronizados (`subsec:metodo-*`, `tab:*`, `fig:*`, `eq:ic`), referências cruzadas funcionais e uso correto de ambientes flutuantes e `booktabs`.

#### Achados

| # | Sev. | Local | Descrição | Recomendação |
|---|------|-------|-----------|--------------|
| 18 | [I] | `tabela_ic.tex`, linha 34 | A nota e a fonte estão **dentro** do ambiente `tabular`, como última linha antes de `\end{tabular}`: `\multicolumn{5}{l}{\footnotesize Nota: ... Fonte: Elaboração própria.}`. Isso viola o padrão interno do artigo, que prescreve `\nota{}` e `\fonte{}` como comandos separados, posicionados **após** `\end{tabular}` e **dentro** de `\begin{table}`. | Extrair nota e fonte do tabular: usar `\nota{--- = IC não calculável...}` e `\fonte{Elaboração própria.}` após `\end{tabular}`, conforme padrão das demais tabelas. |
| 19 | [M] | `metodo.tex`, linhas 89–197 | As cinco tabelas descritivas usam `\small` em vez de `\footnotesize` e não incluem `\renewcommand{\arraystretch}{1.2}`, divergindo do padrão prescrito pela skill de escrita e usado na tabela IC. | Padronizar com `\footnotesize` e `\renewcommand{\arraystretch}{1.2}` em todas as tabelas. |
| 20 | [M] | `tabela_ic.tex`, linha 28 | Chave de citação `\citeonline{Velooso2024}` apresenta possível erro de digitação: "Velooso" vs. "Veloso" (cf. `\citeonline{Veloso2025}` na linha 32 da mesma tabela e `\citeonline{Veloso2025}` em `resultados.tex`). | Verificar no arquivo `references.bib` se a chave correta é `Veloso2024` ou `Velooso2024`. Se for erro, corrigir em `tabela_ic.tex` e no `.bib`. |
| 21 | [S] | `diagrama_prisma.tex` | O diagrama usa `tikzpicture` com valores absolutos de espaçamento (`8mm`, `12mm`, `15mm`), o que pode causar problemas de alinhamento em diferentes compiladores ou configurações de página. | Considerar testar compilação em diferentes ambientes para garantir consistência visual. |

### D6. Pontos fortes e contribuição

A seção Método apresenta contribuições diferenciadas que merecem destaque:

1. **Classificação assistida por LLM com transparência exemplar.** A descrição do processo em três estágios, com questionários tipados e campos estruturados, seguida de relato quantitativo das correções humanas (125 campos corrigidos em 78 registros, 35 reclassificações de triagem), constitui um dos melhores exemplos de transparência no uso de IA em revisão sistemática. Essa abordagem permite ao leitor avaliar tanto a utilidade quanto as limitações do modelo.

2. **Índice de citação cruzada (IC).** A criação de métrica específica para justificar a inclusão de working papers e apresentações em congresso é uma contribuição metodológica original. A comparação direta entre ICs de estudos publicados e não publicados oferece evidência empírica de relevância acadêmica, superando a prática usual de inclusão/exclusão arbitrária.

3. **Aderência ao PRISMA 2020.** O diagrama de fluxo, a descrição detalhada de bases e critérios e a nota de rodapé com link para o repositório público garantem nível elevado de reprodutibilidade.

4. **Cobertura ampla de bases.** A justificativa para cada uma das cinco bases — incluindo a motivação explícita para inclusão de literatura cinzenta — e a explicação para a exclusão de Google Scholar e Web of Science demonstram rigor na delimitação do escopo.

5. **Escala MSM.** A aplicação da escala Maryland Scientific Methods para classificar a robustez dos estudos incluídos acrescenta dimensão avaliativa à revisão, indo além da mera descrição.

---

## 4. Recomendações priorizadas

### Críticas [C]
1. Corrigir "36 estudos" → "35 estudos" na subsec:metodo-indice-citacao, linha 76 (achado #1).
2. Harmonizar contagens entre o diagrama PRISMA (119 triados, 84 excluídos) e o texto narrativo (118/83). Executar `/atualizar-artigo` para determinar os valores corretos com base no pipeline (achado #2).

### Importantes [I]
3. Mover `\input{tabela_ic}` da subsec:metodo-triagem-final para dentro da subsec:metodo-indice-citacao (achado #7).
4. Subdividir subsec:metodo-descricao-estudos, separando a discussão da escala MSM em subseção própria (achado #6).
5. Corrigir concordância verbal: "são comparáveis" → "é comparável" na subsec:metodo-indice-citacao (achado #10).
6. Corrigir formatação de `tabela_ic.tex`: extrair nota e fonte do ambiente tabular (achado #18).

### Menores [M]
7. Separar os dois argumentos de justificativa no IC: estudos com IC > 0 vs. estudos recentes com IC = 0 (achado #3).
8. Expandir subsec:metodo-deduplicacao com detalhes algorítmicos ou integrar à subsec:metodo-estrategia-busca (achado #8).
9. Dividir o parágrafo denso da subsec:metodo-bases-dados em dois (achado #11).
10. Padronizar `\small` → `\footnotesize` e adicionar `\arraystretch` nas tabelas descritivas (achado #19).
11. Verificar chave de citação `Velooso2024` em `tabela_ic.tex` (achado #20).
12. Mencionar registro (ou ausência) de protocolo da revisão (achado #14).
13. Formalizar notação da equação IC (achado #15).
14. Adicionar transição entre subsec:metodo-indice-citacao e subsec:metodo-descricao-estudos (achado #4).

### Sugestões [S]
15. Definir exceção para IC quando $X = 2026$ (achado #5).
16. Interpretar brevemente a taxa de concordância LLM-humano (achado #17).
17. Simplificar frase longa na subsec:metodo-estrategia-busca (achado #12).
18. Variar uso do termo "registros" (achado #13).
19. Considerar formato mais compacto para tabelas descritivas (achado #9).

---

## 5. Retroalimentação da skill de escrita

| # | Problema detectado | Seção da skill `/escrever-artigo` | Sugestão de alteração |
|---|-------------------|----------------------------------|----------------------|
| 1 | Inconsistência numérica entre o diagrama PRISMA e o texto narrativo — mesma informação aparece com valores diferentes em dois arquivos `.tex` distintos | Regras de escrita (não há regra vigente) | Adicionar regra: "Ao referenciar contagens que apareçam em diagramas, tabelas ou figuras incluídos via `\input{}`, verificar que os valores no texto narrativo coincidam **exatamente** com os valores no arquivo incluído. Após editar qualquer contagem, executar busca textual nos demais arquivos `.tex` da seção para garantir consistência." |
| 2 | Tabela IC com nota/fonte dentro do tabular, violando o padrão prescrito pela própria skill | Regras de escrita, item 8 (Tabelas) | Reforçar: "Essa regra aplica-se **inclusive** a tabelas em formato `landscape` e tabelas incluídas via `\input{}`. Em hipótese alguma inserir `Fonte:` ou `Nota:` como última linha do `tabular`." |
| 3 | Subseção "Descrição dos estudos obtidos" excessivamente longa, concentrando múltiplas tabelas e temas | Estrutura esperada do artigo, Seção 3 | Adicionar diretriz: "Subseções com mais de 3 tabelas ou quadros devem ser subdivididas em subseções menores, cada uma com escopo delimitado." |

---

## 6. Observações adicionais

1. **Consistência com a seção de Resultados.** A seção de Resultados (`resultados.tex`) refere-se a "35 estudos aprovados" em diversos pontos. Qualquer alteração na contagem de estudos no Método deve ser propagada para a seção de Resultados e para o Resumo.

2. **Escopo de `/atualizar-artigo`.** As inconsistências numéricas internas (achados #1 e #2) devem ser investigadas com `/atualizar-artigo` para determinar quais valores correspondem aos dados reais do pipeline antes de efetuar correções.

3. **Seção de Introdução.** A seção de Introdução (`sec:introducao`) ainda está marcada como `% TODO`. Quando redigida, deverá antecipar as contribuições metodológicas descritas no Método (LLM, IC, 5 bases), cuja presença constitui ponto forte do artigo.

4. **Potencial de publicação separada.** O índice de citação cruzada (IC) e a classificação assistida por LLM são contribuições metodológicas suficientemente originais para merecer discussão mais aprofundada em nota metodológica ou apêndice, caso o espaço do artigo permita.
