# Citacoes da Tese: Candidatas a Inclusao Manual no PRISMA (pndr_survey)

Data: 2026-03-06

## Objetivo

Avaliar quais citacoes da secao de resultados da tese (Cap. 1, Secao 1.4 — `1-4-discussao-dos-resultados.tex`) nao foram capturadas pelo pipeline automatizado do pndr_survey e podem ser sugeridas para inclusao manual no diagrama PRISMA ("Records identified via other methods").

## Metodologia

1. Extraidas as 34 chaves de citacao unicas da secao de resultados da tese
2. Cada citacao foi verificada contra:
   - `data/2-papers/2-2-papers.json` (34 estudos aprovados + 85 rejeitados)
   - `data/1-records/processed/bib_records.json` (registros importados)
   - `data/1-records/processed/duplicates_removed.csv` (duplicatas removidas)
   - `latex/references.bib` (referencias do artigo)

## Resumo

| Categoria | Qtd | Descricao |
|-----------|-----|-----------|
| Aprovados no pipeline | 22 | Capturados e aprovados automaticamente |
| Duplicata removida (WP → artigo) | 1 | ResendeCravo2014 (TD IPEA 1969) |
| **Ausentes do pipeline** | **11** | **Candidatos a inclusao manual** |

---

## A. Estudos Ausentes do Pipeline (11 candidatos)

Estes estudos avaliam instrumentos da PNDR, estao citados na secao de resultados da tese e NAO foram encontrados em nenhuma etapa do pipeline automatizado do pndr_survey (nenhuma das 5 bases de busca retornou estes registros).

### 1. Resende (2014b) — FNO, Efeitos Fixos

- **Titulo:** Avaliacao dos Impactos Regionais do Fundo Constitucional de Financiamento do Norte entre 2004 e 2010
- **Autores:** Resende, Guilherme
- **Publicacao:** Texto para Discussao IPEA n. 1973
- **DOI:** —
- **URL:** http://repositorio.ipea.gov.br/handle/11058/3138
- **Chave tese:** `Resende2014b`
- **Chave pndr_survey (BibTeX):** `Resende2014b` (adicionado manualmente)
- **Nota:** Complemento regional (Norte) do TD 1918 (Resende2014a, aprovado). Pipeline capturou o TD 1918 (FNE) mas nao o TD 1973 (FNO).

Decisão: INCLUIR

### 2. Cravo e Resende (2015) — FCs, Painel Espacial SDM

- **Titulo:** The Brazilian Regional Development Funds and Economic Growth
- **Autores:** Cravo, Tulio A.; Resende, Guilherme Mendes
- **Publicacao:** UNU-WIDER Working Paper n. 118/2015
- **DOI:** 10.35188/UNU-WIDER/2015/007-2
- **URL:** https://doi.org/10.35188/UNU-WIDER/2015/007-2
- **Chave tese:** `CravoResende2015`
- **Chave pndr_survey (BibTeX):** `Cravo2015` (adicionado manualmente)
- **Nota:** Versao internacional com modelo SDM. Distinto do TD IPEA 1969 (ResendeCravo2014, modelo EF nao-espacial) que foi capturado e removido como duplicata.

Decisão: REJEITADO

### 3. Oliveira, Lima e Arriel (2016) — FCO, Painel Espacial SAR

- **Titulo:** Fundo Constitucional de Financiamento do Centro-Oeste (FCO) em Goias: uma Aplicacao Econometrica-Espacial
- **Autores:** Oliveira, Guilherme Resende; Lima, Alex Felipe Rodrigues; Arriel, Marcos Fernando
- **Publicacao:** Revista Brasileira de Economia de Empresas, v. 16, n. 1
- **DOI:** —
- **URL:** https://portalrevistas.ucb.br/index.php/rbee/article/view/6832
- **Chave tese:** `Oliveira2016`
- **Chave pndr_survey (BibTeX):** `Oliveira2016` (adicionado manualmente)
- **Nota:** Avaliacao espacial do FCO especifica para Goias. Nao confundir com Oliveira2015 (econpapers, aprovado) que trata de concentracao espacial.

Decisão: REJEITAR Oliveira2015 e INCLUIR Oliveira2016

### 4. Resende, Silva e Filho (2017) — FNE, Espacial por Tipologia PNDR

