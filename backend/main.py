from fastapi import FastAPI
from dotenv import load_dotenv, find_dotenv
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from backend.models import MultipleChoiceQuestion
from user import find_user, create_user
from models import User, VocabQuestion, ConversationRequest, LoginResponse

import learn_vocab, multiple_choice, conversation
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
def get_vocab_question(user_id: str):
    user_progress = learn_vocab.get_user_progress(user_id)
    vocab_json = learn_vocab.generate_vocab_question(user_progress)
    return VocabQuestion.model_validate_json(vocab_json)


@app.get('/multiple-choice/{user_id}')
def get_multiple_choice_question(user_id: str):
    user_progress = multiple_choice.get_user_progress(user_id)
    question_json = multiple_choice.generate_question(user_progress)
    multiple_choice.store_question_in_vector_db(question_json)
    return MultipleChoiceQuestion.model_validate_json(question_json)


@app.post('/conversation')
def hold_conversion_with_user(request: ConversationRequest):
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

if __name__ == "__main__":
    load_dotenv(find_dotenv())

    if not config_checker.check_if_ollama_model_is_running():
        print("Ollama model is not running. Please start the Ollama model.")
        exit(1)

    if not config_checker.check_if_mongo_db_is_running():
        print("MongoDB is not running. Please start the MongoDB service.")
        exit(1)

    uvicorn.run(app, host="0.0.0.0", port=8000)
