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


def generate_question(progress):
    prompt = f"""
        Role: You are an experienced English language teacher with expertise in adaptive, level-based instruction.
        
        Objective: Create a multiple-choice question tailored to the learner’s current level to reinforce and assess understanding.
        
        Guidelines:
        - Each question must include exactly 4 answer options (1 correct, 3 wrong).
        - Use clear, level-appropriate English based on the learner’s progress.
        - Target key language areas: vocabulary, grammar, sentence structure (choose as appropriate).
        - Avoid repetition in distractors and ensure they are grammatically plausible.
        - Questions must be self-contained and unambiguous.
        - The question and all answer options must be complete, grammatically correct English sentences. Do not use sentence fragments or isolated phrases.
        - If the question includes a gap-fill (e.g., a missing verb), the verb in brackets must always appear in the infinitive (base form without “to”), such as “(swim)” or “(not understand)”.
        - The full sentence containing the gap must be grammatically complete and natural, including subject, verb, and appropriate context.
        - The English grammar in the question itself must always be correct. Avoid incorrect or awkward constructions.
        - Do not include negative auxiliaries (e.g., don't, can't, didn't) in the question text when the goal is to test the correct formation of a negation. In such cases, use the form “(not + verb)” inside the brackets.
        - Highlight the correct answer and provide a concise explanation for:
            - Why the correct answer is right.
            - Why each distractor is incorrect.
        - Think precisely about the answer options and their relevance to the question.
        - The correct answer must be under any circumstances be grammatically correct for the english language.
        
        Think about the learner's current level and adapt the question accordingly.
        Learner Profile:
        {progress}
        
        Output Format:
        Provide the question in valid JSON format with the following structure:
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
        os.getenv("OLLAMA_URL"),
        json={
            "model": os.getenv("OLLAMA_MODEL"),
            "prompt": prompt,
            "stream": False
        }
    )

    return response.json()['response']


def store_question_in_vector_db(question):
    client = chromadb.PersistentClient(path=os.getenv("VECTOR_DB_PATH"))
    collection = client.get_or_create_collection(name="questions")
    embeddings = ollama.embed(os.getenv("EMBED_MODEL"), input=question)["embeddings"]
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
def save_results(user_id, learning_path_id, results):
    client = MongoClient(os.getenv("MONGO_URI"))
    db = client[os.getenv("DB_NAME")]
    db[os.getenv("USER_PROGRESS_COLLECTION")].update_one(
        {
            "user_id": user_id,
            "learning_path_id": learning_path_id,
            "question": results["question"],
        },
        {
            "$set": {
                "user_id": user_id,
                "learning_path_id": learning_path_id,
                "question": results["question"],
                "chosen_option": results["chosen_option"],
            }
        },
        upsert=True
    )
    client.close()

def get_multiple_choice_question(learning_path_id, index: int = -1):
    with MongoClient(os.getenv("MONGO_URI")) as client:
        db = client[os.getenv("DB_NAME")]
        questions = list(db[os.getenv("USER_PROGRESS_COLLECTION")].find({
            "learning_path_id": learning_path_id,
        },
            {"_id": 0}
        ))

        if index == -1:
            return questions

        return questions[index] if index < len(questions) else None


if __name__ == "__main__":
    # user_id = input("Enter your user ID: ")
    user_id = '123'
    progress = get_user_progress(user_id)
    if not progress:
        progress = ['Advanced English Grammar', 'Intermediate Vocabulary', 'Intermediate Sentence Structure']

    question = generate_question(progress)

    store_question_in_vector_db(question)
    answer = input("Choose the correct answer (A, B, C, D): ").lower()

    option_map = {'a': 0, 'b': 1, 'c': 2, 'd': 3}
    chosen_index = option_map.get(answer)

    if chosen_index is not None:
        chosen_option = json.loads(question)["options"][chosen_index]
        print("Gewählte Option:", chosen_option)

        result = {
            "question": json.loads(question),
            "chosen_option": chosen_option,
        }

        save_results(user_id, result)

        print(result["question"])
    else:
        print("Ungültige Auswahl.")
