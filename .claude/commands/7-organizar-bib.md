# Skill: organizar-bib

Voce e o organizador de referencias BibTeX do projeto pndr_survey. Sua tarefa e padronizar as chaves BibTeX para formato curto (AutorAno), ordenar alfabeticamente e atualizar todas as citacoes nos arquivos `.tex`.

## Objetivo

Organizar o arquivo `latex/references.bib` seguindo convencao uniforme:
1. **Renomear chaves** para formato curto: `PrimeiroAutorAno` (ex: `Anderson1982`)
2. **Resolver conflitos** de chaves duplicadas adicionando segundo autor ou sufixo
3. **Ordenar alfabeticamente** todas as entradas por chave
4. **Atualizar citacoes** em todos os arquivos `.tex` automaticamente
5. **Gerar relatorio** de todas as alteracoes realizadas

## Script

O script `scripts/organize_bibtex.py` implementa toda a logica. Dois modos de operacao:

```bash
python scripts/organize_bibtex.py                        # dry-run (padrao)
python scripts/organize_bibtex.py --archive              # dry-run + lista refs nao citadas
python scripts/organize_bibtex.py --execute              # aplica mudancas
python scripts/organize_bibtex.py --execute --archive    # aplica + arquiva refs nao citadas
```

## Formato das chaves BibTeX

### Formato padrao (curto)
- `Anderson1982` -- autor unico
- `ArellanoBond1991` -- dois autores (sobrenomes concatenados, usado para resolver conflito)
- `Anderson1982b` -- conflito resolvido com sufixo

### Regras de resolucao de conflitos
1. Tentar `PrimeiroAutor + Ano`
2. Se conflito: `PrimeiroAutor + SegundoAutor + Ano`
3. Se sem segundo autor ou ainda conflita: sufixo `b`, `c`, `d`...

### Tratamento de nomes brasileiros
- Particulas (`de`, `da`, `dos`): incluidas na chave -> `deSouza2020`
- Sufixos (`Junior`, `Neto`, `Filho`, `Jr.`): removidos da chave -> `Lucas1988` (nao `LucasJr1988`)
- Sobrenomes compostos: sem espaco -> `SilveiraNeto2012`
- Autores institucionais (`{BRASIL}`, `{IBGE}`): title case -> `Brasil2006`
- Nomes em MAIUSCULAS: convertidos para Title Case

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
   - Ordena entradas alfabeticamente
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

## Restricoes

1. **NUNCA** alterar conteudo dos campos BibTeX (author, title, year, etc.) -- apenas a chave
2. **NUNCA** executar `--execute` sem aprovacao explicita do usuario
3. **NUNCA** deletar entradas — entradas nao citadas sao **arquivadas**, nao removidas
4. **SEMPRE** preservar chaves que ja estao no formato curto correto
5. **SEMPRE** verificar citacoes orfas apos execucao
6. Entradas sem campo `author` sao preservadas com chave original (warning)

## Uso de `$ARGUMENTS`

Se `$ARGUMENTS` estiver vazio, executar o procedimento completo (FASE 1-4).

Se `$ARGUMENTS` contiver argumentos:

| Argumento | Acao |
|-----------|------|
| `dry-run` | Apenas FASE 1 (analise) |
| `execute` | FASE 1-4 completa (com confirmacao) |
| `archive` | FASE 1-4 + arquivar refs nao citadas |
| `validate` | Apenas FASE 3 (verificar citacoes orfas) |
