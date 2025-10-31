import streamlit as st
import re
from textblob import TextBlob
from deep_translator import GoogleTranslator
from gtts import gTTS
import base64
import os
import tempfile

st.set_page_config(page_title="Análisis de Texto", page_icon="🧠", layout="wide")

# --- Estilo visual ---
st.markdown("""
<style>
body, [class*="st-"], .stMarkdown, .stTextInput>div>div>input, textarea {
    color: white !important;
    background-color: #101018 !important;
    font-family: "Poppins", sans-serif;
}
h1, h2, h3, h4, h5, h6 {
    color: #d32f2f;
}
section[data-testid="stSidebar"] {
    background-color: #181820 !important;
    color: white !important;
}
.stButton>button {
    background-color: #d32f2f !important;
    color: white !important;
    border-radius: 6px !important;
}
.stButton>button:hover {
    background-color: #b71c1c !important;
}
</style>
""", unsafe_allow_html=True)

# --- Función para contar palabras ---
def contar_palabras(texto):
    stop_words = set(["el", "la", "los", "las", "y", "o", "a", "de", "que", "es", "en", "the", "and", "to", "of", "for"])
    palabras = re.findall(r'\b\w+\b', texto.lower())
    palabras_filtradas = [p for p in palabras if p not in stop_words and len(p) > 2]
    contador = {}
    for palabra in palabras_filtradas:
        contador[palabra] = contador.get(palabra, 0) + 1
    return dict(sorted(contador.items(), key=lambda x: x[1], reverse=True))

# --- Traducción estable ---
def traducir_texto(texto):
    try:
        return GoogleTranslator(source='auto', target='en').translate(texto)
    except Exception:
        return texto

# --- Análisis principal ---
def procesar_texto(texto):
    texto_traducido = traducir_texto(texto)
    blob = TextBlob(texto_traducido)
    sentimiento = blob.sentiment.polarity
    subjetividad = blob.sentiment.subjectivity
    contador_palabras = contar_palabras(texto_traducido)
    return {
        "texto_original": texto,
        "texto_traducido": texto_traducido,
        "sentimiento": sentimiento,
        "subjetividad": subjetividad,
        "contador": contador_palabras
    }

# --- Visualizaciones y resultados ---
def crear_visualizaciones(resultados):
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🔍 Sentimiento y Subjetividad")
        st.progress((resultados["sentimiento"] + 1) / 2)
        if resultados["sentimiento"] > 0.05:
            st.success(f"😊 Positivo ({resultados['sentimiento']:.2f})")
        elif resultados["sentimiento"] < -0.05:
            st.error(f"😔 Negativo ({resultados['sentimiento']:.2f})")
        else:
            st.info(f"😐 Neutral ({resultados['sentimiento']:.2f})")

        st.progress(resultados["subjetividad"])
        if resultados["subjetividad"] > 0.5:
            st.warning(f"💭 Alta subjetividad ({resultados['subjetividad']:.2f})")
        else:
            st.info(f"📋 Baja subjetividad ({resultados['subjetividad']:.2f})")

    with col2:
        st.subheader("📊 Palabras más frecuentes")
        top_palabras = dict(list(resultados["contador"].items())[:10])
        st.bar_chart(top_palabras)

    with st.expander("🌍 Ver texto traducido"):
        colA, colB = st.columns(2)
        with colA:
            st.markdown("**Texto Original:**")
            st.text(resultados["texto_original"])
        with colB:
            st.markdown("**Texto Traducido:**")
            st.text(resultados["texto_traducido"])

# --- Interfaz principal ---
st.title("🧠 Análisis de Texto con TextBlob")
st.sidebar.header("Opciones de análisis")
modo = st.sidebar.radio("Modo de entrada", ["Texto directo", "Archivo de texto"])

if modo == "Texto directo":
    texto = st.text_area("✏️ Escribe o pega tu texto aquí:", height=180)
    if st.button("Analizar texto"):
        if texto.strip():
            with st.spinner("Analizando texto..."):
                res = procesar_texto(texto)
                crear_visualizaciones(res)

                # Interacción: ofrecer resumen hablado
                if st.toggle("🔊 Escuchar resumen del análisis"):
                    resumen = (
                        f"El texto tiene un sentimiento de {res['sentimiento']:.2f} "
                        f"y una subjetividad de {res['subjetividad']:.2f}. "
                        "Las palabras más frecuentes son: "
                        + ", ".join(list(res['contador'].keys())[:5]) + "."
                    )
                    tts = gTTS(resumen, lang='es')
                    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
                    tts.save(tmp.name)
                    audio_bytes = open(tmp.name, "rb").read()
                    st.audio(audio_bytes, format="audio/mp3")
        else:
            st.warning("Por favor, escribe algo antes de analizar.")

elif modo == "Archivo de texto":
    archivo = st.file_uploader("📁 Carga tu archivo de texto", type=["txt", "csv", "md"])
    if archivo is not None:
        contenido = archivo.getvalue().decode("utf-8")
        st.text_area("Vista previa:", contenido[:800], height=200)
        if st.button("Analizar archivo"):
            with st.spinner("Analizando..."):
                res = procesar_texto(contenido)
                crear_visualizaciones(res)

# --- Info ---
with st.expander("ℹ️ Acerca del análisis"):
    st.markdown("""
    **Polaridad:** mide si el texto es positivo (1), negativo (-1) o neutral (0).  
    **Subjetividad:** mide si el texto expresa opiniones (1) o hechos (0).  
    Usa `TextBlob` para el análisis semántico y `deep_translator` para traducción automática.  
    """)

st.markdown("---")
st.caption("Desarrollado con ❤️ por Khiara usando Streamlit + TextBlob")
