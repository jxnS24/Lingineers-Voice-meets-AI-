import os

import bcrypt
from dotenv import load_dotenv, find_dotenv
from pymongo import MongoClient

load_dotenv(find_dotenv())

with MongoClient(os.getenv("MONGO_URI")) as client:
    db = client[os.getenv("DB_NAME")]
    db["user"].insert_one({
        "username": "admin",
        "password": "admin"
    })

client = MongoClient("mongodb://localhost:27017/")
db = client["your_database_name"]
user_collection = db["user"]


def find_user(username):
    with MongoClient(os.getenv("MONGO_URI")) as client:
        db = client[os.getenv("DB_NAME")]
        user = db["user"].find_one({"username": username})

    return user

def create_user(username, password):
    with MongoClient(os.getenv("MONGO_URI")) as client:
        db = client[os.getenv("DB_NAME")]
        if db["user"].find_one({"username": username}):
            return False

        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

        db["user"].insert_one({
            "username": username,
            "password": hashed_password
        })

    return True
