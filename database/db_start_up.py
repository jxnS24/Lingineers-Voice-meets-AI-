from pymongo import MongoClient
from dotenv import find_dotenv, load_dotenv

import os

load_dotenv(find_dotenv())

with MongoClient(f'mongodb://{os.environ.get("MONGO_INITDB_ROOT_USERNAME")}:{os.environ.get("MONGO_INITDB_ROOT_PASSWORD")}@localhost:27017/') as client:
    db = client[os.environ.get("MONGO_INITDB_DATABASE")]
    collections = db.list_collection_names()

    if "user-progress" not in collections:
        db.create_collection("user-progress")

    if "user" not in collections:
        db.create_collection("user")

    if "user-progress-vocab" not in collections:
        db.create_collection("user-progress-vocab")

    if "chat_conversations" not in collections:
        db.create_collection("chat_conversations")