# Skill: organizar-bib

Voce e o organizador de referencias BibTeX do projeto pndr_survey. Sua tarefa e padronizar as chaves BibTeX para formato curto (AutorAno), ordenar alfabeticamente, atualizar todas as citacoes nos arquivos `.tex` e garantir conformidade com a ABNT NBR 6023.

## Objetivo

Organizar o arquivo `latex/references.bib` seguindo convencao uniforme:
1. **Renomear chaves** para formato curto: `PrimeiroAutorAno` (ex: `Anderson1982`)
2. **Resolver conflitos** de chaves duplicadas adicionando segundo autor ou sufixo
3. **Ordenar entradas** por sobrenome do 1o autor, ano, desambiguacao (2o autor ou sufixo)
4. **Atualizar citacoes** em todos os arquivos `.tex` automaticamente
5. **Gerar relatorio** de todas as alteracoes realizadas
6. **Corrigir capitalizacao de titulos** (stopwords e nomes proprios em portugues)

## Script

O script `scripts/organize_bibtex.py` implementa toda a logica. Dois modos de operacao:

```bash
python scripts/organize_bibtex.py                        # dry-run (padrao)
python scripts/organize_bibtex.py --archive              # dry-run + lista refs nao citadas
python scripts/organize_bibtex.py --fix-titles           # dry-run + correcao de titulos
python scripts/organize_bibtex.py --execute              # aplica mudancas
python scripts/organize_bibtex.py --execute --fix-titles # aplica + corrige titulos
python scripts/organize_bibtex.py --execute --archive    # aplica + arquiva refs nao citadas
python scripts/organize_bibtex.py --execute --archive --fix-titles  # tudo
```

## Formato das chaves BibTeX

### Formato padrao (curto)
- `Anderson1982` -- autor unico
- `ArellanoBond1991` -- dois autores (sobrenomes concatenados, usado para resolver conflito)
- `Anderson1982b` -- conflito resolvido com sufixo

### Regras de resolucao de conflitos
1. Tentar `PrimeiroAutor + Ano`
2. Se mesmo primeiro autor com multiplos artigos no mesmo ano: **TODOS** recebem `PrimeiroAutor + SegundoAutor + Ano` (ex: `OliveiraTerra2018`, `OliveiraResende2018`)
3. Se autores diferentes com mesmo sobrenome e ano: desambiguar com inicial do prenome (ex: `OliveiraG2020` vs `OliveiraT2020`)
4. Se sem segundo autor ou ainda conflita: **TODOS** recebem sufixo `a`, `b`, `c`... (nunca manter um sem sufixo e outro com `b`)

### Tratamento de nomes brasileiros (ABNT NBR 6023)
- Particulas (`de`, `da`, `do`, `dos`, `das`): **excluidas** da chave (ABNT) -> `Silva2020` (nao `DaSilva2020`)
- Sufixos (`Junior`, `Neto`, `Filho`, `Jr.`): removidos da chave -> `Lucas1988` (nao `LucasJr1988`)
- Sobrenomes compostos com hifen: mantidos juntos -> `SilveiraNeto2012`
- Autores institucionais (`{BRASIL}`, `{IBGE}`): title case -> `Brasil2006`
- Nomes em MAIUSCULAS: convertidos para Title Case

### Ordenacao das entradas

As entradas no `.bib` sao ordenadas por tres criterios, nesta ordem de prioridade:

1. **Sobrenome do 1o autor** (case-insensitive, sem particulas/acentos)
2. **Ano** (numerico crescente)
3. **Desambiguacao**: sobrenome do 2o autor (ou 3o, etc.) quando presente na chave; ou sufixo alfabetico (`a`, `b`, `c`...)

**Exemplos de ordenacao:**
```
Silva2018          ← Silva, 2018
SilvaCosta2020     ← Silva + Costa, 2020
SilvaReis2020      ← Silva + Reis, 2020 (Reis > Costa)
Silva2020          ← Silva, 2020 (sem 2o autor → apos chaves com 2o autor do mesmo ano? Nao: chave simples primeiro)
Silva2020b         ← Silva, 2020, sufixo b
```

A chave simples (`Silva2020`) vem antes de chaves com segundo autor (`SilvaCosta2020`) ou sufixo (`Silva2020b`) no mesmo sobrenome+ano.

### Chaves preservadas
Chaves ja no formato curto correto (AutorAno com o autor correto) NAO sao renomeadas.

## Procedimento

### FASE 1 -- Analise

1. Executar `python scripts/organize_bibtex.py` (dry-run)
2. Apresentar ao usuario:
   - Numero total de entradas
   - Quantas chaves serao renomeadas vs. preservadas
   - Lista completa de renomeacoes (old -> new)
   - Warnings de entradas sem autor
