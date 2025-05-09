import requests

MODEL = "mistral"

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
print(data)