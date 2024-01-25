
import os
import logging

import httpx
from sqlmodel import Session
from fastapi import APIRouter, Depends, Request, status

from app.models.telegram import TelegramUpdate 
from app.utils import get_session
from app.helpers import send_telegram_message
from app.models.contact import Contact

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

router = APIRouter(prefix="/api/v1/ignabot/telegram", tags=["ignabot"])

@router.post("/", status_code=status.HTTP_200_OK)
async def handle_message(
    telegram_update: TelegramUpdate,
    db_session: Session = Depends(get_session),
):
    
    message = Message(telegram_update)
    _type = message.get_type()
    
    chat_id = message.get_id()
    
    
    
    await message.send_telegram_message(chat_id=chat_id, text="Hello World!")
        
    return {"ok": True}


class Message:
    
    def __init__(self, telegram_update) -> None:
        self.telegram_update = telegram_update
    
    def get_type(self):
        
        if self.telegram_update.message.voice:
            logging.debug("Received audio")
            return "voice"
            
        if self.telegram_update.message.text:
            logging.debug("Received text")
            return "text"
            
        if self.telegram_update.message.photo:
            logging.debug("Received photo")
            return "photo"
            
    def get_id(self):
        chat_id = self.telegram_update.message.chat.get("id")
        
    async def send_telegram_message(self, chat_id, text):
        telegram_token = os.getenv("TELEGRAM_TOKEN")
        
        url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text,
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload)
            logging.debug(response)
        
    def voice():
        pass
    
    def text():
        pass
    
    def photo():
        pass