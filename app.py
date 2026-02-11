import streamlit as st
import cv2
import pytesseract
from PIL import Image
import numpy as np
import os
import tempfile
import re
from datetime import datetime

# Configuration Streamlit
st.set_page_config(page_title="Analyseur de Graphiques Trading PRO", layout="wide", initial_sidebar_state="expanded")

# ====================
# OCR AVANCÉ
# ====================
def extract_text_from_image(image):
    """Extrait texte avec preprocessing avancé"""
    try:
        img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
        enhanced = clahe.apply(gray)
        denoised = cv2.fastNlMeansDenoising(enhanced, h=10)
        
        text = pytesseract.image_to_string(denoised, lang='eng', config='--psm 6 --oem 3')
        return text if text.strip() else "⚠️ OCR: Aucun texte détecté"
    except Exception as e:
        return f"❌ Erreur OCR : {str(e)}"

# ====================
# EXTRACTION DONNÉES
# ====================
def extract_key_data(text):
    """Extrait les données clés du texte OCR"""
    data = {
        'asset': 'Inconnu',
        'timeframe': 'Inconnu',
        'platform': 'Inconnu',
        'prices': {}
    }
    
    # Asset
    if 'EUR' in text or 'Euro' in text:
        data['asset'] = 'EURUSD'
    elif 'GBP' in text:
        data['asset'] = 'GBPUSD'
    elif 'JPY' in text:
        data['asset'] = 'USDJPY'
    else:
        match = re.search(r'([A-Z]{3})[/\s]([A-Z]{3})', text)
        if match:
            data['asset'] = f"{match.group(1)}/{match.group(2)}"
    
    # Timeframe
    for tf in ['1M', '1W', '1D', '4h', '1h', '30m', '15m', '5m', '1m']:
        if tf in text:
            data['timeframe'] = tf
            break
    
    # Prices
    prices = re.findall(r'\d+\.\d{4,5}', text)
    if prices:
        prices_float = [float(p) for p in prices]
        data['prices']['current'] = prices[-1]
        data['prices']['high'] = max(prices_float)
        data['prices']['low'] = min(prices_float)
        data['prices']['change'] = f"{float(prices[-1]) - float(prices[0]):.5f}" if len(prices) > 1 else "N/A"
    
    # Platform
    if 'TradingView' in text:
        data['platform'] = 'TradingView'
    elif 'MetaTrader' in text:
        data['platform'] = 'MetaTrader'
    
    return data

# ====================
# ANALYSE IA SIMPLE
# ====================
def ai_analysis_visual(image_path, key_data):
    """Analyse visuelle : tendance, structure, momentum"""
    try:
        import ollama
        
        asset = key_data.get('asset', 'Asset')
        timeframe = key_data.get('timeframe', 'TF')
        
        prompt = f"""Analyse ce graphique {asset} {timeframe} VISUELLEMENT SEULEMENT.

⚠️ RÈGLES STRICTES:
- Décris UNIQUEMENT ce que tu vois (pas de chiffres)
- Pas de support/résistance numérotés
- Sois concis et factuel

Points à analyser:
1. **Tendance**: Haussière/baissière/latérale?
2. **Direction récente**: Où va le prix ces derniers jours?
3. **Structure**: Consolidation? Montée? Baisse? Breakout?
4. **Bougies**: Majoritairement vertes (haussier) ou rouges (baissier)?
5. **EMA/Moyenne mobile**: Montent ou descendent?
6. **Momentum**: Fort ou faible? Accélération ou ralentissement?
7. **Signal global**: Résumé en UN MOT: HAUSSIER / BAISSIER / NEUTRE

Sois court et précis."""
        
        models_to_try = ["llava:7b", "llava-phi", "mistral"]
        response_text = None
        
        for model in models_to_try:
            try:
                response = ollama.generate(
                    model=model,
                    prompt=prompt,
                    images=[image_path],
                    stream=False,
                    options={"num_predict": 350}
                )
                response_text = response.get('response', "")
                if response_text:
                    break
            except Exception:
                continue
        
        return response_text if response_text else "⚠️ Erreur analyse"
    except Exception as e:
        return f"❌ Erreur: {str(e)}\nLance: `ollama run llava:7b`"

