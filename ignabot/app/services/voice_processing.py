import asyncio
import io
import logging

from app.helpers import telegram_helper
from app.models.telegram import TelegramUpdate
from pydub import AudioSegment

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class VoiceProcessor:
    """
    Class for processing voice messages received through Telegram.
    Saves the voice message in WAV format after processing.
    """
    def __init__(self, telegram_update, file_name):
        """
        Initialize the VoiceProcessor with a Telegram update and a file name.

        Args:
        - telegram_update (TelegramUpdate): The Telegram update containing the voice message.
        - file_name (str): The name of the file where the voice message will be saved.
        """
        self.telegram_update: TelegramUpdate = telegram_update
        self.file_name: str = file_name
    
    async def process(self) -> str:
        """
        Processes the received voice message. Downloads and saves it as a WAV file.

        Returns:
        - str: A message indicating the outcome of the process.
        """
        voice = self.telegram_update.message.voice
        if not voice:
            logger.debug("No voice found in the message.")
            return "🔇 I didn't detect any voice message. Please try sending it again."

        file_id = voice.get("file_id")
        voice_response, voice_file = await telegram_helper.get_file(file_id)
        if not voice_response:
            logger.debug(f"Failed to fetch voice from Telegram. file_id: {file_id}")
            return "🚫 Oops! Something went wrong while fetching your voice message. Could you please resend it?"

        if voice_response.status_code == 200:
            await self.process_voice(voice_file)
            return "🎙️ Thank you for your audio message! It has been processed successfully."
        
        return "🚫 There was an issue processing your voice message. Please try again."

    async def process_voice(self, voice_content: bytes) -> None:
        """
        Processes the voice content and saves it as a .wav file.

        Args:
        - voice_content (bytes): The voice content in byte format.
        """
        voice_file_in_memory = io.BytesIO(voice_content)
        audio = AudioSegment.from_file(voice_file_in_memory)
        audio = audio.set_frame_rate(16000).set_channels(1)
        audio.export(self.file_name, format="wav")