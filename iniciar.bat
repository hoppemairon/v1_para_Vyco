@echo off
echo ====================================
echo    Conversor V1 para Vyco
echo ====================================
echo.

echo Verificando Python...
python --version
if %errorlevel% neq 0 (
    echo ERRO: Python nao encontrado. Por favor, instale o Python primeiro.
    pause
    exit /b 1
)

echo.
echo Instalando dependencias...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERRO: Falha ao instalar dependencias.
    pause
    exit /b 1
)

echo.
echo Criando diretorios necessarios...
if not exist "planilhas_geradas" mkdir "planilhas_geradas"
if not exist "logs" mkdir "logs"

echo.
echo ====================================
echo Iniciando aplicacao Streamlit...
echo ====================================
echo Acesse no navegador: http://localhost:8501
echo Para parar a aplicacao, pressione Ctrl+C
echo.

streamlit run app.py