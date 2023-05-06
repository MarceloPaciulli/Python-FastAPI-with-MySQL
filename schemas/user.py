from pydantic import BaseModel
from typing import List


class User(BaseModel):
    email: str
    password: str


class Chat(BaseModel):
    user_id: int
    chat_name: str
    chat_description: str
    language: str = "en"


class Message(BaseModel):
    chat_id: int
    user_id: int
    message_content: str
    timestamp: str
    

class UserWithChats(BaseModel):
    email: str
    password: str
    chats: List[Chat] = []
