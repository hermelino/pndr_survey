@echo off
REM =============================================================================
REM pndr_survey — Build Script (Windows)
REM =============================================================================
REM Pipeline completo para regenerar todos os outputs do zero.
REM Requer: Python 3.12+, R, PDFs em data\2-papers\2-2-papers-pdfs\
REM
REM Uso:
REM   build.bat setup       Instalar dependências
REM   build.bat all         Pipeline completo
REM   build.bat clean       Limpar outputs gerados
REM   build.bat help        Mostrar ajuda
REM
REM Etapas individuais:
REM   build.bat import      Importar registros das 5 bases
REM   build.bat screen      Triagem pré-LLM
REM   build.bat analyze     Análise LLM (requer GEMINI_API_KEY e PDFs)
REM   build.bat merge       Mesclar registros + LLM
REM   build.bat citations   Matching de citações + índice
REM   build.bat references  Gerar RIS + BibTeX aprovados
REM   build.bat tables      Gerar tabelas LaTeX
REM   build.bat figures     Gerar figuras (mapas, gráficos)
REM   build.bat latex       Compilar PDF do artigo
REM =============================================================================

setlocal enabledelayedexpansion

REM --- Verificar Python ---
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] Python não encontrado. Instale Python 3.12+ e tente novamente.
    exit /b 1
)

REM --- Parse command ---
set COMMAND=%1
if "%COMMAND%"=="" set COMMAND=help

if "%COMMAND%"=="setup" goto :setup
if "%COMMAND%"=="import" goto :import
if "%COMMAND%"=="screen" goto :screen
if "%COMMAND%"=="analyze" goto :analyze
if "%COMMAND%"=="merge" goto :merge
if "%COMMAND%"=="citations" goto :citations
if "%COMMAND%"=="references" goto :references
if "%COMMAND%"=="tables" goto :tables
if "%COMMAND%"=="figures" goto :figures
if "%COMMAND%"=="latex" goto :latex
if "%COMMAND%"=="all" goto :all
if "%COMMAND%"=="clean" goto :clean
if "%COMMAND%"=="validate" goto :validate
if "%COMMAND%"=="help" goto :help

echo [ERRO] Comando desconhecido: %COMMAND%
goto :help

REM =============================================================================
REM Setup
REM =============================================================================
:setup
echo =^> Instalando dependências...
cd scripts
python -m pip install -r requirements.txt
cd ..
echo.
echo =^> Verificando config.yaml...
if not exist "scripts\config.yaml" (
    echo [AVISO] config.yaml não encontrado. Copiando de config.example.yaml...
    copy "scripts\config.example.yaml" "scripts\config.yaml"
    echo.
    echo ATENÇÃO: Edite scripts\config.yaml antes de prosseguir:
    echo   1. Defina GEMINI_API_KEY no ambiente ou no arquivo
    echo   2. Configure paths de dados externos ^(external_data_dir, external_shapefiles_dir^)
    echo.
)
echo =^> Setup concluído!
goto :eof

REM =============================================================================
REM Import
REM =============================================================================
:import
echo =^> Importando registros das 5 bases...
cd scripts
python main.py search --verbose ^
    --import-scopus "..\data\1-records\1-1-records-scopus\scopus_20260225.ris" ^
    --import-scielo "..\data\1-records\1-2-records-scielo\scielo_20260226.ris" ^
    --import-capes "..\data\1-records\1-3-records-capes\capes_20260224.ris" ^
    --import-econpapers "..\data\1-records\1-4-records-econpapers\econpapers_20260224.ris" ^
    --import-anpec "..\data\1-records\1-5-records-anpec\anpec_20260225.xlsx"
cd ..
echo =^> Importação concluída: data\1-records\processed\bib_records.json
goto :eof

REM =============================================================================
REM Screen
REM =============================================================================
:screen
echo =^> Executando triagem pré-LLM ^(PRISMA^)...
cd scripts
python main.py screen --verbose --input-json "..\data\1-records\processed\bib_records.json"
cd ..
echo =^> Triagem concluída: data\1-records\processed\bib_screened.json
goto :eof

REM =============================================================================
REM Analyze
REM =============================================================================
:analyze
echo =^> Executando análise LLM ^(3 estágios^)...
echo [ATENÇÃO] Requer:
echo   1. GEMINI_API_KEY configurada
echo   2. PDFs em data\2-papers\2-2-papers-pdfs\ ^(119 arquivos^)
echo.
cd scripts
python run_llm_all_papers.py
cd ..
echo =^> Análise LLM concluída
goto :eof

REM =============================================================================
REM Merge
REM =============================================================================
:merge
echo =^> Mesclando registros + classificação LLM...
cd scripts
python merge_papers_to_json.py
cd ..
echo =^> JSON enriquecido gerado: data\2-papers\2-2-papers.json
goto :eof

REM =============================================================================
REM Citations
REM =============================================================================
:citations
echo =^> Executando matching de citações entre estudos...
cd scripts
python match_refs_to_studies.py
echo.
echo =^> Calculando índice de citação...
python citation_index.py
cd ..
echo =^> Índice de citação gerado: data\3-ref-bib\citation_index_results.json
goto :eof