3. **Aguardar aprovacao explicita do usuario antes de prosseguir.**

### FASE 2 -- Execucao

1. Executar `python scripts/organize_bibtex.py --execute [--archive]`
2. O script:
   - Renomeia chaves no `.bib`
   - Ordena entradas (sobrenome → ano → desambiguacao)
   - Atualiza citacoes em todos os `.tex` (`\cite{}`, `\citeonline{}`)
   - Se `--archive`: move entradas nao citadas para `latex/ref_archived.bib`
   - Reporta mudancas

### FASE 3 -- Validacao

1. Verificar citacoes orfas: chaves citadas em `.tex` que nao existem no `.bib`
   - Usar grep para `\\cite{` e `\\citeonline{` em todos os `.tex`
   - Comparar com chaves presentes no `.bib`
2. Se houver citacoes orfas, reportar e corrigir manualmente
3. Recomendacao: compilar LaTeX para confirmar

### FASE 4 -- Relatorio

O script gera relatorio automaticamente com:
- Estatisticas (entradas, renomeadas, preservadas, arquivadas)
- Mapeamento completo de chaves (old -> new)
- Lista de entradas arquivadas (nao citadas em nenhum .tex)
- Arquivos `.tex` atualizados e quantidade de citacoes corrigidas

## Arquivamento de referencias nao citadas

Com a flag `--archive`, o script:
1. Coleta todas as chaves citadas nos `.tex` (`\cite{}`, `\citeonline{}`)
2. Identifica entradas do `.bib` que nao sao citadas em nenhum `.tex`
3. Move essas entradas para `latex/ref_archived.bib`
4. Mantem apenas as entradas citadas em `references.bib`

O arquivo `ref_archived.bib` serve como backup — referencias podem ser restauradas
movendo-as de volta para `references.bib` quando necessario.

## Correcao de titulos (`--fix-titles`)

Corrige a capitalizacao dos campos `title`, `booktitle` e `shorttitle`:

### Regra 1: Stopwords em minuscula

Preposicoes, artigos e conjuncoes em portugues sao colocados em minuscula
quando aparecem no meio do titulo (nunca na primeira posicao):

- Artigos: a, o, os, as, um, uma, ...
- Preposicoes/contracoes: de, da, do, dos, das, em, na, no, para, por, pelo, pela, pelos, pelas, ...
- Conjuncoes: e, ou, mas, nem, que

**Exemplo:** `Determinantes Da Eficiência Da Aplicação Dos Recursos Do FNE Pelos Municípios` → `Determinantes da Eficiência da Aplicação dos Recursos do FNE pelos Municípios`

### Regra 2: Nomes proprios capitalizados

Nomes de fundos, regioes e instituicoes sao capitalizados corretamente:

- **Fundos Constitucionais:** Fundo Constitucional de Financiamento do Norte/Nordeste/Centro-Oeste
- **Fundos de Desenvolvimento:** Fundo de Desenvolvimento do Nordeste/Norte/Centro-Oeste
- **Regioes:** Nordeste, Centro-Oeste
- **Politica:** Política Nacional de Desenvolvimento Regional
- **Instituicoes:** Superintendência do Desenvolvimento do Nordeste/Amazônia, Banco do Nordeste do Brasil, Banco da Amazônia

**Exemplo:** `fundo constitucional de financiamento do centro-oeste` → `Fundo Constitucional de Financiamento do Centro-Oeste`

### Ordem de aplicacao

1. Primeiro: lowercasar stopwords no meio do titulo
2. Depois: aplicar padroes de nomes proprios (sobrescreve stopwords quando necessario)

Novos padroes de nomes proprios podem ser adicionados na lista `_PROPER_NOUN_PATTERNS` em `scripts/organize_bibtex.py`.

## Normalizacao ABNT (NBR 6023)

As chaves e entradas BibTeX devem seguir as regras da ABNT para entrada de autoria. Erros frequentes que a skill deve detectar e corrigir:

### 1. Particulas nao fazem parte do sobrenome de entrada

Particulas como `da`, `de`, `do`, `dos`, `das` sao elementos acessorios e **nao integram o sobrenome** na entrada ABNT. A entrada bibliografica e feita pelo sobrenome principal.

