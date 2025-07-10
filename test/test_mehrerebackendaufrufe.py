import requests

url = "http://localhost:8000/multiple-choice/123"

for i in range(20):
    response = requests.get(url)
    print(f"Request {i + 1}: Status Code {response.status_code}")
    print(response.text)