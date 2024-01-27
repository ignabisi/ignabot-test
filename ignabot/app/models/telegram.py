from typing import List, Optional

from fastapi import FastAPI, Request
from pydantic import BaseModel, Field
from sqlmodel import Column, Field, LargeBinary, SQLModel


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


class TelegramFile(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    file_id: str = Field(default=None)
    content: List[bytes] = Field(default=None, sa_column=Column(LargeBinary))
    
    class Config:
        arbitrary_types_allowed = True