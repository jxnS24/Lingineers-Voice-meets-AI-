import os
import uuid

import requests

from pymongo import MongoClient

from models import ChatConversationMessage, Role


def get_conversation(chat_id: str):
    with MongoClient(os.getenv("MONGO_URI")) as client:
        db = client[os.getenv("DB_NAME")]
        conversation = db["chat_conversations"].find({"chat_id": chat_id})
        return [
            ChatConversationMessage.model_validate(msg)
            for msg in conversation
        ]


def save_conversation(chat_id: str, user_id: str, message: str, role: str):
    with MongoClient(os.getenv("MONGO_URI")) as client:
        db = client[os.getenv("DB_NAME")]
        db["chat_conversations"].insert_one(
            ChatConversationMessage.model_validate({
                "chat_id": chat_id,
                "user_id": user_id,
                "message": message,
                "role": role
            }).model_dump()
        )


def ask_ollama(message: str, chat_id: str, user_id: str) -> ChatConversationMessage:
    messages = []

    if chat_id and chat_id != "":
        messages = [
            ChatConversationMessage.model_validate(msg).model_dump_json()
            for msg in get_conversation(chat_id)
        ]
        print(messages)
    else:
        chat_id = str(uuid.uuid4())

    messages.append(
        ChatConversationMessage.model_validate({
            "chat_id": chat_id,
            "user_id": user_id,
            "message": message,
            "role": Role.USER
        }).model_dump_json()
    )
    save_conversation(chat_id, user_id, message, "user")

    payload = {
        "prompt": f"""
        You are a helpful english learning assistant. Answer the user's question based on the context provided in the conversation history.
        Additionally your goal is to help the user learn English by providing explanations, examples, and corrections when necessary.
        You are only allowed to respond in English or German. If you find it necessary you can also provide a translation of the user's problem, explanations, examples.
        
        Here is the conversation history:
        {messages}
        """,
        "model": os.getenv("OLLAMA_MODEL"),
        "stream": False,
    }

    print(f"Prompt: {payload["prompt"]}")

    response = requests.post(os.getenv("OLLAMA_URL"), json=payload)
    response.raise_for_status()

    ollama_response = response.json()["response"]
    save_conversation(chat_id, user_id, ollama_response, "assistant")

    return ChatConversationMessage.model_validate({
        "chat_id": chat_id,
        "user_id": user_id,
        "message": ollama_response,
        "role": Role.ASSISTANT
    })


if __name__ == "__main__":
    from dotenv import load_dotenv, find_dotenv

    load_dotenv(find_dotenv())
    response = ask_ollama('Can you help me understand this grammatic: I am going to the park', "", "user123")
    print(response)
