from enum import Enum

from pydantic import BaseModel


class User(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    status: str
    message: str


class VocabQuestion(BaseModel):
    german: str
    english: str


class MultipleChoiceOptions(BaseModel):
    text: str
    is_correct: bool


class MultipleChoiceQuestion(BaseModel):
    question: str
    options: list[MultipleChoiceOptions]
    explanation: str


class Role(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"


class ChatConversationMessage(BaseModel):
    chat_id: str
    message: str
    user_id: str
    role: Role


class ChatConversationRequest(BaseModel):
    user_id: str
    message: str
