import streamlit as st
from textblob import TextBlob
from deep_translator import GoogleTranslator
from gtts import gTTS
from io import BytesIO
import re

# ==============================
# 🎨 Selector de tema visual
# ==============================
modo_color = st.sidebar.radio("🎨 Tema visual", ["Claro", "Oscuro"])

if modo_color == "Oscuro":
    st.markdown("""
        <style>
        .stApp {
            background-color: #0e1117;
            color: white;
        }
        .stMarkdown, .stTextInput, .stTextArea, .stSubheader, .stSelectbox, .stRadio, .stCheckbox {
            color: white !important;
        }
        div[data-testid="stMarkdownContainer"] p, h1, h2, h3, h4, h5, h6 {
            color: white !important;
        }
        .stTextInput > div > div > input, .stTextArea textarea {
            background-color: #262730;
            color: white;
            border: 1px solid #40414f;
        }
        </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
        <style>
        .stApp {
            background-color: #ffffff;
            color: #000000;
        }
        .stTextInput > div > div > input, .stTextArea textarea {
            background-color: #f5f5f5;
            color: black;
            border: 1px solid #cccccc;
        }
        </style>
    """, unsafe_allow_html=True)

# ==============================
# 🧠 Encabezado
# ==============================
st.title("🧠 Análisis de texto inteligente")
st.write("Analiza sentimientos, subjetividad y traducción de tus textos con una interfaz sencilla.")

# ==============================
# 📘 Funciones
# ==============================
def contar_palabras(texto):
    stop_words = set(["de", "la", "y", "el", "en", "que", "a", "los", "se", "del", "por", "las", "un", "una", "con", "no", "es", "para", "su", "al"])
    palabras = re.findall(r'\b\w+\b', texto.lower())
    palabras_filtradas = [p for p in palabras if p not in stop_words and len(p) > 2]
    contador = {}
    for palabra in palabras_filtradas:
        contador[palabra] = contador.get(palabra, 0) + 1
    return dict(sorted(contador.items(), key=lambda x: x[1], reverse=True))

def traducir_texto(texto):
    try:
        return GoogleTranslator(source='auto', target='en').translate(texto)
    except Exception as e:
        st.error(f"Error al traducir: {e}")
        return texto

def procesar_texto(texto):
    texto_traducido = traducir_texto(texto)
    blob = TextBlob(texto_traducido)
    sentimiento = blob.sentiment.polarity
    subjetividad = blob.sentiment.subjectivity
    contador = contar_palabras(texto)
    return texto_traducido, sentimiento, subjetividad, contador

# ==============================
# ✍️ Interacción principal
# ==============================
texto = st.text_area("✏️ Escribe o pega un texto para analizar:", height=180, placeholder="Ejemplo: Me encanta aprender sobre inteligencia artificial.")

if st.button("🔍 Analizar texto"):
    if texto.strip():
        with st.spinner("Analizando..."):
            traducido, sentimiento, subjetividad, contador = procesar_texto(texto)

        st.subheader("Resultados del análisis")
        st.write(f"**Traducción al inglés:** {traducido}")
        st.write(f"**Sentimiento:** {sentimiento:.2f}")
        st.write(f"**Subjetividad:** {subjetividad:.2f}")

        if sentimiento > 0.3:
            st.success("😊 Sentimiento positivo")
        elif sentimiento < -0.3:
            st.error("😔 Sentimiento negativo")
        else:
            st.info("😐 Sentimiento neutral")

        st.bar_chart(dict(list(contador.items())[:10]))

        # 🔊 Interacción de voz
        if st.checkbox("🔊 Escuchar resultado"):
            mensaje = (
                "El sentimiento del texto es positivo."
                if sentimiento > 0.3 else
                "El sentimiento del texto es negativo."
                if sentimiento < -0.3 else
                "El sentimiento del texto es neutral."
            )
            tts = gTTS(mensaje, lang="es")
            audio_bytes = BytesIO()
            tts.write_to_fp(audio_bytes)
            st.audio(audio_bytes.getvalue(), format="audio/mp3")
    else:
        st.warning("Por favor, ingresa algún texto para analizar.")

# ==============================
# ℹ️ Información
# ==============================
with st.expander("📘 Información sobre el análisis"):
    st.markdown("""
    - **Sentimiento**: de -1 (muy negativo) a 1 (muy positivo).  
    - **Subjetividad**: de 0 (muy objetivo) a 1 (muy subjetivo).  
    - **Librerías usadas:**  
      - TextBlob 🧠  
      - Deep Translator 🌍  
      - gTTS 🔊  
    """)

st.markdown("---")
st.caption("Desarrollado con 💖 usando Streamlit y Python")
