
import io
import logging
import os
import sys
import time
import traceback

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
            logging.debug("Received audio")
            self.type = "audio"
            
        if self.telegram_update.message.text:
            logging.debug("Received text")
            self.type = "text"
            
        if self.telegram_update.message.photo:
            logging.debug("Received photo")
            self.type = "photo"
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
        # return await self.photo()
        return await self.voice()
    
    async def send(self):
        return await self.voice()
            
    async def voice(self):
        logging.info("Lo que se recibe")
        logging.info(self.telegram_update)
        await self.send_telegram_message("audio")
    
    async def text(self):
        self._process = "text"
        message = "Tank you for your message. Until now my only abilities are to recognize a face by sending an image or photo and to store audios. Please choose one action and send me a message"
        await self.send_telegram_message(message)
    
    async def process_photo(self, photo_content):
        # image_file_in_memory = io.BytesIO(photo_content)
        with Image.open(photo_content) as img:            
            # Convert to gray scale
            img_array = np.array(img)
            gray = cv2.cvtColor(img_array, cv2.COLOR_BGR2GRAY)
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            # Detect Faces
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            if len(faces) > 0:
                self._process = "photo"
                for (x, y, w, h) in faces:
                    cv2.rectangle(img_array, (x, y), (x+w, y+h), (255, 0, 0), 2)
                cv2.imwrite(f"./photos/{self.file_name}.jpg", img_array)
            else:
                self._process = "failed"
                
    
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
                file_path = file_response.json()['result']['file_path']
                photo_url = f"https://api.telegram.org/file/bot{telegram_token}/{file_path}"
                photo_response = await client.get(photo_url)
                
                photo_file = photo_response.read()
                if photo_response.status_code == 200:
                    
                    self.file_name = f"photo_{file_id}.jpg"
                    
                    with open(self.file_name, "wb") as photo_file:
                        await self.process_photo(photo_response)
                    if self._process == "photo":
                        logging.debug(f"Photo saved as {self.file_name}")
                        await self.send_telegram_message("Thank you for sending a picture with a face :)")
                    else:
                        await self.send_telegram_message( "You've sent an image without a face, try again")
                else:
                    logging.error("Failed to download the photo")
            else:
                logging.error("Failed to get the file_path")
    
    async def download_telegram_audio(file_id):
        telegram_token = os.getenv("TELEGRAM_TOKEN")
        # Get file path from Telegram
        async with httpx.AsyncClient() as client:
            file_url = f"https://api.telegram.org/bot{telegram_token}/getFile?file_id={file_id}"
            file_response = await client.get(file_url)
            if file_response.status_code == 200:
                file_path = file_response.json()['result']['file_path']
                audio_url = f"https://api.telegram.org/file/bot{telegram_token}/{file_path}"
                response = await client.get(audio_url)
                logging.info("RRRRRRRRRRRRRRRresponse")
                logging.info(response)
                
        
        # Save the downloaded audio file temporarily
        # with open(local_audio_file, 'wb') as audio_file:
        #     audio_file.write(audio_content)
        
        # return local_audio_file

    def convert_audio_to_wav(input_file_name, output_file_name='converted_audio.wav'):
        # Load the audio file
        audio = AudioSegment.from_file(input_file_name)
        
        # Convert to 16kHz, mono
        audio = audio.set_frame_rate(16000).set_channels(1)
        
        # Export and save the converted audio as WAV
        audio.export(output_file_name, format='wav')
        
        return output_file_name

        # # Example usage
        # file_id = 'TELEGRAM_FILE_ID_FROM_UPDATE'  # Placeholder for the actual file_id from Telegram update
        # downloaded_file_name = download_telegram_audio(file_id)  # Download the file
        # output_wav_file = convert_audio_to_wav(downloaded_file_name)  # Convert and save as WAV

        # print(f'Audio has been converted and saved as {output_wav_file}')

        # # Cleanup: Remove the temporary downloaded file if needed
        # import os
        # os.remove(downloaded_file_name)