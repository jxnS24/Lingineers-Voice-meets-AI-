import os

import requests
from dotenv import load_dotenv, find_dotenv
from pymongo import MongoClient

load_dotenv(find_dotenv())


def check_if_ollama_model_is_running():
    try:
        response = requests.get('http://localhost:11434/api/tags').json()

        if not response:
            return False

        for model in response['models']:
            if model["name"].startswith(os.getenv("OLLAMA_MODEL")):
                print(f"Ollama model {model['name']} is running.")
                return True

        return False

    except Exception as e:
        print(e)
        return False


def check_if_mongo_db_is_running():
    try:
        with MongoClient(os.getenv("MONGO_URI")):
            print("MongoDB is running.")
            return True

    except Exception as e:
        print(e)
        return False
