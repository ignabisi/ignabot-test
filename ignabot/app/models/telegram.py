from fastapi import FastAPI, Request
from pydantic import BaseModel, Field


class Message(BaseModel):
    message_id: int
    from_: dict = Field(..., alias="from")
    chat: dict
    date: int
    text: str = None
    photo: list = None
    voice: dict = None

class TelegramUpdate(BaseModel):
    update_id: int
    message: Message = None