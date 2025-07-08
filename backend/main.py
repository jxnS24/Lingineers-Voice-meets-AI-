from fastapi import FastAPI
from dotenv import load_dotenv, find_dotenv
from fastapi.middleware.cors import CORSMiddleware
from user import find_user, create_user
from models import User, LoginResponse

import learn_vocab, json
import uvicorn
import bcrypt
import config_checker

load_dotenv(find_dotenv())

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/vocab/{user_id}")
def read_root(user_id: str):
    user_progress = learn_vocab.get_user_progress(user_id)
    vocab_json = learn_vocab.generate_vocab_question(user_progress)
    vocab = json.loads(vocab_json)
    return vocab


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


if __name__ == "__main__":
    load_dotenv(find_dotenv())

    if not config_checker.check_if_ollama_model_is_running():
        print("Ollama model is not running. Please start the Ollama model.")
        exit(1)

    if not config_checker.check_if_mongo_db_is_running():
        print("MongoDB is not running. Please start the MongoDB service.")
        exit(1)

    uvicorn.run(app, host="0.0.0.0", port=8000)