REM =============================================================================
REM References
REM =============================================================================
:references
echo =^> Gerando RIS de estudos aprovados...
cd scripts
python generate_approved_ris.py
echo.
echo =^> Convertendo RIS → BibTeX...
python generate_bibtex.py
echo.
echo =^> Gerando tabela de índice de citação...
python generate_ic_table.py
cd ..
echo =^> Referências geradas:
echo   - data\3-ref-bib\approved_studies.ris
echo   - latex\references.bib
echo   - latex\tabela_ic.tex
goto :eof

REM =============================================================================
REM Tables
REM =============================================================================
:tables
echo =^> Gerando todas as tabelas LaTeX...
cd scripts
python generate_latex_tables.py
cd ..
echo =^> Tabelas geradas em latex\tabelas\
goto :eof

REM =============================================================================
REM Figures
REM =============================================================================
:figures
echo =^> Gerando figuras ^(mapas PIB, tipologia, gráfico ICF^)...
cd scripts
python generate_figures.py --verbose
cd ..
echo =^> Figuras geradas em figures\
goto :eof

REM =============================================================================
REM LaTeX
REM =============================================================================
:latex
echo =^> Compilando artigo LaTeX...
cd latex
pdflatex -interaction=nonstopmode main.tex
bibtex main
pdflatex -interaction=nonstopmode main.tex
pdflatex -interaction=nonstopmode main.tex
cd ..
echo =^> Artigo compilado: latex\main.pdf
goto :eof

REM =============================================================================
REM All
REM =============================================================================
:all
echo ==========================================
echo Pipeline completo iniciado
echo ==========================================
echo.
call :setup
call :import
call :screen
call :merge
call :citations
call :references
call :tables
call :figures
call :latex
echo.
echo ==========================================
echo Pipeline completo executado com sucesso!
echo ==========================================
echo.
echo Outputs gerados:
echo   - Artigo PDF: latex\main.pdf
echo   - Registros processados: data\1-records\processed\bib_records.json
echo   - JSON enriquecido: data\2-papers\2-2-papers.json
echo   - Índice de citação: data\3-ref-bib\citation_index_results.json
echo.
echo NOTA: A análise LLM foi pulada. Execute manualmente com:
echo   build.bat analyze
echo.
goto :eof

REM =============================================================================
REM Clean
REM =============================================================================
:clean
echo =^> Limpando outputs gerados...
REM Dados processados
del /Q "data\1-records\processed\*.json" 2>nul
del /Q "data\1-records\processed\*.csv" 2>nul
del /Q "data\1-records\processed\*.xlsx" 2>nul
REM Papers
del /Q "data\2-papers\*.json" 2>nul
del /Q "data\2-papers\*.xlsx" 2>nul
del /Q "data\2-papers\_llm_checkpoint.json" 2>nul
REM Referências
del /Q "data\3-ref-bib\*.json" 2>nul
del /Q "data\3-ref-bib\*.txt" 2>nul
del /Q "data\3-ref-bib\*.ris" 2>nul
rmdir /S /Q "data\3-ref-bib\refs_por_estudo" 2>nul
REM LaTeX outputs
del /Q "latex\*.aux" 2>nul
del /Q "latex\*.bbl" 2>nul
del /Q "latex\*.blg" 2>nul
del /Q "latex\*.log" 2>nul
del /Q "latex\*.out" 2>nul
del /Q "latex\*.toc" 2>nul
del /Q "latex\*.pdf" 2>nul
del /Q "latex\references.bib" 2>nul
del /Q "latex\tabela_ic.tex" 2>nul
REM Figuras (opcional - comente se quiser manter)
REM del /Q "figures\*.png" 2>nul
echo =^> Limpeza concluída!
goto :eof

REM =============================================================================
REM Validate
REM =============================================================================
:validate
echo =^> Validando dependências...
echo.
echo Python:
python --version
echo.
echo R:
Rscript --version 2>nul
if %errorlevel% neq 0 (
    echo [AVISO] R não encontrado. Necessário para gerar figuras.
)
echo.
echo PDFs:
dir /B "data\2-papers\2-2-papers-pdfs\*.pdf" 2>nul | find /C ".pdf"
echo.
echo Figuras ^(dependências externas^):
cd scripts
python generate_figures.py --validate
cd ..
goto :eof

REM =============================================================================
REM Help
REM =============================================================================
:help
echo pndr_survey — Pipeline de Reprodutibilidade
echo.
echo Uso: build.bat [comando]
echo.
echo Comandos disponíveis:
echo   setup       Instalar dependências
echo   import      Importar registros das 5 bases
echo   screen      Triagem pré-LLM
echo   analyze     Análise LLM ^(requer GEMINI_API_KEY e PDFs^)
echo   merge       Mesclar registros + LLM
echo   citations   Matching de citações + índice
echo   references  Gerar RIS + BibTeX aprovados
echo   tables      Gerar tabelas LaTeX
echo   figures     Gerar figuras ^(mapas, gráficos^)
echo   latex       Compilar PDF do artigo
echo   all         Pipeline completo ^(padrão, exceto analyze^)
echo   clean       Limpar outputs gerados
echo   validate    Validar dependências ^(Python, R, PDFs^)
echo   help        Mostrar esta mensagem
echo.
echo Documentação completa: REPRODUCING.md
goto :eof
