import json

from pymongo import MongoClient
import chromadb
import requests
import ollama

# --- Config ---
MONGO_URI = "mongodb://root:example@localhost:27017/"
DB_NAME = "lingineers"
USER_COLLECTION = "user-progress"
RESULTS_COLLECTION = "results"
VECTOR_DB_PATH = "./vector_db"
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "mistral"
EMBED_MODEL = "mxbai-embed-large"


def get_user_progress(user_id):
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    progress = list(db[USER_COLLECTION].find({"user_id": user_id}).limit(3)) or []
    client.close()
    return progress


def generate_question(progress):
    print('Asking Ollama to generate questions...')
    prompt = f"""
        Role: You are an experienced English language teacher with expertise in adaptive, level-based instruction.
        
        Objective: Create a multiple-choice question tailored to the learner’s current level to reinforce and assess understanding.
        
        Guidelines:
        - Each question must include exactly 4 answer options (1 correct, 3 plausible distractors).
        - Use clear, level-appropriate English based on the learner’s progress.
        - Target key language areas: vocabulary, grammar, sentence structure (choose as appropriate).
        - Avoid repetition in distractors and ensure they are grammatically plausible.
        - Questions must be self-contained and unambiguous.
        - Highlight the correct answer and provide a concise explanation for:
            - Why the correct answer is right.
            - Why each distractor is incorrect.
        
        Learner Profile:
        {progress}
        
        Output Format:
        Provide the question in JSON format with the following structure:
         {{
            "question": "Your question here?",
            "options": [
                {{"text": "Option A", "is_correct": true}},
                {{"text": "Option B", "is_correct": false}},
                {{"text": "Option C", "is_correct": false}},
                {{"text": "Option D", "is_correct": false}}
            ], 
            "explanation": "Explain why the correct answer is right and why the others are wrong."
        }}
        """

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False
        }
    )

    return response.json()['response']


def store_question_in_vector_db(question):
    client = chromadb.PersistentClient(path=VECTOR_DB_PATH)
    collection = client.get_or_create_collection(name="questions")
    embeddings = ollama.embed(EMBED_MODEL, input=question)["embeddings"]

    question = json.loads(question)

    metadatas = {
        "question": question["question"],
        "options": json.dumps(question["options"]),
        "explanation": question["explanation"]
    }

    collection.add(
        ids=[str(hash(question["question"]))],
        embeddings=embeddings,
        metadatas=[metadatas],
        documents=["question"],
    )


# Save user progress
def save_results(user_id, results):
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    db[RESULTS_COLLECTION].insert_one({
        "user_id": user_id,
        "results": results
    })
    client.close()

if __name__ == "__main__":
    # user_id = input("Enter your user ID: ")
    progress = get_user_progress('123')
    if not progress:
        progress = ['Advanced English Grammar', 'Intermediate Vocabulary', 'Intermediate Sentence Structure']

    question = generate_question(progress)
    print(question)
    store_question_in_vector_db(question)
