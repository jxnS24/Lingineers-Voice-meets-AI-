import json
import os
from dotenv import load_dotenv, find_dotenv
from pymongo import MongoClient
import chromadb
import requests
import ollama

load_dotenv(find_dotenv())


def get_user_progress(user_id):
    with MongoClient(os.getenv("MONGO_URI")) as client:
        db = client[os.getenv("DB_NAME")]
        return list(db[os.getenv("USER_PROGRESS_COLLECTION")].find({"user_id": user_id}).sort("_id", -1).limit(3)) or []


def generate_vocab_question(progress):
    prompt = f"""
        Role: You are a German teacher. 
        Objective: Give a single German word (noun, verb, or adjective) appropriate for the learner's level, and its English translation.
        Orientation to the learner's level is crucial.
        Choose words from different topics, such as food, travel, or daily life.
        Output valid JSON: {{"german": "Haus", "english": "house"}}
        Learner Profile: {progress}
    """
    response = requests.post(
        os.getenv("OLLAMA_URL"),
        json={
            "model": os.getenv("OLLAMA_MODEL"),
            "prompt": prompt,
            "stream": False
        }
    )
    return response.json()['response']


def store_vocab_in_vector_db(vocab_json):
    client = chromadb.PersistentClient(path=os.getenv("VECTOR_DB_PATH"))
    collection = client.get_or_create_collection(name="vocab")
    vocab = json.loads(vocab_json)
    embeddings = ollama.embed(os.getenv("EMBED_MODEL"), input=vocab["german"])["embeddings"]
    metadatas = {
        "german": vocab["german"],
        "english": vocab["english"]
    }
    collection.add(
        ids=[str(hash(vocab["german"]))],
        embeddings=embeddings,
        metadatas=[metadatas],
        documents=[vocab["german"]],
    )


def save_vocab(user_id, vocab, learning_path_id=""):
    with MongoClient(os.getenv("MONGO_URI")) as client:
        db = client[os.getenv("DB_NAME")]
        db[os.getenv("USER_PROGRESS_VOCAB_COLLECTION")].insert_one({
            "learning_path_id": learning_path_id,
            "user_id": user_id,
            "german": vocab["german"],
            "english": vocab["english"]
        })


def save_results(user_id, vocab, user_answer, correct, learning_path_id):
    with MongoClient(os.getenv("MONGO_URI")) as client:
        db = client[os.getenv("DB_NAME")]
        data = {
            "learning_path_id": learning_path_id,
            "user_id": user_id,
            "german": vocab["german"],
            "expected_english": vocab["english"],
            "user_answer": user_answer,
            "is_correct": correct
        }

        db[os.getenv("USER_PROGRESS_VOCAB_COLLECTION")].update_one(
            filter={
                "learning_path_id": learning_path_id,
                "user_id": user_id,
                "german": vocab["german"]
            },
            update={"$set": data},
            upsert=True
        )

# if __name__ == "__main__":
#     user_id = '123'
#     progress = get_user_progress(user_id)
#     if not progress:
#         progress = ['Beginner Vocabulary']
#
#     vocab_json = generate_vocab_question(progress)
#     vocab = json.loads(vocab_json)
#     print(f"Translate this word into English: {vocab['german']}")
#     user_answer = input("Your answer: ").strip().lower()
#     correct = user_answer == vocab["english"].strip().lower()
#     print("Correct!" if correct else f"Wrong. The correct answer is: {vocab['english']}")
#
#     store_vocab_in_vector_db(vocab_json)
#     save_results(user_id, vocab, user_answer, correct)
