import speech_recognition as sr
import logging
import os
from gtts import gTTS
from google import genai
import streamlit as st
from dotenv import load_dotenv
load_dotenv()

LOG_DIR = "logs"
LOG_FILE_NAME = "application.log"

os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE_PATH = os.path.join(LOG_DIR, LOG_FILE_NAME)

logging.basicConfig(
    filename=LOG_FILE_PATH,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def takeCommand():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening....")
        r.adjust_for_ambient_noise(source, duration=0.5)
        r.pause_threshold = 1
        audio = r.listen(source)
    try:
        print("Recognizing...")
        query = r.recognize_google(audio, language='en-in')
        print(f"User said: {query}\n")
    except Exception as e:
        logging.info(e)
        print("Say that again please")
        return "None"
    return query


def text_to_speech(text):
    ttx = gTTS(text=text, lang="en")
    ttx.save("speech.mp3")


def gemini_model(user_input):
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=user_input
    )
    results = response.text
    return results


def main():
    st.title("Multilingual AI Assistant")
    if st.button("Ask me anything!"):
        with st.spinner("Listening..."):
            text = takeCommand()
            response = gemini_model(text)
            text_to_speech(response)

            audio_file = open("speech.mp3", 'rb')
            audio_bytes = audio_file.read()

            st.text_area(label="Response:", value=response, height=350)
            st.audio(audio_bytes, format='audio/mp3')
            st.download_button(label="Download Speech",
                                data=audio_bytes,
                                file_name="response.mp3",
                                mime="audio/mp3",
                )

main()