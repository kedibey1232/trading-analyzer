#!/usr/bin/env python3
"""
Script de test pour vérifier l'installation de Trading Analyzer
"""

import sys

print("=" * 60)
print("🧪 Vérification des dépendances Trading Analyzer")
print("=" * 60)
print()

# Test Python version
print(f"✓ Python {sys.version}")
print()

# Test des imports Python
dependencies = [
    ("streamlit", "Streamlit"),
    ("cv2", "OpenCV"),
    ("pytesseract", "Pytesseract"),
    ("PIL", "Pillow"),
    ("ollama", "Ollama"),
    ("requests", "Requests"),
    ("pandas", "Pandas"),
    ("numpy", "NumPy"),
]

print("Vérification des packages Python :")
all_ok = True
for module_name, display_name in dependencies:
    try:
        __import__(module_name)
        print(f"  ✅ {display_name}")
    except ImportError:
        print(f"  ❌ {display_name} - NON INSTALLÉ")
        all_ok = False

print()

# Test Tesseract
print("Vérification de Tesseract OCR :")
try:
    import pytesseract
    result = pytesseract.get_tesseract_version()
    print(f"  ✅ Tesseract installé : {result}")
except Exception as e:
    print(f"  ❌ Tesseract non trouvé ou non configuré")
    print(f"     Erreur: {e}")
    print()
    print("     Solutions :")
    print("     - Mac: brew install tesseract")
    print("     - Linux: sudo apt-get install tesseract-ocr")
    print("     - Windows: Télécharge depuis github.com/UB-Mannheim/tesseract/wiki")
    all_ok = False

print()

# Test Ollama
print("Vérification de Ollama :")
try:
    import ollama
    print("  ✅ Package Ollama installé")
    print()
    print("  Note: Vérifiez que Ollama est lancé :")
    print("        ollama run llava:7b")
except Exception as e:
    print(f"  ❌ Ollama non trouvé: {e}")
    all_ok = False

print()
print("=" * 60)

if all_ok:
    print("✅ Toutes les dépendances sont correctement installées!")
    print()
    print("Prochaines étapes :")
    print("1. Assurez-vous que Ollama est lancé:")
    print("   → ollama run llava:7b")
    print()
    print("2. Lancez l'application:")
    print("   → streamlit run app.py")
    print()
else:
    print("❌ Certaines dépendances manquent ou ne sont pas configurées")
    print()
    print("Solutions :")
    print("1. Réinstallez les packages: pip install -r requirements.txt")
    print("2. Installez Tesseract OCR (voir guide ci-dessus)")
    print("3. Installez Ollama depuis ollama.com")
    print()
    sys.exit(1)

print("=" * 60)
