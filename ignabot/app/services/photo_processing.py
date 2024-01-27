import asyncio
import io
import logging
import os

import cv2
import numpy as np
from app.helpers import telegram_helper
from app.models.telegram import TelegramUpdate
from PIL import Image

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class PhotoProcessor:
    """
    Class for processing photo messages received through Telegram.
    It checks for photos, downloads them, and processes them to detect faces.
    """
    def __init__(self, telegram_update: TelegramUpdate, file_name: str):
        """
        Initialize the PhotoProcessor with a Telegram update and a file name for saving the photo.

        Args:
        - telegram_update (TelegramUpdate): The Telegram update containing the photo.
        - file_name (str): The name of the file where the processed photo will be saved.
        """
        self.telegram_update = telegram_update
        self.file_name = file_name
        self.photo = telegram_update.message.photo[-1] if telegram_update.message.photo else None
    
    async def process(self) -> str:
        """
        Processes the photo from the Telegram update. 
        Downloads the photo, detects faces, and saves the processed image.

        Returns:
        - str: A message indicating the outcome of the process.
        """
        if not self.photo:
            logger.debug("No photo found in the message.")
            return "Oops! There was no photo in your message. Please send a photo to proceed."

        file_id = self.photo.get("file_id")
        photo_response, photo_file = await telegram_helper.get_file(file_id)
        logger.debug(f"Response type: {type(photo_response)}, Photo file type: {type(photo_file)}")
        
        if not photo_response:
            logger.debug(f"Failed to fetch photo from Telegram. file_id: {file_id}")
            return "Sorry, I couldn't retrieve the photo. Could you please try sending it again?"

        if photo_response.status_code == 200:
            status = await self.process_photo(photo_file)
            if status == "photo":
                logger.debug(f"Photo processed and saved as {self.file_name}")
                return "Awesome! Your photo with a face has been processed successfully."
            else:
                return "Hmm, I couldn't find any faces in your photo. Could you try a different one?"
        else:
            logger.error("Failed to download the photo.")
            return "Oops! There was an issue downloading your photo. Please try sending it again."

    
    async def process_photo(self, photo_content: bytes) -> None:
        """
        Processes the photo to detect faces and save it.

        Args:
        - photo_content (bytes): The content of the photo to be processed.
        """
        image_file_in_memory = io.BytesIO(photo_content)
        with Image.open(image_file_in_memory) as img:
            img_array = np.array(img)
            gray = cv2.cvtColor(img_array, cv2.COLOR_BGR2GRAY)
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            if len(faces) > 0:
                for (x, y, w, h) in faces:
                    cv2.rectangle(img_array, (x, y), (x+w, y+h), (255, 0, 0), 2)
                cv2.imwrite(self.file_name, img_array)
                return "photo"
            else:
                return "failed"




        