- **Titulo:** Avaliacao Economica do Fundo Constitucional de Financiamento do Nordeste (FNE): uma Analise Espacial por Tipologia da PNDR entre 1999 e 2011
- **Autores:** Resende, Guilherme Mendes; Silva, Danilo Firmino Costa; Silva Filho, Luis Abel
- **Publicacao:** Revista Economica do Nordeste, v. 48, n. 1, p. 9-29
- **DOI:** 10.61673/ren.2017.701
- **URL:** https://doi.org/10.61673/ren.2017.701
- **Chave tese:** `Resende2017`
- **Chave pndr_survey (BibTeX):** `Resende2017` (adicionado manualmente)
- **Nota:** Avalia somente o FNE por tipologia. Distinto de Resende2018 (aprovado) que avalia os tres fundos. O TD IPEA 2145 (versao WP do Resende2018) foi capturado e removido como duplicata.

Decisão: INCLUIR

### 5. Irffi, Araujo e Bastos (2016) — FNE, Regressao Quantilica

- **Titulo:** Efeitos Heterogeneos do Fundo Constitucional de Financiamento do Nordeste na Regiao do Semiarido
- **Autores:** Irffi, Guilherme; Araujo, Jair Andrade da Silva; Bastos, Fabricio de Souza
- **Publicacao:** Forum Banco do Nordeste de Desenvolvimento, v. 22
- **DOI:** —
- **URL:** —
- **Chave tese:** `Irffi2016`
- **Chave pndr_survey (BibTeX):** `Irffi2016` (adicionado manualmente)
- **Nota:** Publicacao interna do BNB, provavelmente fora do alcance das bases consultadas.

Decisão: INCLUIR

### 6. Carneiro (2018) — FNE, Analise de Eficiencia DEA

- **Titulo:** Determinantes da Eficiencia da Aplicacao dos Recursos do FNE pelos Municipios Beneficiados
- **Autores:** Carneiro, Diego
- **Publicacao:** Artigos ETENE, Banco do Nordeste do Brasil
- **DOI:** —
- **URL:** https://www.bnb.gov.br/s482-dspace/handle/123456789/676
- **Chave tese:** `Carneiro2018b`
- **Chave pndr_survey (BibTeX):** `Carneiro2018` (adicionado manualmente)
- **Nota:** Publicacao institucional do BNB (serie ETENE), fora do alcance das bases academicas consultadas.

Decisão: INCLUIR

### 7. Cambota e Viana (2019) — FNE, Painel Dinamico

- **Titulo:** O Impacto do Fundo Constitucional de Financiamento do Nordeste (FNE) no Crescimento dos Municipios: uma Aplicacao de Painel Dinamico
- **Autores:** Cambota, Jacqueline Nogueira; Viana, Leonardo Ferreira Gomes
- **Publicacao:** Revista Controle - Doutrina e Artigos, v. 17, n. 1, p. 20-46
- **DOI:** 10.32586/rcda.v17i1.472
- **URL:** https://doi.org/10.32586/rcda.v17i1.472
- **Chave tese:** `Cambota2019`
- **Chave pndr_survey (BibTeX):** `Cambota2019` (adicionado manualmente)
- **Nota:** Publicacao do TCE-CE, periodico nao indexado nas bases consultadas.

Decisão: INCLUIR

### 8. Goncalves, Braga e Gurgel (2022) — FNE, Equilibrio Geral

- **Titulo:** Avaliacao dos Impactos do Fundo Constitucional de Financiamento do Nordeste (FNE): uma Abordagem de Equilibrio Geral
- **Autores:** Goncalves, Marcelo Ferreira; Braga, Marcelo Jose; Gurgel, Angelo Costa
- **Publicacao:** Analise Economica, v. 40, n. 81
- **DOI:** 10.22456/2176-5456.92093
- **URL:** https://doi.org/10.22456/2176-5456.92093
- **Chave tese:** `Goncalves2022`
- **Chave pndr_survey (BibTeX):** `Goncalves2022` (adicionado manualmente)
- **Nota:** Periodico da UFRGS. Possivelmente nao retornado pelas queries de busca usadas no pipeline.

Decisão: INCLUIR

### 9. Rieger, Lima e Rodrigues (2020) — FNE, Emprego Formal, Painel Dinamico

