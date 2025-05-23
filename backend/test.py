import random
import json
from pymongo import MongoClient
import chromadb
import requests

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
        Role: You are an experienced English language teacher specializing in personalized learning.
        
        Objective: Based on the learner’s current progress, generate multiple-choice questions to reinforce and assess their understanding.
        
        Instructions:
        - The question must have 1 correct answer and 3 plausible distractors.
        - Questions should be in English and adapted to the learner’s current level of language proficiency.
        - Focus on key areas of learning such as vocabulary, grammar, and sentence structure, as appropriate.
        - Clearly indicate the correct answer.
        - Provide a brief explanation for why the correct answer is right, and why the distractors are incorrect.
        
        Learner Progress:
        {progress}*
        
        Output Format:
        1. [Question text]  
           a) [Option A]  
           b) [Option B]  
           c) [Option C]  
           d) [Option D]  
           Correct answer: [Correct option]  
           Explanation: [Brief explanation]
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


def store_questions_in_vector_db(questions):
    client = chromadb.PersistentClient(path=VECTOR_DB_PATH)
    collection = client.get_or_create_collection(name="questions")
    for idx, q in enumerate(questions):
        # Use Ollama to embed the question
        emb_response = requests.post(
            "http://localhost:11434/api/embeddings",
            json={
                "model": EMBED_MODEL, "prompt": q["question"]}
        )
        emb = emb_response.json()["embedding"]
        collection.add(
            ids=[f"q_{idx}"],
            embeddings=[emb],
            documents=[q["question"]],
            metadatas=[q]
        )


def save_results(user_id, results):
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    db[RESULTS_COLLECTION].insert_one({
        "user_id": user_id,
        "results": results
    })
    client.close()


if __name__ == "__main__":
    user_id = input("Enter your user ID: ")
    progress = get_user_progress(user_id)
    if not progress:
        progress = ['Advanced English Grammar', 'Intermediate Vocabulary', 'Intermediate Sentence Structure']

    questions = generate_question(progress)
    print(questions)
