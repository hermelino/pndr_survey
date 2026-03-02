# =============================================================================
# MAPA - DISTRIBUIÇÃO ESPACIAL DO PIB PER CAPITA RELATIVO
# =============================================================================

rm(list=ls())
gc()

# Pacotes necessários
if (!require("pacman")) install.packages("pacman")
pacman::p_load(readr, dplyr, magrittr, ggplot2, sf, cowplot)

# Carregar funções de output
source("./output_helpers.R")

# Carregar dados
painel <- read_rds("../output/data/dataset_completo_com_pib_relativo.rds")

# Anos de interesse
anos_interesse <- c(2002, 2010, 2019, 2021)

# =============================================================================
# GRÁFICO - DISTRIBUIÇÃO ESPACIAL DO PIB PER CAPITA RELATIVO
# =============================================================================

# Carregar shapefiles
# Municípios
shp_municipios_path <- "C:/OneDrive/DATABASES/DIVISÃO POLÍTICA E REGIONAL/SHAPES/BR_Municipios_2021/BR_Municipios_2021.shp"
shp_municipios <- st_read(shp_municipios_path, quiet = TRUE) %>%
  mutate(CD_MUN = as.numeric(CD_MUN))

# Estados (para bordas)
shp_estados_path <- "C:/OneDrive/DATABASES/DIVISÃO POLÍTICA E REGIONAL/SHAPES/BR_UF_2021/BR_UF_2021.shp"
shp_estados <- st_read(shp_estados_path, quiet = TRUE)

# Preparar dados para o mapa (apenas municípios das superintendências)
dados_mapa <- painel %>%
  filter(ano %in% anos_interesse & (sudam == 1 | sudene2021 == 1 | sudeco == 1)) %>%
  select(ano, CD_MUN, pibrpc_relativo, classificacao_pib) %>%
  mutate(
    # Criar categorias conforme legenda do gráfico original
    categoria_mapa = case_when(
      pibrpc_relativo >= 0 & pibrpc_relativo < 0.25 ~ "0 a 0,25",
      pibrpc_relativo >= 0.25 & pibrpc_relativo < 0.5 ~ "0,25 a 0,5", 
      pibrpc_relativo >= 0.5 & pibrpc_relativo < 0.75 ~ "0,5 a 0,75",
      pibrpc_relativo >= 0.75 & pibrpc_relativo <= 1 ~ "0,75 a 1",
      pibrpc_relativo > 1 ~ "Maior que 1",
      TRUE ~ NA_character_
    ),
    categoria_mapa = factor(categoria_mapa, 
                           levels = c("0 a 0,25", "0,25 a 0,5", "0,5 a 0,75", "0,75 a 1", "Maior que 1"),
                           ordered = TRUE)
  )

# Unir dados com shapefile
mapa_dados <- shp_municipios %>%
  right_join(dados_mapa, by = "CD_MUN")

# Definir cores conforme o gráfico original
cores_mapa <- c("0 a 0,25" = "#dcf3e8",      # 90% mais claro que o verde da próxima categoria
                "0,25 a 0,5" = "#a8ddb5",     # verde claro
                "0,5 a 0,75" = "#7bccc4",     # verde-azul claro
                "0,75 a 1" = "#4eb3d3",       # azul claro
                "Maior que 1" = "#0868ac")    # azul escuro

# Criar função para gerar cada mapa
criar_mapa_ano <- function(ano_sel) {
  dados_ano <- mapa_dados %>% filter(ano == ano_sel)
  
  ggplot() +
    # Municípios sem bordas
    geom_sf(data = dados_ano, aes(fill = categoria_mapa), 
            color = NA) +
    # Bordas dos estados com cor reduzida (75% de intensidade) e linha mais fina
    geom_sf(data = shp_estados, fill = NA, 
            color = "#404040", size = 0.15) +
    scale_fill_manual(values = cores_mapa, na.value = "white", drop = FALSE) +
    labs(title = as.character(ano_sel)) +
    theme_void() +
    theme(
      plot.title = element_text(hjust = 0.5, size = 20, face = "plain", 
                               margin = margin(t = 10, b = 10), family = "Times"),
      legend.position = "none",
      panel.background = element_rect(fill = "white", color = "white"),
      plot.background = element_rect(fill = "white", color = "white")
    ) +
    coord_sf(crs = st_crs(4326), expand = FALSE, ylim = c(-24, 5))
}

# Criar os 4 mapas
mapa_2002 <- criar_mapa_ano(2002)
mapa_2010 <- criar_mapa_ano(2010)
mapa_2019 <- criar_mapa_ano(2019)
mapa_2021 <- criar_mapa_ano(2021)

# Criar legenda separada
legenda_data <- data.frame(
  x = 1:5,
  y = 1,
  categoria = factor(c("0 a 0,25", "0,25 a 0,5", "0,5 a 0,75", "0,75 a 1", "Maior que 1"),
                    levels = c("0 a 0,25", "0,25 a 0,5", "0,5 a 0,75", "0,75 a 1", "Maior que 1"))
)

legenda_plot <- ggplot(legenda_data, aes(x = x, y = y, fill = categoria)) +
  geom_tile(color = "#404040", size = 0.15) +
  scale_fill_manual(values = cores_mapa) +
  theme_void() +
  theme(legend.position = "bottom",
        legend.title = element_blank(),
        legend.text = element_text(size = 16, family = "Times"),
        legend.key.width = unit(1.5, "cm"),
        legend.key.height = unit(0.5, "cm")) +
  guides(fill = guide_legend(nrow = 1, byrow = TRUE))

# Combinar os 4 mapas em grid 2x2 com espaçamento reduzido
mapas_grid <- plot_grid(mapa_2002, mapa_2010, mapa_2019, mapa_2021, 
                       ncol = 2, nrow = 2, align = "hv", 
                       hjust = 0, vjust = 0.5)

# Extrair apenas a legenda
legenda <- get_legend(legenda_plot)

# Combinar tudo
grafico_final <- plot_grid(
  mapas_grid,
  legenda,
  ncol = 1,
  rel_heights = c(1, 0.1)
)

# Salvar o gráfico
ggsave("../output/maps/distribuicao_pib_relativo_municipal.png", 
       grafico_final, 
       width = 12, height = 10, dpi = 300, bg = "white")

# Salvar também na pasta de figuras da tese
ggsave("../../arquivos_latex/tese/figuras/distribuicao_pib_relativo_municipal.png", 
       grafico_final, 
       width = 12, height = 10, dpi = 300, bg = "white")

cat("=== MAPA GERADO ===\n")
cat("Arquivo salvo em: ../output/maps/distribuicao_pib_relativo_municipal.png\n")
cat("Arquivo salvo em: ../../arquivos_latex/tese/figuras/distribuicao_pib_relativo_municipal.png\n")