- **Titulo:** O Efeito do FNE no Crescimento do Emprego Formal da Regiao Nordeste
- **Autores:** Rieger, Roberto Arruda; Lima, Regina Marta Nepomuceno; Rodrigues, Clauber Teixeira
- **Publicacao:** Revista Economica do Nordeste, v. 51, n. 2, p. 155-168
- **DOI:** 10.61673/ren.2020.1106
- **URL:** https://doi.org/10.61673/ren.2020.1106
- **Chave tese:** `Rieger2020`
- **Chave pndr_survey (BibTeX):** `Rieger2020` (adicionado manualmente)
- **Nota:** Revista Economica do Nordeste (BNB). Presente no SciELO mas nao retornado pelas queries.

Decisão: INCLUIR

### 10. Daniel e Braga (2020) — FNO, DID, Emprego por Porte

- **Titulo:** Impactos do Fundo Constitucional de Financiamento do Norte: evidencias do estimador de diferencas em diferencas
- **Autores:** Daniel, Lindomar Pegorini; Braga, Marcelo Jose
- **Publicacao:** Planejamento e Politicas Publicas (PPP/IPEA), n. 55, p. 97-146
- **DOI:** 10.38116/ppp55art4
- **URL:** https://www.ipea.gov.br/ppp/index.php/PPP/article/view/945
- **Chave tese:** `DanielBraga2020b`
- **Chave pndr_survey (BibTeX):** `Daniel2020` (adicionado manualmente)
- **Nota:** Periodico do IPEA. Unico estudo DID sobre o FNO na literatura.

Decisão: INCLUIR

### 11. Silva Filho, Azzoni e Chagas (2023) — FNE/FNO/FCO, Painel Espacial

- **Titulo:** Impactos do Financiamento Publico sobre a Economia dos Municipios Beneficiados
- **Autores:** da Silva Filho, Luis Abel; Azzoni, Carlos Roberto; Chagas, Andre Luis Squarize
- **Publicacao:** TD NEREUS n. 03-2023, USP
- **DOI:** —
- **URL:** https://www.usp.br/nereus/wp-content/uploads/TD_NEREUS_03_2023.pdf
- **Chave tese:** `Silva2023`
- **Chave pndr_survey (BibTeX):** `Silva2023` (adicionado manualmente)
- **Nota:** Working paper do NEREUS/USP, nao indexado nas bases consultadas.

Decisão: INCLUIR

---

## B. Estudo Capturado mas Removido como Duplicata (1)

### ResendeCravo2014 (TD IPEA 1969) — FCO, Efeitos Fixos

- **Titulo:** Avaliacao dos Impactos Economicos do Fundo Constitucional de Financiamento do Centro-Oeste (FCO) entre 2004 e 2010
- **Autores:** Resende, Guilherme Mendes; Cravo, Tulio Antonio; Pires, Murilo Jose de Souza
- **Publicacao:** Texto para Discussao IPEA n. 1969 (2014)
- **Pipeline:** Capturado via EconPapers → marcado como `is_duplicate: true` → `motivo_exclusao: "duplicata de versao publicada"` → removido em favor de Resende2018
- **Chave tese:** `ResendeCravo2014a`
- **Chave pndr_survey:** `ResendeCravo2014`
- **Nota:** O TD 1969 usa modelo EF nao-espacial para o FCO, enquanto Resende2018 (aprovado) usa modelo SDM espacial para os tres fundos por tipologia. A analise nao-espacial especifica do FCO nao esta representada no corpus aprovado. Considerar se a deduplicacao foi adequada.

---

## C. Estudos da Tese JA Aprovados no Pipeline (22)

