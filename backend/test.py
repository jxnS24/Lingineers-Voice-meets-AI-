import requests

MODEL = "mistral:7b"

prompt = "Hello how are you"

response = requests.post(
    "http://localhost:11434/api/generate",
    json={
        "model": MODEL,
        "prompt": prompt,
        "stream": False
    }
)

data = response.json()
print(data["response"])