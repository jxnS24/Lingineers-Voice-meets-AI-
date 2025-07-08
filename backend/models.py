from pydantic import BaseModel


class User(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    status: str
    message: str