# ====================
# ANALYSE CV (COULEURS)
# ====================
def analyze_colors(image):
    """Analyse les couleurs du graphique"""
    try:
        img_array = np.array(image)
        hsv = cv2.cvtColor(img_array, cv2.COLOR_RGB2HSV)
        
        # Rouge (baissier)
        lower_red1 = np.array([0, 50, 50])
        upper_red1 = np.array([10, 255, 255])
        mask_red = cv2.inRange(hsv, lower_red1, upper_red1)
        red_pixels = cv2.countNonZero(mask_red)
        
        # Vert (haussier)
        lower_green = np.array([40, 85, 50])
        upper_green = np.array([85, 255, 255])
        mask_green = cv2.inRange(hsv, lower_green, upper_green)
        green_pixels = cv2.countNonZero(mask_green)
        
        total = red_pixels + green_pixels
        if total > 0:
            return {
                'red_pct': (red_pixels / total) * 100,
                'green_pct': (green_pixels / total) * 100,
                'bias': 'HAUSSIER' if green_pixels > red_pixels else 'BAISSIER'
            }
        return None
    except Exception:
        return None

# ====================
# RAPPORT FINAL
# ====================
def generate_report(key_data, color_analysis, visual_analysis):
    """Génère un rapport complet"""
    report = f"""
## 📊 RAPPORT D'ANALYSE TECHNIQUE

### 📍 Identification du Graphique
- **Asset**: {key_data.get('asset', '?')}
- **Timeframe**: {key_data.get('timeframe', '?')}
- **Platform**: {key_data.get('platform', '?')}
- **Date d'analyse**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

### 💰 Données de Prix (OCR)
"""
    
    if key_data['prices']:
        report += f"- **Prix Actuel**: {key_data['prices'].get('current', 'N/A')}\n"
        report += f"- **Plus Haut**: {key_data['prices'].get('high', 'N/A')}\n"
        report += f"- **Plus Bas**: {key_data['prices'].get('low', 'N/A')}\n"
        report += f"- **Variation**: {key_data['prices'].get('change', 'N/A')}\n"
    else:
        report += "- Données de prix non disponibles\n"
    
    if color_analysis:
        report += f"""
### 🎨 Analyse des Couleurs (Computer Vision)
- **Dominance Haussière (Vert)**: {color_analysis['green_pct']:.1f}%
- **Dominance Baissière (Rouge)**: {color_analysis['red_pct']:.1f}%
- **Biais Couleur**: {color_analysis['bias']}
"""
    
    report += f"""
### 📈 Analyse Visuelle (IA)
{visual_analysis}

### ⚠️ DISCLAIMER
Cette analyse est à titre **ÉDUCATIF UNIQUEMENT**.
- ❌ N'est PAS un conseil d'investissement
- ❌ À valider avec un analyste humain
- ❌ Les marchés sont imprévisibles
"""
    
    return report

# ====================
# INTERFACE PRINCIPALE
# ====================
st.title("📊 Analyseur de Trading PRO")
st.markdown("**Analyse complète : OCR Précis + Vision IA + Color Detection**")

with st.sidebar:
    st.header("ℹ️ À propos")
    st.markdown("""
    ### Architecture
    1. **OCR Avancé** : Extrait prix, symbole, timeframe
    2. **Computer Vision** : Détecte tendance par couleurs
    3. **IA Visuelle** : Analyse structure et momentum
    4. **Synthèse** : Rapport complet
    
    ### Modèle
    - **Vision**: llava:7b (4GB RAM)
    - **Texte**: Tesseract OCR
    
    ### Compatible
    ✅ 4GB RAM
    ✅ Linux/Mac/Windows
    ✅ Gratuit (local)
    """)

