rm(list=ls())
gc()

# MAPA SIMPLES PARA TESTE - SEM TMAP

# Install and load packages using pacman
if (!require(pacman, quietly = TRUE)) install.packages("pacman")
pacman::p_load(readr, magrittr, sf, dplyr, ggplot2)

# Carregar shapefiles básicos
shp_uf <- "C:/OneDrive/DATABASES/DIVISÃO POLÍTICA E REGIONAL/SHAPES/BR_UF_2021/"
shp_uf <- st_read(paste0(shp_uf, "BR_UF_2021.shp"), quiet = TRUE)

levels <- c("Baixa Renda e Baixo Dinamismo", 
            "Baixa Renda e Médio Dinamismo",
            "Baixa Renda e Alto Dinamismo", 
            "Média Renda e Baixo Dinamismo", 
            "Média Renda e Médio Dinamismo", 
            "Média Renda e Alto Dinamismo", 
            "Alta Renda e Baixo Dinamismo", 
            "Alta Renda e Médio Dinamismo", 
            "Alta Renda e Alto Dinamismo")

shp <- "C:/OneDrive/DATABASES/DIVISÃO POLÍTICA E REGIONAL/SHAPES/BR_Municipios_2021/"
shp <- sf::st_read(paste0(shp,"BR_Municipios_2021.shp"),quiet=TRUE) %>%
  dplyr::mutate(CD_MUN=as.numeric(CD_MUN)) %>%
  dplyr::select(CD_MUN,geometry)

# Carregar dados e filtrar todas as três regiões
painel_unificado <- readr::read_rds("../output/data/painel_balanc_var_ln_pibrpc.rds") %>%
  merge(shp,by="CD_MUN",all.x=T) %>%
  dplyr::mutate(sudeco=ifelse(uberlandia==1,1,sudeco),
                tipologia=factor(tipologia,levels=levels)) %>%
  dplyr::filter(ano==2020) %>%
  dplyr::select(CD_MUN,norte,nordeste,centrooeste,
                sudene2021,sudam,sudeco,tipologia,geometry) %>% 
  st_as_sf()

# NOVA PALETA DE CORES
p <- c("Baixa Renda e Baixo Dinamismo" ="#ff6666",   
       "Baixa Renda e Médio Dinamismo" ="#ff9999",   
       "Baixa Renda e Alto Dinamismo"  ="#ffcccc",   
       "Média Renda e Baixo Dinamismo" ="#FFD700",   
       "Média Renda e Médio Dinamismo" ="#FFFF99",   
       "Média Renda e Alto Dinamismo"  ="#90EE90",   
       "Alta Renda e Baixo Dinamismo"  ="#87CEEB",   
       "Alta Renda e Médio Dinamismo"  ="#E6F3FF",   
       "Alta Renda e Alto Dinamismo"   ="#FFFFFF")

# Tentar carregar limites especiais (pode ser lento)
cat("Carregando limites especiais...\n")

# Inicializar como NULL
shp_semiarido <- NULL
shp_amazonia <- NULL

# Tentar carregar semiárido
tryCatch({
  path_semiarido <- "C:/OneDrive/DATABASES/DIVISÃO POLÍTICA E REGIONAL/LIM_Semiarido_Municipal_OFICIAL/"
  if (file.exists(paste0(path_semiarido, "LIM_Semiarido_Municipal_OFICIAL.shp"))) {
    dados_semiarido <- sf::st_read(paste0(path_semiarido, "LIM_Semiarido_Municipal_OFICIAL.shp"), quiet=TRUE)
    shp_semiarido <- dados_semiarido %>%
      sf::st_simplify(dTolerance = 0.05) %>%  # Simplificação mais agressiva
      sf::st_geometry() %>%  
      sf::st_union()
    cat("Semiárido carregado com sucesso\n")
  }
}, error = function(e) {
  cat("Erro ao carregar semiárido:", e$message, "\n")
})

# Tentar carregar Amazônia Legal
tryCatch({
  path_amazonia <- "C:/OneDrive/DATABASES/DIVISÃO POLÍTICA E REGIONAL/AMAZONIA LEGAL/Mun_Amazonia_Legal_2022_shp/"
  if (file.exists(paste0(path_amazonia, "Mun_Amazonia_Legal_2022.shp"))) {
    dados_amazonia <- sf::st_read(paste0(path_amazonia, "Mun_Amazonia_Legal_2022.shp"), quiet=TRUE)
    shp_amazonia <- dados_amazonia %>%
      sf::st_simplify(dTolerance = 0.05) %>%  # Simplificação mais agressiva
      sf::st_geometry() %>%  
      sf::st_union() %>%
      sf::st_boundary()
    cat("Amazônia Legal carregada com sucesso\n")
  }
}, error = function(e) {
  cat("Erro ao carregar Amazônia Legal:", e$message, "\n")
})

# Criar mapa simples usando ggplot2
mapa_simples <- ggplot() +
  # Municípios com tipologia
  geom_sf(data = painel_unificado, aes(fill = tipologia), color = "white", linewidth = 0.05) +
  # Bordas dos estados
  geom_sf(data = shp_uf, fill = NA, color = "black", linewidth = 0.8)

# Adicionar semiárido se foi carregado com sucesso
if (!is.null(shp_semiarido)) {
  mapa_simples <- mapa_simples +
    geom_sf(data = shp_semiarido, color = "#ff8c00", linewidth = 2, fill = NA)
}

# Adicionar Amazônia Legal se foi carregada com sucesso  
if (!is.null(shp_amazonia)) {
  mapa_simples <- mapa_simples +
    geom_sf(data = shp_amazonia, color = "#0066cc", linewidth = 2, fill = NA)
}

# Finalizar mapa
mapa_simples <- mapa_simples +
  # Configurar cores
  scale_fill_manual(values = p, na.value = "#d5dce1") +
  # Configurar tema
  theme_void() +
  theme(
    legend.position = "none",
    panel.background = element_rect(fill = "white", color = NA),
    plot.background = element_rect(fill = "white", color = NA)
  ) +
  # Remover grid e eixos
  coord_sf(expand = FALSE)

# Salvar mapa
file_name_simples <- "../output/maps/tipologia_simples.png"
ggsave(filename = file_name_simples, plot = mapa_simples, width = 16, height = 12, dpi = 300, units = "in", bg = "white")

cat("Mapa simples salvo em:", file_name_simples, "\n")
