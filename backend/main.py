from fastapi import FastAPI
from dotenv import load_dotenv, find_dotenv
import learn_vocab, json
import uvicorn

app = FastAPI()


@app.get("/vocab/{user_id}")
def read_root(user_id: str):
    user_progress = learn_vocab.get_user_progress(user_id)
    vocab_json = learn_vocab.generate_vocab_question(user_progress)
    vocab = json.loads(vocab_json)
    return vocab



if __name__ == "__main__":
    load_dotenv(find_dotenv())
    uvicorn.run(app, host="0.0.0.0", port=8000)
