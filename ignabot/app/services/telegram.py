import logging
import os
from uuid import uuid4

import httpx
from app.services.photo_processing import PhotoProcessor
from app.services.text_processing import TextProcessor
from app.services.voice_processing import VoiceProcessor

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class Telegram:
    """
    Handles incoming Telegram messages by determining the type and processing accordingly.
    """

    def __init__(self, telegram_update):
        """
        Initializes the message handler with necessary context.

        Parameters:
        - telegram_update: TelegramUpdate object containing the message and metadata.
        - db_session: Database session for any required database operations.
        """
        self.telegram_update = telegram_update
        self.file_name = None
                
    @property     
    def chat_id(self):
        return self.telegram_update.message.chat.get("id")

    def get_type(self):
        """
        Determines the type of the incoming message (voice, text, or photo) and sets it.
        """
        if self.telegram_update.message.voice:
            logger.debug("Received voice message.")
            file_id = self.telegram_update.message.voice.get("file_unique_id")
            self.file_name = f"audio_message_{self.chat_id}_{file_id}.wav"
            return "voice"
            
        if self.telegram_update.message.text:
            logger.debug("Received text message.")
            return "text"
            
        if self.telegram_update.message.photo:
            logger.debug("Received photo message.")
            file_id = self.telegram_update.message.photo[-1].get("file_unique_id")
            self.file_name = f"photo_message_{self.chat_id}_{file_id}.jpg"
            return "photo"
        
    
    async def send(self, text):
        telegram_token = os.getenv("TELEGRAM_TOKEN")
        url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": text,
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload)
            logging.debug(response)
    

    async def process(self):
        """
        Processes the message based on its type.
        """
        response = None
        _type = self.get_type()
        if _type == "voice":
            voice_processor = VoiceProcessor(self.telegram_update, self.file_name)
            response = await voice_processor.process()
        elif _type == "text":
            text_processor = TextProcessor(self.telegram_update, self.file_name)
            response= await text_processor.process()
        elif _type == "photo":
            photo_processor = PhotoProcessor(self.telegram_update, self.file_name)
            response = await photo_processor.process()
        else:
            logger.error("Unsupported message type.")
            response = "Something happened. Please retry."
        return response
    