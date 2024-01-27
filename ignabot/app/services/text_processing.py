import logging

from app.models.telegram import TelegramUpdate

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class TextProcessor:
    """
    Class for processing text messages received through Telegram.
    Provides a response explaining the bot's capabilities.
    """
    def __init__(self, telegram_update, file_name):
        """
        Initialize the TextProcessor with a Telegram update and a file name.

        Args:
        - telegram_update (TelegramUpdate): The Telegram update containing the text message.
        - file_name (str): The name of the file related to the text processing.
        """
        self.telegram_update: TelegramUpdate = telegram_update
        self.file_name = file_name

    async def process(self) -> str:
        """
        Processes the received text message and returns a response.

        Returns:
        - str: A message explaining the bot's current capabilities.
        """
        message = "📝 Thank you for your message. Currently, my capabilities are limited to 🧐 recognizing faces by processing an image or photo 🖼️ and storing audio recordings 🎤. Please select one of these actions and send me a message to proceed."
        return message