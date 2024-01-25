from fastapi import FastAPI, Request
from pydantic import BaseModel

class Message(BaseModel):
    message_id: int
    from_: dict = None
    chat: dict
    date: int
    text: str = None
    photo: list = None
    voice: dict = None
    # Puedes añadir más campos según los tipos de mensajes que esperas recibir

# Modelo para el update entrante de Telegram
class TelegramUpdate(BaseModel):
    update_id: int
    message: Message = None