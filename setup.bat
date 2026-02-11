@echo off
REM Script de setup pour Trading Analyzer sur Windows

echo 🚀 Installation de Trading Analyzer...
echo.

REM Vérifie Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python n'est pas installé. Télécharge-le depuis python.org
    pause
    exit /b 1
)

echo ✅ Python trouvé
echo.

REM Crée l'env virtuel
echo Création de l'environnement virtuel...
python -m venv venv

REM Active l'env
echo Activation de l'environnement...
call venv\Scripts\activate.bat

REM Installe les dépendances
echo Installation des dépendances Python...
python -m pip install --upgrade pip
pip install -r requirements.txt

echo.
echo ================================
echo ✅ Installation complète!
echo ================================
echo.
echo Étapes suivantes :
echo.
echo 1. Installe Tesseract OCR :
echo    Télécharge depuis github.com/UB-Mannheim/tesseract/wiki
echo.
echo 2. Installe Ollama depuis ollama.com
echo.
echo 3. Lance Ollama avec le modèle :
echo    ollama run llava:7b
echo.
echo 4. Dans une autre cmd, lance l'app :
echo    venv\Scripts\activate.bat
echo    streamlit run app.py
echo.
pause
