import requests
import json

MODEL = "mistral"

with open("backend/data.json", "rb+") as file:
    datasets = json.loads(file.read())
    success = 0
    failure = 0

    for dataset in datasets:

        question = dataset["question"]
        options = dataset["options"]

        prompt = f"""
        I want you to act as a spoken English teacher and are answering my multi-choice questions correctly. Choose the answer which is most appropriate.
        
        You will be given a multiple-choice question with four options. Your task is to return **only** the correct answer from the provided options. Do not explain or repeat the question. Just return the correct word or phrase exactly as it appears in the options list.
        
        For example:
        If the question is "Was heißt Katze auf Englisch?" and the options are "cat, dog, tiger, lion", return only: cat
        
        Question: {question}
        Options: {options}
        Answer:"""

        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": MODEL,
                "prompt": prompt,
                "stream": False
            }
        )

        data = response.json()
        answer_ai = data["response"].replace("\"", "").replace("'", "").lower().strip()
        answer_expected = dataset['answer'].replace("\"", "").replace("'", "").lower().strip()

        if answer_expected == answer_ai:
            success += 1
        else:
            failure += 1
            print(prompt)
            print(question)
            print(answer_expected)
            print(answer_ai)
            print('-------')

    print(success)
    print(failure) 