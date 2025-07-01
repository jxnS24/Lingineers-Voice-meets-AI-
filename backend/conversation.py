import io
import os
import tempfile

import requests
import pyttsx3
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

VOICE_ID_WINDOWS = 'HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices\\Tokens\\TTS_MS_EN-US_ZIRA_11.0'


def ask_ollama(prompt):
    response = requests.post(
        os.getenv("OLLAMA_URL"),
        json={
            "model": os.getenv("OLLAMA_MODEL"),
            "prompt": """"
                      You are a professional English teacher. We are having a conversation in English.
                      Please pay close attention to my grammar, word choice, and sentence structure.
                      You can correct me if I make mistakes, but do not explain the rules of English.
                      Also carry on the conversation naturally, as if we were having a real chat. 
                      Ask follow-up questions and keep the conversation going.
                      Keep your response short and concise, no more than 3 sentences or 30 words.
                      Only speak English with me and not any other language. Here is my input: """ + prompt,
            "stream": False
        }
    )
    return response.json()["response"]


def speak(text):
    engine = pyttsx3.init()

    voices = engine.getProperty('voices')
    for voice in voices:
        if voice.id == VOICE_ID_WINDOWS:
            engine.setProperty('voice', VOICE_ID_WINDOWS)
            break

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
        tmp_path = tmp_file.name

    engine.save_to_file(text, tmp_path)
    engine.runAndWait()

    with open(tmp_path, "rb") as f:
        audio_data = io.BytesIO(f.read())

    os.remove(tmp_path)

    audio_data.seek(0)

    return audio_data



if __name__ == "__main__":
    exit = False
    while not exit:
        user_input = input("Write your text: ")
        if user_input == "/bye":
            print("Goodbye!")
            speak("Goodbye!")
            exit = True
        ai_response = ask_ollama(user_input)
        print("AI:", ai_response)
        speak(ai_response)