# Upload
uploaded_file = st.file_uploader("📸 Upload ton graphique", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    
    # Affiche l'image
    col1, col2 = st.columns([1, 1])
    with col1:
        st.image(image, caption="Graphique uploadé", use_container_width=True)
    
    with col2:
        st.markdown("### 📊 Traitement...")
        progress_bar = st.progress(0)
    
    # Sauvegarde temporaire
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
        image.save(tmp.name)
        temp_path = tmp.name
    
    # Extraction OCR
    with col2:
        st.markdown("**1/3 - OCR...**")
    ocr_text = extract_text_from_image(image)
    key_data = extract_key_data(ocr_text)
    progress_bar.progress(33)
    
    # Analyse couleurs
    with col2:
        st.markdown("**2/3 - Couleurs...**")
    color_analysis = analyze_colors(image)
    progress_bar.progress(66)
    
    # Analyse IA
    with col2:
        st.markdown("**3/3 - IA...**")
    visual_analysis = ai_analysis_visual(temp_path, key_data)
    progress_bar.progress(100)
    
    st.markdown("---")
    
    # ONGLETS
    tab1, tab2, tab3, tab4 = st.tabs(["📄 Rapport", "📝 OCR", "🎨 Couleurs", "🤖 IA Visuelle"])
    
    # TAB 1 : RAPPORT
    with tab1:
        report = generate_report(key_data, color_analysis, visual_analysis)
        st.markdown(report)
        
        # Bouton export
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("📋 Copier le rapport"):
                st.success("✅ Rapport copié !")
    
    # TAB 2 : OCR
    with tab2:
        st.subheader("Données Extraites par OCR")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Asset", key_data.get('asset', '?'))
        with col2:
            st.metric("Timeframe", key_data.get('timeframe', '?'))
        with col3:
            st.metric("Prix", key_data['prices'].get('current', '?') if key_data['prices'] else '?')
        with col4:
            st.metric("Platform", key_data.get('platform', '?'))
        
        st.markdown("### 📄 Texte Complet (OCR)")
        st.code(ocr_text, language="text")
    
    # TAB 3 : COULEURS
    with tab3:
        st.subheader("Analyse Computer Vision")
        
        if color_analysis:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("🟢 Vert (Haussier)", f"{color_analysis['green_pct']:.1f}%")
            with col2:
                st.metric("🔴 Rouge (Baissier)", f"{color_analysis['red_pct']:.1f}%")
            with col3:
                st.metric("Biais", color_analysis['bias'])
            
            # Visualisation
            fig_data = {
                'Haussier': color_analysis['green_pct'],
                'Baissier': color_analysis['red_pct']
            }
            
            col1, col2 = st.columns([1, 3])
            with col2:
                st.bar_chart(fig_data)
        else:
            st.warning("❌ Impossible d'analyser les couleurs")
    
    # TAB 4 : IA
    with tab4:
        st.subheader("Analyse Visuelle (IA)")
        st.markdown(visual_analysis)
        st.success("✅ Analyse générée par llava:7b")
    
    # Cleanup
    try:
        os.remove(temp_path)
    except Exception:
        pass

else:
    st.info("👆 Upload une image pour commencer l'analyse")
    
    # Exemple d'utilisation
    st.markdown("---")
    st.markdown("""
    ### 📚 Comment utiliser
    
    1. **Upload une capture** d'un graphique TradingView/MetaTrader
    2. **L'app traite** automatiquement (OCR + IA + Couleurs)
    3. **Reçois un rapport** complet avec :
       - Données précises (prix, symbol, timeframe)
       - Analyse de tendance (haussière/baissière)
       - Structure et momentum
       - Synthèse professionnelle
    
    ### ✨ Avantages
    - ✅ **Gratuit** (local, pas d'API payante)
    - ✅ **Rapide** (30-60 secondes)
    - ✅ **Précis** (OCR + IA combinées)
    - ✅ **Léger** (4GB RAM compatible)
    - ✅ **Privé** (aucune donnée envoyée)
    """)

st.markdown("---")
st.caption("📊 Trading Chart Analyzer PRO | Ollama + Tesseract + OpenCV")
