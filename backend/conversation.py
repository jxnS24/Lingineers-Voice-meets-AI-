import requests
import pyttsx3

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "mistral"

def ask_ollama(prompt):
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": OLLAMA_MODEL,
            "prompt": "You are an experienced English teacher and want to help me learn English. Here is my input: " + prompt,
            "stream": False
        }
    )
    return response.json()["response"]

def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

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
