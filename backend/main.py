from fastapi import FastAPI
from dotenv import load_dotenv, find_dotenv
import learn_vocab, json
import uvicorn
import config_checker

app = FastAPI()


@app.get("/vocab/{user_id}")
def read_root(user_id: str):
    user_progress = learn_vocab.get_user_progress(user_id)
    vocab_json = learn_vocab.generate_vocab_question(user_progress)
    vocab = json.loads(vocab_json)
    return vocab



if __name__ == "__main__":
    load_dotenv(find_dotenv())

    if not config_checker.check_if_ollama_model_is_running():
        print("Ollama model is not running. Please start the Ollama model.")
        exit(1)

    if not config_checker.check_if_mongo_db_is_running():
        print("MongoDB is not running. Please start the MongoDB service.")
        exit(1)

    uvicorn.run(app, host="0.0.0.0", port=8000)
