# =============================================================================
# OUTPUT HELPERS - Funções para salvar outputs organizadamente
# =============================================================================

# Define o diretório base de output
output_dir <- "../output"

# Função para salvar dados
save_data <- function(data, filename, format = "rds") {
  dir_path <- file.path(output_dir, "data")
  if (!dir.exists(dir_path)) dir.create(dir_path, recursive = TRUE)
  
  filepath <- file.path(dir_path, paste0(filename, ".", format))
  
  if (format == "rds") {
    saveRDS(data, filepath)
  } else if (format == "csv") {
    write.csv(data, filepath, row.names = FALSE)
  } else if (format == "xlsx") {
    openxlsx::write.xlsx(data, filepath)
  } else if (format == "dta") {
    haven::write_dta(data, filepath)
  }
  
  cat("Dados salvos em:", filepath, "\n")
  return(filepath)
}

# Função para salvar gráficos
save_plot <- function(plot_obj, filename, width = 10, height = 8, format = "png") {
  dir_path <- file.path(output_dir, "plots")
  if (!dir.exists(dir_path)) dir.create(dir_path, recursive = TRUE)
  
  filepath <- file.path(dir_path, paste0(filename, ".", format))
  
  if (format == "png") {
    png(filepath, width = width, height = height, units = "in", res = 300)
  } else if (format == "pdf") {
    pdf(filepath, width = width, height = height)
  }
  
  print(plot_obj)
  dev.off()
  
  cat("Gráfico salvo em:", filepath, "\n")
  return(filepath)
}

# Função para salvar tabelas
save_table <- function(table_data, filename, format = "csv") {
  dir_path <- file.path(output_dir, "tables")
  if (!dir.exists(dir_path)) dir.create(dir_path, recursive = TRUE)
  
  filepath <- file.path(dir_path, paste0(filename, ".", format))
  
  if (format == "csv") {
    write.csv(table_data, filepath, row.names = FALSE)
  } else if (format == "xlsx") {
    openxlsx::write.xlsx(table_data, filepath)
  } else if (format == "tex") {
    # Para LaTeX (requer stargazer ou similar)
    writeLines(table_data, filepath)
  }
  
  cat("Tabela salva em:", filepath, "\n")
  return(filepath)
}

# Função para salvar mapas
save_map <- function(map_obj, filename, width = 12, height = 10, format = "png") {
  dir_path <- file.path(output_dir, "maps")
  if (!dir.exists(dir_path)) dir.create(dir_path, recursive = TRUE)
  
  filepath <- file.path(dir_path, paste0(filename, ".", format))
  
  if (format == "png") {
    png(filepath, width = width, height = height, units = "in", res = 300)
  } else if (format == "pdf") {
    pdf(filepath, width = width, height = height)
  }
  
  print(map_obj)
  dev.off()
  
  cat("Mapa salvo em:", filepath, "\n")
  return(filepath)
}

# Função para salvar resultados de modelos
save_model <- function(model_obj, filename, format = "rds") {
  dir_path <- file.path(output_dir, "models")
  if (!dir.exists(dir_path)) dir.create(dir_path, recursive = TRUE)
  
  filepath <- file.path(dir_path, paste0(filename, ".", format))
  
  if (format == "rds") {
    saveRDS(model_obj, filepath)
  } else if (format == "txt") {
    capture.output(summary(model_obj), file = filepath)
  }
  
  cat("Modelo salvo em:", filepath, "\n")
  return(filepath)
}

# Função para salvar resultados de testes
save_test <- function(test_result, filename, format = "rds") {
  dir_path <- file.path(output_dir, "tests")
  if (!dir.exists(dir_path)) dir.create(dir_path, recursive = TRUE)
  
  filepath <- file.path(dir_path, paste0(filename, ".", format))
  
  if (format == "rds") {
    saveRDS(test_result, filepath)
  } else if (format == "txt") {
    capture.output(test_result, file = filepath)
  }
  
  cat("Teste salvo em:", filepath, "\n")
  return(filepath)
}

# cat("Output helpers carregados! Use:\n")
# cat("- save_data(data, 'nome_arquivo')\n")
# cat("- save_plot(grafico, 'nome_arquivo')\n") 
# cat("- save_table(tabela, 'nome_arquivo')\n")
# cat("- save_map(mapa, 'nome_arquivo')\n")
# cat("- save_model(modelo, 'nome_arquivo')\n")
# cat("- save_test(teste, 'nome_arquivo')\n")