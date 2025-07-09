import os

from pymongo import MongoClient

import multiple_choice
import learn_vocab
import json

def update_finished_steps(learning_path_id):
    with MongoClient(os.getenv("MONGO_URI")) as client:
        db = client[os.getenv("DB_NAME")]
        db[os.getenv("LEARNING_PATH_COLLECTION")].update_one(
            {"learning_path_id": learning_path_id},
            {"$inc": {"finished_steps": 1}}
        )

def is_finished(learning_path_id):
    with MongoClient(os.getenv("MONGO_URI")) as client:
        db = client[os.getenv("DB_NAME")]
        learning_path = db[os.getenv("LEARNING_PATH_COLLECTION")].find_one(
            {"learning_path_id": learning_path_id}
        )

        if learning_path:
            return learning_path["finished_steps"] >= learning_path["valid_steps"]

        return False
def set_status_to_finished(learning_path_id):
    with MongoClient(os.getenv("MONGO_URI")) as client:
        db = client[os.getenv("DB_NAME")]
        db[os.getenv("LEARNING_PATH_COLLECTION")].update_one(
            {"learning_path_id": learning_path_id},
            {"$set": {"state": "finished"}}
        )

async def generate_step_for_learning_path(data):
    user_id = data['user_id']
    learning_path_id = data['learning_path_id']

    update_finished_steps(learning_path_id)

    match data["type"]:
        case "vocab":
            try:
                user_progress = learn_vocab.get_user_progress(user_id)
                vocab_json = learn_vocab.generate_vocab_question(user_progress)
                vocab = json.loads(vocab_json)
                user_answer = ""
                correct = "NOT ANSWERED - DO NOT COUNT"
                learn_vocab.save_results(user_id, vocab, user_answer, correct, learning_path_id)

                print("[Learning Path] Generated vocab question")
                print(
                    f"[Learning Path] User id: {user_id}, Learning Path ID: {learning_path_id}, German: {vocab['german']}, English: {vocab['english']}"
                )
            except:
                print("[Learning Path] Error generating vocab question")

        case "multiple_choice":
            try:
                user_progress = multiple_choice.get_user_progress(user_id)
                question_json = multiple_choice.generate_question(user_progress)
                multiple_choice.store_question_in_vector_db(question_json)
                question = json.loads(question_json)
                chosen_option = "NOT ANSWERED - DO NOT COUNT"
                result = {
                    "question": question,
                    "chosen_option": chosen_option,
                }
                multiple_choice.save_results(user_id, learning_path_id, result)

                print("[Learning Path] Generated multiple choice question")
                print(f"[Learning Path] User id: {user_id}, Learning Path ID: {learning_path_id} Multiple Choice")
            except:
                print("[Learning Path] Error generating multiple choice question")

        case "conversation":
            print("[Learning Path] Skipping conversation step generation")


    if is_finished(learning_path_id):
        print("[Learning Path] Learning path is finished")
        set_status_to_finished(learning_path_id)