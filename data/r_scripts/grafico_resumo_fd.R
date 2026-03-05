# =============================================================================
# GRÁFICO RESUMO FUNDOS DE DESENVOLVIMENTO  
# =============================================================================

rm(list=ls())
gc()

# Pacotes necessários
if (!require("pacman")) install.packages("pacman")
pacman::p_load(tidyverse, ggplot2, RColorBrewer, scales, readxl)

# Carregar funções de output
source("./output_helpers.R")

# Carregar dados necessários
data_dir <- "../external_data"
resumo_fd <- readxl::read_excel(file.path(data_dir, "resumo_fd.xlsx"))

# Carregar dados para calcular per capita
painel_fd <- readr::read_rds(file.path(data_dir, "painel_fd_agregado.rds"))
populacao <- readr::read_rds(file.path(data_dir, "populacao_fc.rds"))
df_tipologia2007 <- readxl::read_excel(file.path(data_dir, "tipologia_2007.xlsx"), sheet="Table 1") %>%
  select(1,6) %>% rename_with(~c("id_municipio","tipologia2007")) %>%
  mutate(id_municipio = as.numeric(id_municipio))

# =============================================================================
# PREPARAÇÃO DOS DADOS PARA O GRÁFICO
# =============================================================================

# Preparar os dados para o gráfico
dados_grafico <- resumo_fd %>%
  # Remover valores NA na tipologia
  filter(!is.na(tipologia2007)) %>%
  # Remover combinação Baixa Renda + FDCO
  filter(!(tipologia2007 == "Baixa Renda" & INSTR == "FDCO")) %>%
  # Definir ordem dos instrumentos: FDNE, FDA, FDCO
  mutate(INSTR = factor(INSTR, levels = c("FDNE", "FDA", "FDCO"))) %>%
  # Garantir que as tipologias estejam na ordem desejada e adicionar quebras de linha
  mutate(tipologia2007 = factor(tipologia2007, 
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
         # Ordenar setores e adicionar quebras de linha se necessário
         SETOR_quebrado = case_when(
           SETOR == "Indústria de transformação" ~ "Indústria de transformação",
           SETOR == "Infraestrutura" ~ "Infraestrutura",
           SETOR == "Indústria extrativa" ~ "Indústria extrativa",
           SETOR == "Serviços" ~ "Serviços",
           TRUE ~ SETOR
         ),
         # Converter valores para bilhões para melhor visualização
         valor_milhoes = valor / 1000000000)

# Calcular médias per capita por tipologia para FD
medias_pc_fd <- painel_fd %>%
  left_join(df_tipologia2007, by = c("COD_MUNIC" = "id_municipio")) %>%
  left_join(populacao, by = c("COD_MUNIC" = "CD_MUN", "year" = "ano")) %>%
  filter(!is.na(tipologia2007) & !is.na(populacao) & populacao > 0) %>%
  mutate(
    fdne_pc = fdne / populacao,
    fda_pc = fda / populacao,
    fdco_pc = fdco / populacao
  ) %>%
  group_by(tipologia2007) %>%
  summarise(
    fdne_pc_media = mean(fdne_pc, na.rm = TRUE),
    fda_pc_media = mean(fda_pc, na.rm = TRUE),
    fdco_pc_media = mean(fdco_pc, na.rm = TRUE),
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
max_pc_valor_fd <- max(c(medias_pc_fd$fdne_pc_media, medias_pc_fd$fda_pc_media, medias_pc_fd$fdco_pc_media), na.rm = TRUE)
limite_pc_max_fd <- ceiling(max_pc_valor_fd * 1.1)

cat("Escala per capita FD: 0 a", limite_pc_max_fd, "reais per capita\n")

# Preparar dados da linha per capita por instrumento
linha_pc_fdne <- medias_pc_fd %>%
  select(tipologia_quebrada, fdne_pc_media) %>%
  mutate(pc_scaled = (fdne_pc_media / limite_pc_max_fd) * 4) %>%
  mutate(INSTR = "FDNE")

linha_pc_fda <- medias_pc_fd %>%
  select(tipologia_quebrada, fda_pc_media) %>%
  mutate(pc_scaled = (fda_pc_media / limite_pc_max_fd) * 4) %>%
  mutate(INSTR = "FDA")

linha_pc_fdco <- medias_pc_fd %>%
  select(tipologia_quebrada, fdco_pc_media) %>%
  mutate(pc_scaled = (fdco_pc_media / limite_pc_max_fd) * 4) %>%
  mutate(INSTR = "FDCO")

linha_pc_todas <- bind_rows(linha_pc_fdne, linha_pc_fda, linha_pc_fdco) %>%
  mutate(INSTR = factor(INSTR, levels = c("FDNE", "FDA", "FDCO")))

# Definir uma paleta de cores para os setores
cores_setores <- RColorBrewer::brewer.pal(n = max(3, length(unique(dados_grafico$SETOR))), 
                                          name = "Set3")[1:length(unique(dados_grafico$SETOR))]

# Criar o gráfico com fontes maiores e eixo secundário
grafico <- ggplot(dados_grafico, aes(x = tipologia_quebrada, y = valor_milhoes, fill = SETOR_quebrado)) +
  geom_col(position = "stack", width = 0.8) +
  # Adicionar linha vermelha per capita
  geom_point(data = linha_pc_todas, aes(x = tipologia_quebrada, y = pc_scaled), 
             color = "red", size = 3, inherit.aes = FALSE) +
  geom_line(data = linha_pc_todas, aes(x = tipologia_quebrada, y = pc_scaled, group = 1), 
            color = "red", linewidth = 1.2, inherit.aes = FALSE) +
  facet_wrap(~INSTR, scales = "fixed") +
  scale_y_continuous(
    name = "Valor (R$ bilhões)",
    limits = c(0, 4), 
    labels = function(x) ifelse(x == 0, "0", scales::comma(x, big.mark = ".", decimal.mark = ",")),
    sec.axis = sec_axis(~ (. / 4) * limite_pc_max_fd, 
                       name = "Per Capita (R$)",
                       labels = function(x) ifelse(x == 0, "0", scales::comma(x, big.mark = ".", decimal.mark = ",")))
  ) +
  scale_fill_manual(values = cores_setores, name = NULL) +
  labs(
    title = "",
    x = NULL,
    y = "Valor (R$ bilhões)",
    caption = ""
  ) +
  theme_minimal(base_family = "serif") +
  theme(
    # Fonte serif (compatível com LaTeX) em todos os elementos
    text = element_text(family = "serif"),
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
    legend.position = "bottom",
    legend.key.size = unit(0.8, "cm"),
    legend.margin = margin(t = 20),
    legend.box = "horizontal",
    
    # Labels das facetas maiores
    strip.text = element_text(size = 16, face = "plain"),
    
    # Ajustes de grid e espaçamento
    panel.grid.minor.y = element_line(color = "gray90", linewidth = 0.3),
    panel.grid.major.x = element_blank(),
    panel.spacing = unit(1.5, "cm"),
    
    # Margens do plot
    plot.margin = margin(20, 20, 20, 20)
  ) +
  guides(fill = guide_legend(nrow = 1, byrow = TRUE, 
                             title = NULL,
                             label.position = "right"))

# =============================================================================
# SALVAR E EXIBIR
# =============================================================================

# Salvar o gráfico com configurações otimizadas para LaTeX
figures_dir <- "../../figures"
if (!dir.exists(figures_dir)) dir.create(figures_dir, recursive = TRUE)
ggsave(file.path(figures_dir, "fd_fundo_setor.png"), grafico,
       width = 14, height = 6, units = "in", dpi = 300)

# Exibir o gráfico
print(grafico)

cat("\nMédias per capita FD por tipologia:\n")
print(medias_pc_fd %>%
        select(tipologia2007, fdne_pc_media, fda_pc_media, fdco_pc_media) %>%
        mutate(across(ends_with("_media"), ~ round(.x, 2))))

cat("\nGráfico salvo como: fd_fundo_setor.png\n")