from pydantic import BaseModel


class User(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    status: int
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

class ConversationRequest(BaseModel):
    user_id: str
    message: str
