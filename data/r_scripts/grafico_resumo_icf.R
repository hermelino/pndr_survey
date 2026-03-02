# =============================================================================
# GRÁFICO RESUMO INCENTIVOS FISCAIS (ICF)
# =============================================================================

rm(list=ls())
gc()

# Pacotes necessários
if (!require("pacman")) install.packages("pacman")
pacman::p_load(tidyverse, ggplot2, RColorBrewer, scales, readxl)

# Carregar funções de output
source("./output_helpers.R")

# Carregar dados necessários
resumo_icf <- readxl::read_excel("../output/data/classif_incent_fiscais.xlsx")

# Carregar dados para calcular per capita
painel_icf <- readr::read_rds("../output/data/painel_icf.rds")
populacao <- readr::read_rds("../output/data/populacao_fc.rds")
tipologia2007 <- readxl::read_excel("C:/OneDrive/DATABASES/MUNICÍPIOS/tipologia_2007.xlsx", sheet="Table 1") %>%
  select(1,6) %>% rename_with(~c("id_municipio","tipologia2007")) %>%
  mutate(id_municipio = as.numeric(id_municipio))

# =============================================================================
# PREPARAÇÃO DOS DADOS PARA O GRÁFICO
# =============================================================================

# Preparar os dados para o gráfico
dados_grafico <- resumo_icf %>%
  # Converter para formato longo
  pivot_longer(cols = c(SUDAM, SUDENE), 
               names_to = "Superintendencia", 
               values_to = "Quantidade") %>%
  # Remover valores NA e valores zero/vazios
  filter(!is.na(Quantidade) & Quantidade > 0) %>%
  # Reordenar superintendências para SUDENE aparecer primeiro
  mutate(Superintendencia = factor(Superintendencia, levels = c("SUDENE", "SUDAM")),
         # Garantir que as tipologias estejam na ordem desejada e adicionar quebras de linha
         tipologia2007 = factor(tipologia2007, 
                                levels = c("Alta Renda", "Baixa Renda", "Dinâmica", "Estagnada")),
         # Criar labels com quebras de linha para as tipologias
         tipologia_quebrada = case_when(
           tipologia2007 == "Alta Renda" ~ "Alta\nRenda",
           tipologia2007 == "Baixa Renda" ~ "Baixa\nRenda",
           tipologia2007 == "Dinâmica" ~ "Dinâmica",
           tipologia2007 == "Estagnada" ~ "Estagnada"
         ),
         tipologia_quebrada = factor(tipologia_quebrada, 
                                     levels = c("Alta\nRenda", "Baixa\nRenda", "Dinâmica", "Estagnada")),
         # Ordenar setores conforme especificação e adicionar quebras de linha
         ordem_setor = case_when(
           SETOR2 == "Indústria de transformação" ~ 1,
           SETOR2 == "Infraestrutura" ~ 2,
           SETOR2 == "Indústria extrativa de minerais metálicos" ~ 3,
           SETOR2 == "Turismo" ~ 4,
           SETOR2 == "Agroindústria" ~ 5,
           SETOR2 == "Agricultura irrigada" ~ 6
         ),
         SETOR2 = reorder(SETOR2, ordem_setor),
         # Criar labels com quebras de linha para a legenda
         SETOR2_quebrado = case_when(
           SETOR2 == "Indústria de transformação" ~ "Indústria de\ntransformação",
           SETOR2 == "Infraestrutura" ~ "Infraestrutura",
           SETOR2 == "Indústria extrativa de minerais metálicos" ~ "Ind. extrativa de\nminerais metálicos",
           SETOR2 == "Turismo" ~ "Turismo",
           SETOR2 == "Agroindústria" ~ "Agroindústria",
           SETOR2 == "Agricultura irrigada" ~ "Agricultura irrigada"
         ),
         SETOR2_quebrado = reorder(SETOR2_quebrado, ordem_setor))

# Calcular médias per capita por tipologia para ICF (multiplicar por 100.000 para melhor visualização)
medias_pc_icf <- painel_icf %>%
  left_join(tipologia2007, by = c("COD" = "id_municipio")) %>%
  left_join(populacao, by = c("COD" = "CD_MUN", "ANO" = "ano")) %>%
  filter(!is.na(tipologia2007) & !is.na(populacao) & populacao > 0) %>%
  mutate(
    icf_sudene_pc = (icf_sudene / populacao) * 100000,  # ICF por 100 mil habitantes
    icf_sudam_pc = (icf_sudam / populacao) * 100000     # ICF por 100 mil habitantes
  ) %>%
  group_by(tipologia2007) %>%
  summarise(
    icf_sudene_pc_media = mean(icf_sudene_pc, na.rm = TRUE),
    icf_sudam_pc_media = mean(icf_sudam_pc, na.rm = TRUE),
    .groups = 'drop'
  ) %>%
  mutate(
    tipologia_quebrada = case_when(
      tipologia2007 == "Alta Renda" ~ "Alta\nRenda",
      tipologia2007 == "Baixa Renda" ~ "Baixa\nRenda",
      tipologia2007 == "Dinâmica" ~ "Dinâmica",
      tipologia2007 == "Estagnada" ~ "Estagnada"
    ),
    tipologia_quebrada = factor(tipologia_quebrada, levels = c("Alta\nRenda", "Baixa\nRenda", "Dinâmica", "Estagnada"))
  )

