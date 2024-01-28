from typing import List, Optional

from pydantic import BaseModel, Field, validator


class Message(BaseModel):
    message_id: int
    from_: dict = Field(...,alias='from')
    chat: dict
    date: int
    text: Optional[str] = None
    photo: Optional[List] = None
    voice: Optional[dict] = None
    entities: Optional[List] = None
    link_preview_options: Optional[dict] = None

    class Config:
        populate_by_name = True


class TelegramUpdate(BaseModel):
    update_id: int
    message: Message = None


