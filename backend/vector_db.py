import json

import chromadb
import ollama

MODEL_NAME = "mxbai-embed-large"


def get_datasets():
    with open("dataset_vector_db/data.json", "rb+") as file:
        datasets = json.loads(file.read())
        return datasets


def store_documents(model, collection):
    for index, dataset in enumerate(get_datasets()):
        embeddings = ollama.embed(model, input=dataset["question"])["embeddings"]

        collection.add(
            ids=[str(index)],
            embeddings=embeddings,
            documents=[dataset["question"]],
        )


client = chromadb.PersistentClient(path='./dataset_vector_db')
collection = client.get_or_create_collection(name="datasets")

if collection.count() == 0:
    print("Creating datasets")
    store_documents(MODEL_NAME, collection)

input = "Was heißt Hund auf Englisch?"


response = ollama.embed(MODEL_NAME, input=input)

result = collection.query(
    query_embeddings=response["embeddings"],
    n_results=5,
)

data = result["documents"][0]
print(data)
