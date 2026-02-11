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
st.set_page_config(page_title="Analyseur Multi-Timeframe PRO", layout="wide", initial_sidebar_state="expanded")

# ====================
# TIMEFRAMES CONFIG
# ====================
TIMEFRAMES = {
    '1D': {'label': '📅 Daily (1D)', 'icon': '📅', 'role': 'Tendance macro et direction générale du marché'},
    '4H': {'label': '⏰ 4 Heures (4H)', 'icon': '⏰', 'role': 'Tendance intermédiaire et structure de prix'},
    '15m': {'label': '⚡ 15 Minutes (15min)', 'icon': '⚡', 'role': "Timing d'entrée précis et momentum court terme"},
}

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
def extract_key_data(text, forced_timeframe=None):
    """Extrait les données clés du texte OCR"""
    data = {
        'asset': 'Inconnu',
        'timeframe': forced_timeframe or 'Inconnu',
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
    
    # Timeframe (auto-detect si pas forcé)
    if not forced_timeframe:
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
# ANALYSE IA PAR TF
# ====================
def ai_analysis_mtf(image_path, timeframe, role):
    """Analyse visuelle adaptée au timeframe"""
    try:
        import ollama
        
        prompt = f"""Analyse ce graphique de trading en timeframe {timeframe}.

Contexte: Ce graphique montre la vue {timeframe}. Son rôle dans l'analyse multi-timeframe est: {role}.

⚠️ RÈGLES STRICTES:
- Décris UNIQUEMENT ce que tu vois visuellement
- Pas de chiffres inventés ni de niveaux de prix
- Sois concis et factuel

Points à analyser pour le {timeframe}:
1. **Tendance**: Haussière/baissière/latérale?
2. **Direction récente**: Mouvement dominant visible?
3. **Structure**: Consolidation? Impulsion? Breakout? Range?
4. **Bougies**: Majoritairement vertes ou rouges?
5. **Moyennes mobiles**: Direction des EMA/MA si visibles?
6. **Momentum**: Fort ou faible? En accélération?
7. **Signal {timeframe}**: UN MOT: HAUSSIER / BAISSIER / NEUTRE

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
                    options={"num_predict": 400}
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
# SYNTHÈSE MTF (IA)
# ====================
def generate_mtf_synthesis(analyses):
    """Génère une synthèse multi-timeframe via IA"""
    try:
        import ollama
        
        prompt = f"""Tu es un analyste technique expert. Voici les analyses de 3 timeframes différents pour le même actif.

=== ANALYSE DAILY (1D) — Tendance macro ===
{analyses['1D']['visual']}
Biais couleur 1D: {analyses['1D']['color_bias']}

=== ANALYSE 4H — Tendance intermédiaire ===
{analyses['4H']['visual']}
Biais couleur 4H: {analyses['4H']['color_bias']}

=== ANALYSE 15min — Timing d'entrée ===
{analyses['15m']['visual']}
Biais couleur 15min: {analyses['15m']['color_bias']}

En te basant UNIQUEMENT sur ces 3 analyses, donne ta synthèse multi-timeframe:

1. **Alignement des timeframes**: Les 3 TF pointent-ils dans la même direction?
2. **Confluence**: Le signal est-il cohérent entre les TF?
3. **Signal global**: ACHETER / VENDRE / ATTENDRE
4. **Force du signal**: Fort (3/3 alignés) / Moyen (2/3 alignés) / Faible (1/3 ou contradictoire)
5. **Recommandation**: Résumé concis de l'action à envisager

⚠️ Rappel: Ceci est à titre ÉDUCATIF UNIQUEMENT, pas un conseil d'investissement.

Sois concis et structuré."""
        
        models_to_try = ["llava:7b", "llava-phi", "mistral"]
        response_text = None
        
        for model in models_to_try:
            try:
                response = ollama.generate(
                    model=model,
                    prompt=prompt,
                    stream=False,
                    options={"num_predict": 500}
                )
                response_text = response.get('response', "")
                if response_text:
                    break
            except Exception:
                continue
        
        return response_text if response_text else "⚠️ Impossible de générer la synthèse MTF"
    except Exception as e:
        return f"❌ Erreur synthèse: {str(e)}"

# ====================
# RAPPORT MTF
# ====================
def generate_mtf_report(analyses, synthesis):
    """Génère le rapport multi-timeframe complet"""
    
    # Déterminer l'asset (prendre le premier trouvé)
    asset = 'Inconnu'
    platform = 'Inconnu'
    for tf in ['1D', '4H', '15m']:
        if analyses[tf]['key_data']['asset'] != 'Inconnu':
            asset = analyses[tf]['key_data']['asset']
            break
    for tf in ['1D', '4H', '15m']:
        if analyses[tf]['key_data']['platform'] != 'Inconnu':
            platform = analyses[tf]['key_data']['platform']
            break
    
    # Signal de confluence
    biases = [analyses[tf]['color_bias'] for tf in ['1D', '4H', '15m']]
    haussier_count = biases.count('HAUSSIER')
    baissier_count = biases.count('BAISSIER')
    
    if haussier_count == 3:
        confluence = "🟢 FORTE CONFLUENCE HAUSSIÈRE (3/3)"
    elif baissier_count == 3:
        confluence = "🔴 FORTE CONFLUENCE BAISSIÈRE (3/3)"
    elif haussier_count == 2:
        confluence = "🟡 CONFLUENCE MODÉRÉE HAUSSIÈRE (2/3)"
    elif baissier_count == 2:
        confluence = "🟡 CONFLUENCE MODÉRÉE BAISSIÈRE (2/3)"
    else:
        confluence = "⚪ PAS DE CONFLUENCE — SIGNAL MIXTE"
    
    report = f"""
## 📊 RAPPORT MULTI-TIMEFRAME

### 📍 Identification
- **Asset**: {asset}
- **Platform**: {platform}
- **Date d'analyse**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Timeframes analysés**: 1D · 4H · 15min

---

### 🎯 Signal de Confluence (Couleurs)
**{confluence}**

| Timeframe | Biais Couleur | Vert | Rouge |
|-----------|--------------|------|-------|
| 📅 1D | {analyses['1D']['color_bias']} | {analyses['1D']['color_green']:.1f}% | {analyses['1D']['color_red']:.1f}% |
| ⏰ 4H | {analyses['4H']['color_bias']} | {analyses['4H']['color_green']:.1f}% | {analyses['4H']['color_red']:.1f}% |
| ⚡ 15min | {analyses['15m']['color_bias']} | {analyses['15m']['color_green']:.1f}% | {analyses['15m']['color_red']:.1f}% |

---

### 🧠 Synthèse IA Multi-Timeframe
{synthesis}

---

### ⚠️ DISCLAIMER
Cette analyse est à titre **ÉDUCATIF UNIQUEMENT**.
- ❌ N'est PAS un conseil d'investissement
- ❌ À valider avec un analyste humain
- ❌ Les marchés sont imprévisibles
"""
    
    return report

# ====================
# TRAITEMENT D'UN TF
# ====================
def process_timeframe(image, tf_key, progress_callback=None):
    """Traite un timeframe complet : OCR + Couleurs + IA"""
    tf_config = TIMEFRAMES[tf_key]
    result = {}
    
    # OCR
    ocr_text = extract_text_from_image(image)
    result['ocr_text'] = ocr_text
    result['key_data'] = extract_key_data(ocr_text, forced_timeframe=tf_key)
    
    # Couleurs
    color = analyze_colors(image)
    if color:
        result['color_bias'] = color['bias']
        result['color_green'] = color['green_pct']
        result['color_red'] = color['red_pct']
        result['color_data'] = color
    else:
        result['color_bias'] = 'N/A'
        result['color_green'] = 0.0
        result['color_red'] = 0.0
        result['color_data'] = None
    
    # IA visuelle
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
        image.save(tmp.name)
        temp_path = tmp.name
    
    result['visual'] = ai_analysis_mtf(temp_path, tf_key, tf_config['role'])
    
    # Cleanup
    try:
        os.remove(temp_path)
    except Exception:
        pass
    
    return result

# ====================
# INTERFACE PRINCIPALE
# ====================
st.title("📊 Analyseur Multi-Timeframe PRO")
st.markdown("**Analyse complète : 3 Timeframes × (OCR + Vision IA + Couleurs) → Synthèse MTF**")

with st.sidebar:
    st.header("ℹ️ À propos")
    st.markdown("""
    ### Analyse Multi-Timeframe
    Upload **3 graphiques** du même actif :
    1. **📅 1D** → Tendance macro
    2. **⏰ 4H** → Structure intermédiaire
    3. **⚡ 15min** → Timing d'entrée
    
    ### Pipeline par graphique
    1. **OCR** : Extrait prix, symbole
    2. **Couleurs** : Détecte tendance
    3. **IA** : Analyse structure
    
    ### Synthèse finale
    L'IA croise les 3 analyses pour donner :
    - Signal de **confluence**
    - Recommandation globale
    
    ### Modèle
    - **Vision**: llava:7b
    - **Texte**: Tesseract OCR
    
    ### Compatible
    ✅ 4GB RAM · ✅ Local · ✅ Gratuit
    """)

# ====================
# UPLOAD 3 IMAGES
# ====================
st.subheader("📸 Upload tes 3 graphiques")

col1, col2, col3 = st.columns(3)

with col1:
    file_1d = st.file_uploader("📅 Graphique Daily (1D)", type=["png", "jpg", "jpeg"], key="tf_1d")
    if file_1d:
        img_1d = Image.open(file_1d)
        st.image(img_1d, caption="📅 Daily (1D)", use_container_width=True)

with col2:
    file_4h = st.file_uploader("⏰ Graphique 4 Heures (4H)", type=["png", "jpg", "jpeg"], key="tf_4h")
    if file_4h:
        img_4h = Image.open(file_4h)
        st.image(img_4h, caption="⏰ 4H", use_container_width=True)

with col3:
    file_15m = st.file_uploader("⚡ Graphique 15 Minutes", type=["png", "jpg", "jpeg"], key="tf_15m")
    if file_15m:
        img_15m = Image.open(file_15m)
        st.image(img_15m, caption="⚡ 15min", use_container_width=True)

# ====================
# TRAITEMENT
# ====================
if file_1d and file_4h and file_15m:
    images = {
        '1D': Image.open(file_1d),
        '4H': Image.open(file_4h),
        '15m': Image.open(file_15m),
    }
    
    st.markdown("---")
    
    # Bouton d'analyse
    if st.button("🚀 Lancer l'analyse Multi-Timeframe", type="primary", use_container_width=True):
        
        analyses = {}
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Traitement de chaque timeframe
        tf_keys = ['1D', '4H', '15m']
        for i, tf in enumerate(tf_keys):
            tf_label = TIMEFRAMES[tf]['label']
            status_text.markdown(f"**Analyse en cours : {tf_label}** ({i+1}/3)")
            
            analyses[tf] = process_timeframe(images[tf], tf)
            progress_bar.progress(int((i + 1) / 4 * 100))
        
        # Synthèse MTF
        status_text.markdown("**🧠 Synthèse Multi-Timeframe en cours...**")
        synthesis = generate_mtf_synthesis(analyses)
        progress_bar.progress(100)
        status_text.markdown("**✅ Analyse terminée !**")
        
        st.markdown("---")
        
        # ====================
        # ONGLETS RÉSULTATS
        # ====================
        tab_report, tab_1d, tab_4h, tab_15m = st.tabs([
            "📊 Rapport MTF",
            "📅 Daily (1D)",
            "⏰ 4H",
            "⚡ 15min"
        ])
        
        # TAB : RAPPORT MTF
        with tab_report:
            report = generate_mtf_report(analyses, synthesis)
            st.markdown(report)
        
        # Tabs individuels par timeframe
        tf_tabs = {'1D': tab_1d, '4H': tab_4h, '15m': tab_15m}
        
        for tf, tab in tf_tabs.items():
            with tab:
                tf_config = TIMEFRAMES[tf]
                data = analyses[tf]
                
                st.subheader(f"{tf_config['icon']} Analyse {tf_config['label']}")
                
                # Image + Métriques
                col_img, col_data = st.columns([1, 1])
                
                with col_img:
                    st.image(images[tf], caption=tf_config['label'], use_container_width=True)
                
                with col_data:
                    # Métriques OCR
                    st.markdown("#### 📝 Données OCR")
                    m1, m2 = st.columns(2)
                    with m1:
                        st.metric("Asset", data['key_data'].get('asset', '?'))
                        st.metric("Prix", data['key_data']['prices'].get('current', '?') if data['key_data']['prices'] else '?')
                    with m2:
                        st.metric("Timeframe", data['key_data'].get('timeframe', '?'))
                        st.metric("Platform", data['key_data'].get('platform', '?'))
                    
                    # Couleurs
                    st.markdown("#### 🎨 Couleurs")
                    if data['color_data']:
                        c1, c2, c3 = st.columns(3)
                        with c1:
                            st.metric("🟢 Vert", f"{data['color_green']:.1f}%")
                        with c2:
                            st.metric("🔴 Rouge", f"{data['color_red']:.1f}%")
                        with c3:
                            st.metric("Biais", data['color_bias'])
                    else:
                        st.warning("Couleurs non détectées")
                
                # Analyse IA
                st.markdown("#### 🤖 Analyse IA")
                st.markdown(data['visual'])
                
                # OCR brut
                with st.expander("📄 Texte OCR brut"):
                    st.code(data['ocr_text'], language="text")

elif file_1d or file_4h or file_15m:
    # Au moins une image mais pas les 3
    missing = []
    if not file_1d:
        missing.append("📅 Daily (1D)")
    if not file_4h:
        missing.append("⏰ 4H")
    if not file_15m:
        missing.append("⚡ 15min")
    
    st.warning(f"⏳ Il manque encore : **{', '.join(missing)}**")

else:
    st.info("👆 Upload tes 3 graphiques (1D, 4H, 15min) pour commencer l'analyse multi-timeframe")
    
    st.markdown("---")
    st.markdown("""
    ### 📚 Comment utiliser
    
    1. **Upload 3 captures** du **même actif** sur TradingView/MetaTrader :
       - 📅 **Daily (1D)** : pour la tendance macro
       - ⏰ **4H** : pour la structure intermédiaire
       - ⚡ **15min** : pour le timing d'entrée
    2. **Clique sur "Lancer l'analyse"** — traitement ~1-3 min
    3. **Consulte le rapport MTF** avec signal de confluence
    
    ### 🎯 Pourquoi le Multi-Timeframe ?
    
    L'analyse MTF est utilisée par les traders professionnels :
    - **1D** confirme la direction générale
    - **4H** montre la structure et les niveaux clés
    - **15min** donne le timing précis d'entrée
    - Quand les **3 TF s'alignent** → signal fort 🟢
    
    ### ✨ Avantages
    - ✅ **Gratuit** (local, pas d'API payante)
    - ✅ **Multi-Timeframe** (3 graphiques analysés)
    - ✅ **Confluence IA** (synthèse automatique)
    - ✅ **Privé** (aucune donnée envoyée)
    """)

st.markdown("---")
st.caption("📊 Trading Chart Analyzer PRO — Multi-Timeframe | Ollama + Tesseract + OpenCV")
