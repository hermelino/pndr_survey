# Relatório: Cruzamento Método x Resultados

Data: 2026-03-04

## Objetivo

Identificar quais dos 35 estudos aprovados (listados na tabela IC do Método) estão ausentes da seção Resultados, e quais estudos aparecem nos quadros de Resultados mas não constam na tabela IC.

---

## 1. Estudos na tabela IC (Método) ausentes do Resultados descomentado

### Grupo A: Presentes apenas na seção 4.2 comentada (FC - Mercado de Trabalho)

| # IC | Chave BibTeX | Descrição | Correção |
|------|-------------|-----------|
| 1 | `Silva2009` | Primeiro estudo PSM sobre emprego FC | ref ok |
| 10 | `Soares2017` | PSM sobre emprego FNE | |
| 11 | `Ribeiro2024` | Painel dinâmico FNE emprego por setor ||
| 14 | `Junior2024` | Função dose-resposta FNE emprego ||
| 28 | `Oliveira2017c` | Referenciado na seção comentada ||

### Grupo B: Completamente ausentes do Resultados

| # IC | Chave BibTeX | Pipeline ID | Correção |
|------|-------------|-------------|
| 16 | `Borges2025` | scopus-2025-borges-rodrigues | rejeitado: fora de escopo |
| 19 | `Resende2011a` | econpapers-2011-resende | Duplicado com scopus-2014-resende.pdf |
| 30 | `Filho2024b` | anpec-2024-filho-alves |
| 31 | `Veloso2024` | anpec-2024-veloso-costa-carneiro |
| 32 | `Lazaretti2025` | anpec-2025-lazaretti-davanzo-neves |
| 33 | `Shirasu2025a` | anpec-2025-shirasu |
| 35 | `Veloso2025` | anpec-2025-veloso |

**Total: 12 dos 35 estudos do IC estão ausentes do Resultados descomentado** (5 na seção comentada + 7 ausentes por completo).

---

## 2. Estudos nos quadros de Resultados ausentes da tabela IC

Estudos que aparecem nos quadros survey (`survey_artigos_fc_pib.tex`, `survey_artigos_fd.tex`, `survey_artigos_if.tex`) mas não constam entre os 35 da tabela IC.

### Estudos genuinamente distintos (não são duplicatas de chaves IC)

| Chave no quadro | Quadro | Descrição |
|----------------|--------|-----------|
| `Resende2014b` | FC-PIB | Avaliação FNO, TD IPEA 1973 |
| `ResendeCravoPires2014` | FC-PIB | Avaliação FCO, TD IPEA |
| `CravoResende2015` | FC-PIB | Spatial FC, UNU-WIDER |
| `OliveiraLimaArriel2016` | FC-PIB | FCO espacial Goiás |
| `ResendeSilvaFilho2017` | FC-PIB | FNE por tipologia PNDR, Rev. Econ. NE |
| `SilvaFilhoetal2023` | FC-PIB | Financiamento público, TD NEREUS |
| `IrffiAraujoBastos2016` | FC-PIB | FNE quantílico, Fórum BNB |
| `Carneiro2018b` | FC-PIB | Eficiência FNE, ETENE |
| `CambotaViana2019` | FC-PIB | FNE painel dinâmico, Rev. Controle |
| `GoncalvesBragaGurgel2022` | FC-PIB | FNE EGC, Análise Econômica |
| `OliveiraSilveiraNeto2021` | FC-PIB | FNE RDD geográfico |
| `FerreiraIrffiCarneiro2024` | FD + IF | FDNE+IF painel espacial IDM |
| `Irffietal2025` | FD | Parques eólicos NE |

**Total: ~13 estudos nos quadros que não estão na tabela IC.**

### Chaves duplicadas (mesmo estudo, chave diferente da IC)

Estes estudos estão nos quadros com chave diferente da usada na tabela IC, mas referem-se ao mesmo trabalho:

| Chave IC | Chave no quadro | Confirmação |
|----------|----------------|-------------|
| `MendesResende2018` | `ResendeSilvaFilho2018` | Mesmo DOI |
| `deSantanaRibeiro2020a` | `Ribeiroetal2020` | Mesmo DOI |
| `Oliveira2018a` | `Oliveira2018` | Mesmo DOI (3 entradas no .bib) |
| `Carneiro2024` | `Carneiroetal2024a` | Mesmo estudo |
| `Monte2025a` | `MonteIrffiBastosCarneiro2025` | Mesmo DOI |
| `Bastos2024a` | `BrazBastosIrffi2024` | Mesmo pipeline ID |
| `Nascimento2017a` | `NascimentoHaddad2017` | Mesmo congresso |
| `Oliveira2005a` | `OliveiraDomingues2005` | Mesmo congresso |
| `Viana2014a` | `Linharesetal2014` | Mesma publicação |
| `Braz2023a` | `Braz2023` | Mesmo estudo |
| `Oliveira2020a` | `Oliveira2020` | Mesmo estudo |
| `Oliveira2021a` | `Oliveira2021` | Mesmo estudo |
| `Oliveira2026` | `gondim2025` | Mesmo estudo |

---

## 3. Problemas adicionais identificados

### 3.1. Entradas BibTeX triplicadas no references.bib

- `Oliveira2018a` = `Oliveira2018` = `OliveiraMenezesResende2018a` (3 entradas, mesmo DOI) Resolvido
- `deSantanaRibeiro2020a` = `deSantanaRibeiro2020` = `Ribeiroetal2020` (3 entradas, mesmo DOI) Resolvido

### 3.2. Erro de citação no texto de resultados.tex

No texto de `resultados.tex` (linhas 39 e 45), `\citeonline{Viana2014}` é usado tanto para o modelo threshold (que deveria ser `Viana2014a` / `Linharesetal2014`) quanto para o modelo dinâmico (que deveria ser `CambotaViana2019`). No references.bib, a chave `Viana2014` (sem sufixo "a") mapeia para `CambotaViana2019`. Resolvido

### 3.3. Estudo duplicado no quadro FC-PIB

`ResendeSilvaFilho2018` aparece como linha separada no quadro FC-PIB, mas é o mesmo estudo que `MendesResende2018` (mesmo DOI). O mesmo estudo consta duas vezes no quadro com chaves diferentes.

---

## 4. Resumo quantitativo

| Métrica | Qtd |
|---------|-----|
| Estudos na tabela IC (Método) | 35 |
| Estudos do IC presentes no Resultados descomentado | ~23 |
| Estudos do IC **ausentes** do Resultados | **12** |
| ...dos quais na seção 4.2 comentada | 5 |
| ...dos quais ausentes por completo | 7 |
| Estudos nos quadros de Resultados **ausentes** do IC | **~13** |
| Pares de chaves BibTeX duplicadas | ~13 |
| Entradas BibTeX triplicadas | 2 |

---

## 5. Ações sugeridas

1. **Descomentar seção 4.2** (FC - Mercado de Trabalho) para reincorporar os 5 estudos do Grupo A
2. **Escrever seções para os 7 estudos do Grupo B** que não aparecem em nenhum lugar do Resultados
3. **Consolidar chaves BibTeX**: eliminar duplicatas no references.bib e padronizar as chaves usadas nos quadros para corresponder às da tabela IC
4. **Corrigir citação `Viana2014`** no texto para distinguir os dois estudos (threshold vs. dinâmico)
5. **Verificar se os ~13 estudos extras nos quadros** pertencem ou não aos 35 aprovados (possível divergência entre a contagem oficial e o conteúdo dos quadros)
