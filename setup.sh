#!/bin/bash
# Script de setup pour Trading Analyzer

echo "🚀 Installation de Trading Analyzer..."

# Vérifie Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 n'est pas installé. Télécharge-le depuis python.org"
    exit 1
fi

echo "✅ Python trouvé"

# Crée l'env virtuel
echo "Création de l'environnement virtuel..."
python3 -m venv venv

# Active l'env
echo "Activation de l'environnement..."
source venv/bin/activate

# Installe les dépendances
echo "Installation des dépendances Python..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "================================"
echo "✅ Installation complète!"
echo "================================"
echo ""
echo "Étapes suivantes :"
echo ""
echo "1. Installe Tesseract OCR :"
echo "   - Mac: brew install tesseract"
echo "   - Linux: sudo apt-get install tesseract-ocr"
echo "   - Windows: Télécharge depuis github.com/UB-Mannheim/tesseract/wiki"
echo ""
echo "2. Installe Ollama depuis ollama.com"
echo ""
echo "3. Lance Ollama avec le modèle :"
echo "   ollama run llava:7b"
echo ""
echo "4. Dans une autre terminal, lance l'app :"
echo "   source venv/bin/activate"
echo "   streamlit run app.py"
echo ""
