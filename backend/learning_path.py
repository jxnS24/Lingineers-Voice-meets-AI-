import asyncio
import json
import uuid

import requests
from pymongo import MongoClient
from dotenv import find_dotenv, load_dotenv

import step_generator
from event_dispatcher import get_event_dispatcher
import os

event_dispatcher = get_event_dispatcher()
event_dispatcher.subscribe("generate_step", step_generator.generate_step_for_learning_path)

def get_relevant_user_data(user_id):
    user_data = {
        "multiple_choice": [],
        "vocab": [],
        "conversations": []
    }

    with MongoClient(os.getenv("MONGO_URI")) as client:
        db = client[os.getenv("DB_NAME")]
        user_data["multiple_choice"] = list(
            db[os.getenv("USER_PROGRESS_COLLECTION")].find({"user_id": user_id}).limit(5)) or []
        user_data["vocab"] = list(
            db[os.getenv("USER_PROGRESS_VOCAB_COLLECTION")].find({"user_id": user_id}).limit(5)) or []

        # Get last 5 conversations for the user
        user_data["conversations"] = list(db[os.getenv("CHAT_CONVERSATIONS_COLLECTION")].aggregate([
            {"$match": {"user_id": user_id}},
            {"$sort": {"chat_id": -1, "_id": -1}},
            {"$group": {
                "_id": "$chat_id",
                "docs": {"$push": "$$ROOT"}
            }},
            {"$sort": {"_id": -1}},
            {"$limit": 5},
            {"$unwind": "$docs"},
            {"$replaceRoot": {"newRoot": "$docs"}}
        ])) or []

    return user_data


def save_learning_path(learning_path):
    load_dotenv(find_dotenv())

    with MongoClient(os.getenv("MONGO_URI")) as client:
        db = client[os.getenv("DB_NAME")]
        db[os.getenv("LEARNING_PATH_COLLECTION")].update_one(
            {"learning_path_id": learning_path["learning_path_id"]},
            {"$set": learning_path},
            upsert=True
        )


async def generate_learning_path(data):
    learning_path_id = data["learning_path_id"]
    user_id = data["user_id"]

    user_data = get_relevant_user_data(user_id)

    learning_path = {
        "learning_path_id": learning_path_id,
        "user_id": user_id,
        "state": "in_preparation",
        "user_progress": {
            "multiple_choice": user_data["multiple_choice"],
            "vocab": user_data["vocab"],
            "conversations": user_data["conversations"]
        },
        "steps": [],
    }

    save_learning_path(learning_path)

    prompt = f"""
    You are an expert language learning path generator for the English language. 
    Orientation: You are creating a personalized learning path for a user based on their recent progress in multiple-choice questions, vocabulary, and conversations.
    The concept is similar to Duolingo. 
    Focus on creating a personalized learning path based on the user's recent progress in multiple-choice questions, vocabulary, and conversations.
    Use the following user data to create a structured learning path:
    {user_data}
    
    Lets think step by step about the learning path which give the user the best learning experience.
    """

    pre_response = requests.post(
        os.getenv("OLLAMA_URL"),
        json={
            "model": os.getenv("OLLAMA_MODEL"),
            "prompt": prompt,
            "stream": False
        }
    ).json()["response"]

    print('[Learning Path] Pre-response generated')
    fine_prompt = f"""
    {pre_response}
    Format your thoughts into a structured learning path as a JSON array.
    Each element in the array must be an object with the following structure:
    "step": A string representing the step number (e.g., "0", "1", etc.)
    "type": One of exactly these three values: "vocab", "conversation", or "multiple_choice"
    Important:
    Only these three values are allowed for "type": "vocab", "conversation", or "multiple_choice".
    Do not use any other type.
    Per session is a maximum of 2 conversation steps allowed.
    The output must be valid JSON.
    Only respond with the JSON array. No extra text.

    Example:
    [
      {{
        "step": "0",
        "type": "vocab"
      }},
      {{
        "step": "1",
        "type": "multiple_choice"
      }}
    ]
    """

    response = requests.post(
        os.getenv("OLLAMA_URL"),
        json={
            "model": os.getenv("OLLAMA_MODEL"),
            "prompt": fine_prompt,
            "stream": False
        }
    ).json()["response"]

    try:
        steps = json.loads(response)
        valid_steps = 0
        for step in steps:
            step["learning_path_id"] = learning_path_id
            step["user_id"] = user_id

            if step["type"] == "vocab" or step["type"] == "multiple_choice" or step["type"] == "conversation":
                valid_steps += 1
                asyncio.create_task(
                    event_dispatcher.dispatch("generate_step", step)
                )

        learning_path["steps"] = steps
        learning_path["state"] = "in_progress"
        learning_path["valid_steps"] = valid_steps
        learning_path["finished_steps"] = 0

        save_learning_path(learning_path)
    except:
        learning_path["state"] = "error"
        save_learning_path(learning_path)
        print("[Learning Path] Error in response parsing", response)
