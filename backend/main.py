from fastapi import FastAPI
import LearnVocab, json
import uvicorn

app = FastAPI()


@app.get("/vocab/{user_id}")
def read_root(user_id: str):
    user_progress = LearnVocab.get_user_progress(user_id)
    vocab_json = LearnVocab.generate_vocab_question(user_progress)
    vocab = json.loads(vocab_json)
    return vocab



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
