import io
import os
import logging

import streamlit as st
import speech_recognition as sr
from gtts import gTTS
from google import genai
from dotenv import load_dotenv

load_dotenv()

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)
logging.basicConfig(
    filename=os.path.join(LOG_DIR, "application.log"),
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

MODEL_NAME = "gemini-2.5-flash" 
LANGUAGES = {
    "English": ("en-IN", "en"),
    "Hindi": ("hi-IN", "hi"),
}


def get_api_key():
   
    try:
        return st.secrets["GEMINI_API_KEY"]
    except Exception:
        return os.getenv("GEMINI_API_KEY")


def transcribe(audio_file, language_code):
    r = sr.Recognizer()
    with sr.AudioFile(audio_file) as source:
        audio = r.record(source)
    try:
        return r.recognize_google(audio, language=language_code)
    except Exception as e:
        logging.info(e)
        return None


def gemini_model(user_input):
    api_key = get_api_key()
    if not api_key:
        raise ValueError("GEMINI_API_KEY set nahi hai")
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(model=MODEL_NAME, contents=user_input)
    return response.text


def text_to_speech(text, lang="en"):
    fp = io.BytesIO()
    gTTS(text=text, lang=lang).write_to_fp(fp)   
    return fp.getvalue()


def main():
    st.title("Multilingual AI Assistant")

    language = st.selectbox("Language", list(LANGUAGES.keys()))
    sr_code, tts_code = LANGUAGES[language]

    user_text = st.text_input("Type your question")
    voice = st.audio_input("Or record your question")

    question = None
    if user_text:
        question = user_text
    elif voice is not None:
        with st.spinner("Recognizing..."):
            question = transcribe(voice, sr_code)
        if question:
            st.write(f"**You said:** {question}")
        else:
            st.warning("Samajh nahi aaya, dobara bolo.")

    if question:
        try:
            with st.spinner("Thinking..."):
                answer = gemini_model(question)
            st.write("**Assistant:**", answer)
            st.audio(text_to_speech(answer, tts_code), format="audio/mp3")
        except Exception as e:
            logging.error(e)
            st.error(f"Error: {e}")


main()