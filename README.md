# 📊 Trading Chart Analyzer PRO

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28%2B-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Analyseur automatique de graphiques de trading combinant **OCR**, **Computer Vision** et **IA locale** (Ollama) pour générer des rapports d'analyse technique complets — le tout en local, gratuit et privé.

---

## ✨ Fonctionnalités

- 📝 **OCR Avancé** — Extraction automatique des prix, symboles et timeframes via Tesseract
- 🎨 **Détection de Couleurs** — Analyse des tendances haussières/baissières par Computer Vision (OpenCV)
- 🤖 **Analyse IA Visuelle** — Analyse de structure, tendance et momentum via LLM local (llava:7b)
- 📊 **Rapport Complet** — Synthèse professionnelle avec données de prix, biais couleur et analyse IA
- 🔒 **100% Local & Privé** — Aucune donnée envoyée à l'extérieur

---

## 📁 Structure du Projet

```
trading-analyzer/
├── app.py              # Application principale Streamlit
├── test_setup.py       # Script de vérification d'installation
├── requirements.txt    # Dépendances Python
├── setup.sh            # Script d'installation (Mac/Linux)
├── setup.bat           # Script d'installation (Windows)
├── LICENSE             # Licence MIT
└── README.md
```

---

## 🚀 Installation

### Prérequis

| Composant     | Version | Lien                                                 |
| ------------- | ------- | ---------------------------------------------------- |
| Python        | 3.10+   | [python.org](https://python.org)                     |
| Tesseract OCR | Latest  | [GitHub](https://github.com/tesseract-ocr/tesseract) |
| Ollama        | Latest  | [ollama.com](https://ollama.com)                     |

### 1. Cloner le projet

```bash
git clone https://github.com/Bull1016/trading-analyzer.git
cd trading-analyzer
```

### 2. Installer les dépendances Python

**Mac/Linux :**

```bash
chmod +x setup.sh
./setup.sh
```

**Windows :**

```cmd
setup.bat
```

**Ou manuellement :**

```bash
python -m venv venv
source venv/bin/activate    # Mac/Linux
# venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

### 3. Installer Tesseract OCR

**Mac :**

```bash
brew install tesseract
```

**Linux (Ubuntu/Debian) :**

```bash
sudo apt-get install tesseract-ocr
```

**Windows :**

1. Télécharge l'installeur depuis [UB-Mannheim/tesseract](https://github.com/UB-Mannheim/tesseract/wiki)
2. Installe-le (par défaut : `C:\Program Files\Tesseract-OCR`)
3. Si nécessaire, ajoute dans `app.py` après les imports :
   ```python
   pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
   ```

### 4. Installer et lancer Ollama

```bash
# Télécharge le modèle de vision (première fois : ~4GB)
ollama pull llava:7b
```

---

## 🏃 Lancer l'application

**Terminal 1 — Ollama (doit rester actif) :**

```bash
ollama run llava:7b
```

**Terminal 2 — Application Streamlit :**

```bash
source venv/bin/activate    # Mac/Linux
# venv\Scripts\activate     # Windows
streamlit run app.py
```

L'app s'ouvre automatiquement sur **http://localhost:8501**

### Vérifier l'installation

```bash
python test_setup.py
```

---

## 💡 Utilisation

1. **Upload une image** — Capture d'écran d'un graphique TradingView ou MetaTrader (PNG/JPG)
2. **Traitement automatique** — OCR + Couleurs + IA en ~30-60 secondes
3. **Consulte le rapport** — 4 onglets : Rapport, OCR, Couleurs, IA Visuelle

### Exemples de captures compatibles

- Graphiques de crypto (Bitcoin, Ethereum) sur TradingView
- Graphiques d'actions avec indicateurs (EMA, RSI, MACD)
- Graphiques forex ou commodities

---

## 🔧 Troubleshooting

| Erreur                        | Solution                                                       |
| ----------------------------- | -------------------------------------------------------------- |
| `ModuleNotFoundError`         | `pip install -r requirements.txt`                              |
| `TesseractNotFoundError`      | Installer Tesseract OCR (voir section Installation)            |
| `Connection refused` (Ollama) | Lancer Ollama : `ollama run llava:7b`                          |
| Erreur Tesseract sur Windows  | Configurer le chemin dans `app.py` (voir section Installation) |

---

## 🚀 Améliorations futures

- [ ] Support de TA-lib pour calcul d'indicateurs (RSI, MACD, etc.)
- [ ] Sauvegarde de l'historique d'analyses
- [ ] Intégration API yfinance pour données réelles
- [ ] Reconnaissance de patterns (Head & Shoulders, Double Bottom, etc.)
- [ ] Export des analyses en PDF

---

## 🤝 Contributing

Les contributions sont les bienvenues ! Pour contribuer :

1. Fork le projet
2. Crée une branche (`git checkout -b feature/ma-feature`)
3. Commit tes changements (`git commit -m 'Ajout de ma feature'`)
4. Push (`git push origin feature/ma-feature`)
5. Ouvre une Pull Request

---

## ⚠️ Avertissement légal

Cette application est à titre **éducatif uniquement**. Ne l'utilisez pas comme conseil d'investissement. Toute décision de trading doit être validée par un analyste humain qualifié.

---

## 📚 Ressources

- [Streamlit](https://docs.streamlit.io) — Framework UI
- [OpenCV](https://docs.opencv.org) — Computer Vision
- [Ollama](https://github.com/ollama/ollama) — LLM local
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) — Extraction de texte

## 📝 Licence

Ce projet est sous licence [MIT](LICENSE).

---

**Questions ?** Crée une [issue](https://github.com/Bull1016/trading-analyzer/issues) sur GitHub.