| # | Chave tese | Chave pndr_survey | PDF aprovado |
|---|-----------|-------------------|--------------|
| 1 | Resende2014a | Resende2014a | econpapers-2014-resende.pdf |
| 2 | Resende2014c | Resende2014c | scopus-2014-resende.pdf |
| 3 | Resende2018 | Resende2018 | scopus-2018-resende-silva-filho.pdf |
| 4 | LinharesSoares2014b | Linhares2014 | econpapers-2014-viana-goncalves-linhares.pdf |
| 5 | Olivera2026 | Oliveira2026 | manual-2026-oliveira-carneiro-souza.pdf |
| 6 | Nascimento2017 | Nascimento2017 | anpec-2017-nascimento-haddad.pdf |
| 7 | Ribeiro2020 | Ribeiro2020 | scopus-2020-ribeiro-caldas-souza.pdf |
| 8 | OliveiraSilveira2020 | Oliveira2020 | anpec-2020-oliveira-neto.pdf |
| 9 | CarneiroVeloso2024 | CarneiroVeloso2024 | anpec-2024-carneiro-veloso-ferreira.pdf |
| 10 | Monte2025 | Monte2025 | scopus-2025-monte-irffi-bastos.pdf |
| 11 | Silva2009 | SilvaResende2009 | scopus-2009-silva-resende-neto.pdf |
| 12 | Soares2009 | Soares2009 / Soares2017 | capes-2017-soares-sousa-neto.pdf |
| 13 | OliveiraMenezes2018 | OliveiraTerra2018 | scopus-2018-oliveira-terra-resende.pdf |
| 14 | OliveiraResende2018 | OliveiraResende2018 | via anpec-2017-oliveira-resende-goncalves.pdf |
| 15 | Cunha2024 | Cunha2024 | scopus-2024-cunha-soares.pdf |
| 16 | Oliveira2021 | Oliveira2021 | anpec-2021-oliveira-neto.pdf |
| 17 | Braz2024 | Braz2024 | anpec-2024-braz-bastos-irffi.pdf |
| 18 | CarneiroCosta2024 | CarneiroCosta2024 | via Costa2024 / scopus-2024-costa-carneiro-irffi.pdf |
| 19 | IrffiCosta2025b | Irffi2025 | via anpec-2025-veloso.pdf |
| 20 | Garsous2017 | Garsous2017 | scopus-2017-garsous-novoa-velasco.pdf |
| 21 | Braz2023 | Braz2023 | anpec-2023-braz-irffi.pdf |
| 22 | Ferreira2024* | Ferreira2024 | * ver nota abaixo |

*Nota sobre Ferreira2024: Esta entrada existe no BibTeX do pndr_survey como referencia mas NAO corresponde a nenhum dos 34 estudos aprovados no pipeline. O estudo ("A PNDR e o Desenvolvimento Economico do Nordeste: uma Analise do FDNE e dos Incentivos Fiscais da SUDENE", Ferreira, Irffi, Carneiro, 2024) avalia FDNE e IF SUDENE com modelo SAC espacial sobre o IDM. Poderia ser reclassificado como candidato a inclusao manual (Secao A) — totalizando 12 candidatos.*

---

## D. Diagnostico: Por Que o Pipeline Nao Capturou Estes Estudos?

| Causa provavel | Estudos afetados |
|----------------|------------------|
| **Periodico nao indexado nas 5 bases** | Irffi2016 (Forum BNB), Carneiro2018 (ETENE/BNB), Cambota2019 (Rev. Controle/TCE-CE) |
| **Working paper/TD nao indexado** | CravoResende2015 (UNU-WIDER), Silva2023 (NEREUS/USP) |
| **Indexado mas nao retornado pelas queries** | Resende2014b (IPEA/EconPapers), Resende2017 (REN), Rieger2020 (REN), Goncalves2022 (Analise Economica), Daniel2020 (PPP/IPEA) |
| **Estudo nao publicado / WP recente** | Ferreira2024 (ANPEC WP) |
| **Apresentado em evento nao coberto** | Oliveira2016 (RBEE/UCB) |

---

## E. Recomendacao para o Diagrama PRISMA

No PRISMA 2020, estudos identificados por fontes externas ao protocolo de busca sistematica sao reportados no fluxo esquerdo: "Identification of studies via other methods" → "Records identified from: Citation searching / Other sources".

**Acao sugerida:**
1. Incluir os 11 (ou 12) estudos ausentes na caixa "Records identified from other sources" do PRISMA
2. Classificar a fonte como "revisao sistematica anterior (tese)"
3. Submeter cada estudo ao mesmo criterio de triagem (LLM stages 1-3) aplicado aos demais
4. Atualizar `2-2-papers.json` com os registros correspondentes e `triagem: "APROVADO"` apos verificacao
5. Revisar a deduplicacao de ResendeCravo2014 (TD IPEA 1969) — a analise nao-espacial do FCO pode conter informacoes unicas nao presentes em Resende2018

**Impacto no PRISMA:**
- Registros identificados via outras fontes: +11 (ou +12)
- Potencial aumento no corpus aprovado: ate +11 estudos adicionais (de 34 para ate 45)
- Total de estudos unicos da tese + pipeline: ate 45 (37 tese + 12 novos do pipeline - 4 sobreposicao parcial)