# =============================================================================
# GERAÇÃO DO GRÁFICO
# =============================================================================

# Calcular escala para eixo secundário (per capita) 
max_pc_valor_icf <- max(c(medias_pc_icf$icf_sudene_pc_media, medias_pc_icf$icf_sudam_pc_media), na.rm = TRUE)
limite_pc_max_icf <- ceiling(max_pc_valor_icf * 1.5)  # Dar mais espaço para visualização

cat("Escala per capita ICF: 0 a", limite_pc_max_icf, "unidades per capita\n")

# Preparar dados da linha per capita por superintendência
linha_pc_sudene <- medias_pc_icf %>%
  select(tipologia_quebrada, icf_sudene_pc_media) %>%
  mutate(pc_scaled = (icf_sudene_pc_media / limite_pc_max_icf) * 1500) %>%
  mutate(Superintendencia = "SUDENE")

linha_pc_sudam <- medias_pc_icf %>%
  select(tipologia_quebrada, icf_sudam_pc_media) %>%
  mutate(pc_scaled = (icf_sudam_pc_media / limite_pc_max_icf) * 1500) %>%
  mutate(Superintendencia = "SUDAM")

linha_pc_todas_icf <- bind_rows(linha_pc_sudene, linha_pc_sudam) %>%
  mutate(Superintendencia = factor(Superintendencia, levels = c("SUDENE", "SUDAM")))

# Definir uma paleta de cores para os setores
cores_setores <- RColorBrewer::brewer.pal(n = length(unique(dados_grafico$SETOR2)), 
                                          name = "Set3")

# Criar o gráfico com fontes maiores para LaTeX e eixo secundário
grafico <- 
  ggplot(dados_grafico, aes(x = tipologia_quebrada, y = Quantidade, fill = SETOR2_quebrado)) +
  geom_col(position = "stack", width = 0.9) +
  # Adicionar linha vermelha per capita
  geom_point(data = linha_pc_todas_icf, aes(x = tipologia_quebrada, y = pc_scaled), 
             color = "red", size = 3, inherit.aes = FALSE) +
  geom_line(data = linha_pc_todas_icf, aes(x = tipologia_quebrada, y = pc_scaled, group = 1), 
            color = "red", linewidth = 1.2, inherit.aes = FALSE) +
  facet_wrap(~Superintendencia, scales = "free_x") +
  scale_y_continuous(
    name = "Quantidade",
    limits = c(0, 1500),
    labels = function(x) ifelse(x == 0, "0", scales::comma(x, big.mark = ".", decimal.mark = ",")),
    sec.axis = sec_axis(~ (. / 1500) * limite_pc_max_icf, 
                       name = "Por 100 mil hab.",
                       labels = function(x) ifelse(x == 0, "0", format(round(x, 3), nsmall = 3, decimal.mark = ",")))
  ) +
  scale_fill_manual(values = cores_setores, name = NULL) +
  labs(
    title = "",
    x = NULL,
    y = "Quantidade",
    caption = ""
  ) +
  theme_minimal() +
  theme(
    # Fontes maiores para todos os elementos de texto
    axis.text.x = element_text(angle = 0, hjust = 0.5, size = 16),
    axis.text.y = element_text(size = 16),
    axis.title = element_text(size = 18, face = "plain"),
    axis.title.y = element_text(margin = margin(r = 15), face = "plain"),
    axis.title.y.right = element_text(margin = margin(l = 15), face = "plain"),
    
    # Remover tick marks
    axis.ticks.y = element_blank(),
    axis.ticks.y.right = element_blank(),
    axis.ticks.x = element_blank(),
    
    # Legenda com fonte maior
    legend.text = element_text(size = 13),
    legend.position = "right",
    legend.key.size = unit(1.0, "cm"),
    legend.margin = margin(l = 15),
    
    # Labels das facetas maiores
    strip.text = element_text(size = 16, face = "plain"),
    
    # Ajustes de grid e espaçamento
    panel.grid.minor = element_blank(),
    panel.grid.major.x = element_blank(),
    panel.spacing = unit(1.5, "cm"),
    
    # Margens do plot
    plot.margin = margin(20, 20, 20, 20)
  ) +
  guides(fill = guide_legend(ncol = 1, byrow = TRUE, 
                             title.position = "top",
                             label.position = "right"))

# =============================================================================
# SALVAR E EXIBIR
# =============================================================================

# Salvar o gráfico com configurações otimizadas para LaTeX
save_plot(grafico, "icf_superint_setor", width = 14, height = 7, format = "png")

# Exibir o gráfico
print(grafico)

cat("\nMédias per capita ICF por tipologia:\n")
print(medias_pc_icf %>% 
        select(tipologia2007, icf_sudene_pc_media, icf_sudam_pc_media) %>%
        mutate(across(ends_with("_media"), ~ round(.x, 4))))

cat("\nGráfico salvo como: icf_superint_setor.png\n")