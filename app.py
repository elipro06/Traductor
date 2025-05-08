import os
import streamlit as st
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
from PIL import Image
import time
import glob
from gtts import gTTS
from googletrans import Translator

st.markdown(
    """
    <style>
        .stApp {
            background-color: #f0f2f6;
            color: #1F3B4D;
        }
        h1 {
            color: #1F3B4D !important;
            text-align: center;
        }
        h2, h3, h4, h5, h6, label, span, div {
            color: #3a3a3a !important;
        }
        .bk-btn {
            background-color: #28C76F !important;
            color: white !important;
            border: none !important;
            font-size: 18px !important;
            padding: 10px 20px !important;
            border-radius: 8px !important;
        }
        .stButton>button {
            background-color: #28C76F !important;
            color: white !important;
            font-size: 16px !important;
            border-radius: 8px;
            border: none;
        }
        .stSelectbox, .stTextInput {
            background-color: white;
            color: #1F3B4D;
            border-radius: 6px;
        }
        .css-1aumxhk {
            background-color: white !important;
        }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown('<h1>🧙‍♂️ Traductor Mágico</h1>', unsafe_allow_html=True)
st.subheader("¡Habla y deja que la magia de los idiomas ocurra!")

try:
    image = Image.open("traductor.png")
    st.image(image, caption='¡Diviértete con tus traducciones!', use_column_width=True)
except:
    st.warning("No se encontró la imagen 'traductor.png'.")

with st.sidebar:
    st.subheader("🔧 Configuración del Traductor")
    st.write("Presiona el botón para hablar y selecciona los idiomas deseados.")

st.write("Haz clic en el botón para comenzar:")

stt_button = Button(label="🎤 ¡Hablar!", width=350, height=60)
stt_button.js_on_event("button_click", CustomJS(code="""
    var recognition = new webkitSpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.onresult = function (e) {
        var value = "";
        for (var i = e.resultIndex; i < e.results.length; ++i) {
            if (e.results[i].isFinal) {
                value += e.results[i][0].transcript;
            }
        }
        if (value != "") {
            document.dispatchEvent(new CustomEvent("GET_TEXT", {detail: value}));
        }
    }
    recognition.start();
"""))

result = streamlit_bokeh_events(
    stt_button,
    events="GET_TEXT",
    key="listen",
    refresh_on_update=False,
    override_height=75,
    debounce_time=0
)

if result and "GET_TEXT" in result:
    text = result.get("GET_TEXT")
    st.success(f"Texto detectado: {text}")
    os.makedirs("temp", exist_ok=True)
    translator = Translator()

    lang_dict = {
        "Inglés": "en",
        "Español": "es",
        "Francés": "fr",
        "Alemán": "de",
        "Italiano": "it",
        "Japonés": "ja"
    }

    in_lang = st.selectbox("Idioma de entrada", list(lang_dict.keys()))
    out_lang = st.selectbox("Idioma de salida", list(lang_dict.keys()))

    input_language = lang_dict[in_lang]
    output_language = lang_dict[out_lang]

    def text_to_speech(input_language, output_language, text):
        translation = translator.translate(text, src=input_language, dest=output_language)
        trans_text = translation.text
        tts = gTTS(trans_text, lang=output_language, slow=False)
        filename = f"temp/{text[:20].strip().replace(' ', '_')}.mp3"
        tts.save(filename)
        return filename, trans_text

    if st.checkbox("Mostrar texto traducido"):
        show_text = True
    else:
        show_text = False

    if st.button("🔊 Convertir a Audio"):
        audio_path, output_text = text_to_speech(input_language, output_language, text)
        with open(audio_path, "rb") as audio_file:
            st.markdown("### 🔈 Reproducción del audio:")
            st.audio(audio_file.read(), format="audio/mp3")
        if show_text:
            st.markdown("### 📄 Texto traducido:")
            st.write(output_text)

    def remove_files(days_old):
        now = time.time()
        for f in glob.glob("temp/*.mp3"):
            if os.stat(f).st_mtime < now - days_old * 86400:
                os.remove(f)

    remove_files(7)
