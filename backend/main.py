import asyncio
import json
import os
import uuid

from fastapi import FastAPI
from dotenv import load_dotenv, find_dotenv
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pymongo import MongoClient

from event_dispatcher import get_event_dispatcher
from user import find_user, create_user
from models import User, VocabQuestion, ChatConversationRequest, LoginResponse, MultipleChoiceQuestion

import learn_vocab, multiple_choice, conversation, chat_conversation, learning_path
import uvicorn
import bcrypt
import config_checker

load_dotenv(find_dotenv())

app = FastAPI()

event_dispatcher = get_event_dispatcher()

event_dispatcher.subscribe("generate_learning_path", learning_path.generate_learning_path)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/vocab/{learning_path_id}/{index}")
def get_vocab_question(learning_path_id: str, index: int):
    vocab = learn_vocab.get_vocab_question(learning_path_id, index)
    return vocab


@app.get("/vocab/{learning_path_id}")
def get_vocab_questions(learning_path_id: str):
    return learn_vocab.get_vocab_question(learning_path_id)


@app.get('/multiple-choice/{learning_path_id}/{index}')
def get_multiple_choice_question(learning_path_id: str, index: int):
    question = multiple_choice.get_multiple_choice_question(learning_path_id, index)
    return question


@app.get('/multiple-choice/{learning_path_id}')
def get_multiple_choice_questions(learning_path_id: str):
    return multiple_choice.get_multiple_choice_question(learning_path_id)


@app.post('/conversation')
def hold_conversion_with_user(request: ChatConversationRequest):
    response = conversation.ask_ollama(request.message)
    output = conversation.speak(response)

    return StreamingResponse(
        output,
        media_type="audio/wav",
        headers={"Content-Disposition": "attachment; filename=example.wav"}
    )


@app.post("/register")
def register(user: User):
    create_user(user.username, user.password)

    return {"msg": "Registered successfully"}


@app.post("/login")
def login(user: User):
    try:
        db_user = find_user(user.username)

        if bcrypt.checkpw(user.password.encode('utf-8'), db_user['password'].encode('utf-8')):
            return LoginResponse(status="success", message=db_user['username'])

        return LoginResponse(status="error", message="Invalid username or password")

    except Exception as e:
        return LoginResponse(status="error", message=str(e))


@app.post("/chat_conversation")
def ask_chat_conversation(request: ChatConversationRequest):
    return chat_conversation.ask_ollama(request.message, request.chat_id, request.user_id)


@app.get("/learning_path/{user_id}")
async def start_generating_learning_path(user_id: str):
    learning_path_id = str(uuid.uuid4())
    payload = {
        "learning_path_id": learning_path_id,
        "user_id": user_id
    }

    asyncio.create_task(
        event_dispatcher.dispatch("generate_learning_path", payload)
    )

    return {"learning_path_id": learning_path_id}


@app.get("/learning_path/{user_id}/{learning_path_id}/status")
async def get_learning_path_status(user_id: str, learning_path_id: str):
    with MongoClient(os.environ.get("MONGO_URI")) as client:
        db = client[os.environ.get("DB_NAME")]
        learning_path = db[os.environ.get("LEARNING_PATH_COLLECTION")].find_one(
            {"learning_path_id": learning_path_id, "user_id": user_id}
        )

        if not learning_path:
            return {"status": "not_found"}

        return {
            "status": learning_path["state"],
        }

@app.get("/learning_path/{user_id}/{learning_path_id}")
def get_learning_path(user_id: str, learning_path_id: str):
    def remove_ids(obj):
        if isinstance(obj, dict):
            return {k: remove_ids(v) for k, v in obj.items() if k != "_id"}
        elif isinstance(obj, list):
            return [remove_ids(item) for item in obj]
        else:
            return obj

    with MongoClient(os.environ.get("MONGO_URI")) as client:
        db = client[os.environ.get("DB_NAME")]
        learning_path = db[os.environ.get("LEARNING_PATH_COLLECTION")].find_one(
            {"learning_path_id": learning_path_id, "user_id": user_id}
        )

        return remove_ids(learning_path)


if __name__ == "__main__":
    load_dotenv(find_dotenv())

    if not config_checker.check_if_ollama_model_is_running():
        print("Ollama model is not running. Please start the Ollama model.")
        exit(1)

    if not config_checker.check_if_mongo_db_is_running():
        print("MongoDB is not running. Please start the MongoDB service.")
        exit(1)

    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, log_level="info", workers=10)
