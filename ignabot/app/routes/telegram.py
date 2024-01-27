
import asyncio
import io
import logging
import os
import sys
import time
import traceback
from io import BytesIO

import aiofiles
import cv2
import httpx
import numpy as np
from app.models.contact import Contact as ContactModel
from app.models.telegram import TelegramUpdate
from app.utils import get_session
from fastapi import APIRouter, Depends, Request, status
from PIL import Image
from pydub import AudioSegment
from sqlmodel import Session

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

router = APIRouter(prefix="/api/v1/ignabot/telegram", tags=["ignabot"])

@router.post("/", status_code=status.HTTP_200_OK)
async def handle_message(
    telegram_update: TelegramUpdate,
    db_session: Session = Depends(get_session),
):
    logging.info(telegram_update)  
    contact = _Contact()
    message = Message(contact, telegram_update, db_session)
    try:
        contact.get_status()
        response = await message.process()
        contact.save_status(response)
    except Exception as err:
        error_traceback = traceback.format_exception(*sys.exc_info())
        # Cleaning up the content by removing newlines and symbols
        error_msg = [
            line.replace("\n", "").replace("^", "").strip() for line in error_traceback
        ]
        # Compile the error response data
        error_type = type(err).__name__
        response_data = {
            "error_type": error_type,
            "traceback": error_msg,
        }
        logging.error(response_data)
        response = {"status_code": 500, "content": "Internal server Error"}
    finally:    
        return response
    
    
class _Contact:
    def __init__(self) -> None:
        pass
    
    def get_status(self):
        pass
    
    def save_status(self, response):
        pass
        
        
class Message:
    
    def __init__(self, contact, telegram_update, db_session) -> None:
        self.contact = contact
        self.telegram_update = telegram_update
        self.db_session = db_session
        self.type = None
        self._process = None
        self.file_name = None
    
    def get_type(self):
        
        
        if self.telegram_update.message.voice:
            logging.debug("Received voice")
            return "voice"
            
        if self.telegram_update.message.text:
            logging.debug("Received text")
            return "text"
            
        if self.telegram_update.message.photo:
            logging.debug("Received photo")
            return "photo"
    @property     
    def chat_id(self):
        return self.telegram_update.message.chat.get("id")
        
    async def send_telegram_message(self, text):
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
        _type = self.get_type()
        _process = getattr(self, _type)
        return await _process()
    
    
    async def send(self):
        return await self.voice()
    

    async def process_photo(self, photo_content):
        image_file_in_memory = io.BytesIO(photo_content)
        with Image.open(image_file_in_memory) as img:            
            # Convert to gray scale
            img_array = np.array(img)
            gray = cv2.cvtColor(img_array, cv2.COLOR_BGR2GRAY)
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
            # Detect Faces
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            if len(faces) > 0:
                self._process = "photo"
                for (x, y, w, h) in faces:
                    cv2.rectangle(img_array, (x, y), (x+w, y+h), (255, 0, 0), 2)
                cv2.imwrite(f"./photos/{self.file_name}.jpg", img_array)
            else:
                self._process = "failed"

    async def process_voice(self, voice_content):
        voice_file_in_memory = io.BytesIO(voice_content)
        audio = AudioSegment.from_file(voice_file_in_memory)
        audio = audio.set_frame_rate(16000).set_channels(1)
        audio.export(self.file_name, format="wav")

            
    async def voice(self):
        logging.info("Lo que se recibe")
        logging.info(self.telegram_update)
        voice = self.telegram_update.message.voice
        if not voice:
            logging.debug("No voice found in the message")
            message = "Received a voice but something wrong happened, please retry."
            await self.send_telegram_message(message)
            return message
        
        file_id = voice.get("file_id")
        telegram_token = os.getenv("TELEGRAM_TOKEN")
        file_url = f"https://api.telegram.org/bot{telegram_token}/getFile?file_id={file_id}"
        async with httpx.AsyncClient() as client:
            file_response = await client.get(file_url)
            if file_response.status_code == 200:
                file_path = file_response.json()["result"]["file_path"]
                voice_url = f"https://api.telegram.org/file/bot{telegram_token}/{file_path}"
                voice_response = await client.get(voice_url)
                voice_file = voice_response.read()
                if voice_response.status_code == 200:
                    self.file_name = f"voice_{file_id}.wav"
                    await self.process_voice(voice_file)
        await self.send_telegram_message("Thank you for your audio message!")
    
    async def text(self):
        self._process = "text"
        message = "Thank you for your message. Currently, my capabilities are limited to recognizing faces by processing an image or photo and storing audio recordings. Please select one of these actions and send me a message to proceed."
        await self.send_telegram_message(message)
    
    async def photo(self):
        if not self.telegram_update.message.photo:
            logging.debug("No photo found in the message")
            message = "Received a photo but something wrong happened, please retry."
            self.send_telegram_message(message)
            return message

        photo = self.telegram_update.message.photo[-1]
        file_id = photo.get("file_id")
        # Obtener el file_path del file_id usando la API de Telegram
        telegram_token = os.getenv("TELEGRAM_TOKEN")
        file_url = f"https://api.telegram.org/bot{telegram_token}/getFile?file_id={file_id}"
        
        async with httpx.AsyncClient() as client:
            file_response = await client.get(file_url)
            if file_response.status_code == 200:
                file_path = file_response.json()["result"]["file_path"]
                photo_url = f"https://api.telegram.org/file/bot{telegram_token}/{file_path}"
                photo_response = await client.get(photo_url)
                photo_file = photo_response.read()
                if photo_response.status_code == 200:
                    
                    self.file_name = f"photo_{file_id}.jpg"
                    await self.process_photo(photo_file)
                    if self._process == "photo":
                        logging.debug(f"Photo saved as {self.file_name}")
                        await self.send_telegram_message("Thank you for sending a picture with a face :)")
                    else:
                        await self.send_telegram_message( "Youve sent an image without a face, try again")
                else:
                    logging.error("Failed to download the photo")
            else:
                logging.error("Failed to get the file_path")
    
    async def download_telegram_voice(self,file_id):
        telegram_token = os.getenv("TELEGRAM_TOKEN")
        # Get file path from Telegram
        async with httpx.AsyncClient() as client:
            file_url = f"https://api.telegram.org/bot{telegram_token}/getFile?file_id={file_id}"
            file_response = await client.get(file_url)
            if file_response.status_code == 200:
                file_path = file_response.json()["result"]["file_path"]
                voice_url = f"https://api.telegram.org/file/bot{telegram_token}/{file_path}"
        
        if voice_url:
            async with httpx.AsyncClient() as client:
                response = await client.get(voice_url)
                voice_content = response.content
                filename = file_path.split('/')[-1]
                logging.info("FILEEEEEEEEEEEEEEE")
                logging.info(file_id)
                logging.info(filename)
            # Save the downloaded audio file temporarily
            async with aiofiles.open(filename, "wb") as audio_file:
                await audio_file.write(voice_content)
            return filename
    
        

    async def convert_voice_to_wav(filename, output_file_name="converted_voice.wav"):
        loop = asyncio.get_running_loop()

        # Define a synchronous wrapper function to perform the blocking operation
        def _sync_convert():
            logging.debug("Converting file: " + filename)
            audio = AudioSegment.from_file(filename)
            audio = audio.set_frame_rate(16000).set_channels(1)
            audio.export(output_file_name, format="wav")
            return output_file_name

        # Run the synchronous function in a separate thread
        return await loop.run_in_executor(None, _sync_convert)