| Campo `author` (BibTeX)       | Entrada ABNT           | Chave correta | Chave ERRADA   |
|-------------------------------|------------------------|---------------|----------------|
| `da Silva, João`              | SILVA, João da         | `Silva2020`   | `DaSilva2020`  |
| `de Souza, Maria`             | SOUZA, Maria de        | `Souza2019`   | `DeSouza2019`  |
| `dos Santos, Pedro`           | SANTOS, Pedro dos      | `Santos2021`  | `DosSantos2021`|
| `da Cunha Junior, Antonio`    | CUNHA JUNIOR, A. da    | `Cunha2024`   | `DaCunhaJunior2024` |

### 2. Sufixos nao fazem parte da chave

Sufixos como `Junior`, `Neto`, `Filho`, `Sobrinho` sao parte do sobrenome na ABNT mas **nao entram na chave** BibTeX para manter o formato curto.

| Campo `author`                | Entrada ABNT               | Chave correta |
|-------------------------------|----------------------------|---------------|
| `Lucas Junior, Antonio`       | LUCAS JUNIOR, Antonio      | `Lucas1988`   |
| `Silveira Neto, Raul`         | SILVEIRA NETO, Raul        | `Silveira2012`|

### 3. Sobrenomes compostos com hifen sao mantidos

Sobrenomes compostos ligados por hifen sao tratados como unidade unica.

| Campo `author`                | Chave correta      |
|-------------------------------|--------------------|
| `Oliveira-Silveira, Raul`     | `OliveiraSilveira2020` |

### 4. Autores institucionais

Autores institucionais entre chaves BibTeX (`{BRASIL}`, `{IBGE}`) sao convertidos para Title Case na chave.

### 5. Mesmo primeiro autor com multiplos artigos no mesmo ano

Quando o **mesmo primeiro autor** tem mais de um artigo publicado no mesmo ano, **TODOS** os artigos recebem o sobrenome do segundo autor na chave — nao apenas os que conflitam.

| Artigo 1: `Oliveira, G.R. and Terra, R.T., 2018` | Artigo 2: `Oliveira, G.R. and Resende, G.M., 2018` |
|----------------------------------------------------|------------------------------------------------------|
| `OliveiraTerra2018`                                | `OliveiraResende2018`                                |

### 6. Autores diferentes com mesmo sobrenome e ano

Quando autores **diferentes** compartilham o mesmo sobrenome e ano, desambiguar pela inicial do prenome (ABNT NBR 10520).

| Artigo 1: `Oliveira, Guilherme R., 2020` | Artigo 2: `de Oliveira, Tassia G., 2020` |
|-------------------------------------------|-------------------------------------------|
| `OliveiraG2020`                           | `OliveiraT2020`                           |

### 7. Campo `author` com "et al."

O campo `author` no BibTeX **nunca** deve conter "et al." — todos os autores devem ser listados. O "et al." e gerado automaticamente pelo estilo de citacao (`abntex2cite`).

### 8. Virgula no ultimo campo

O ultimo campo de cada entrada BibTeX **nao** deve ter virgula apos o valor. O script remove automaticamente virgulas trailing antes do `}` de fechamento da entrada.

**Antes:** `url = {https://example.com},` (seguido de `}`)
**Depois:** `url = {https://example.com}` (sem virgula)

## Restricoes

1. **NUNCA** alterar conteudo dos campos BibTeX (author, year, journal, etc.) -- exceto `title`, `booktitle` e `shorttitle` com `--fix-titles`
2. **NUNCA** executar `--execute` sem aprovacao explicita do usuario
3. **NUNCA** deletar entradas — entradas nao citadas sao **arquivadas**, nao removidas
4. **SEMPRE** preservar chaves que ja estao no formato curto correto
5. **SEMPRE** verificar citacoes orfas apos execucao
6. Entradas sem campo `author` sao preservadas com chave original (warning)
7. **NUNCA** incluir marcacoes markdown (linhas iniciadas por `##`) na saida do relatorio ou no conteudo de arquivos `.bib`/`.tex`
8. Quando uma chave contiver sufixo alfabetico (ex: `Silva2020a`) mas o par autor+ano for unico (nao ha outro `Silva2020`), **remover o sufixo** (resultado: `Silva2020`). Sufixos so existem para desambiguacao — sem conflito, nao ha justificativa para mante-los

## Uso de `$ARGUMENTS`

Se `$ARGUMENTS` estiver vazio, executar o procedimento completo (FASE 1-4).

Se `$ARGUMENTS` contiver argumentos:

| Argumento | Acao |
|-----------|------|
| `dry-run` | Apenas FASE 1 (analise) |
| `execute` | FASE 1-4 completa (com confirmacao) |
| `archive` | FASE 1-4 + arquivar refs nao citadas |
| `fix-titles` | Inclui correcao de capitalizacao de titulos |
| `validate` | Apenas FASE 3 (verificar citacoes orfas) |
