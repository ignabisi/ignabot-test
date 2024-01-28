from datetime import datetime

import aiofiles
from app.models.contact import Contact, TelegramFile
from sqlmodel import select


class ContactManager:
    """
    Manages contact-related operations for Telegram interactions, including storing and updating contact details in the database.
    """
    
    def __init__(self, telegram, db_session) -> None:
        """
        Initializes the ContactManager with a Telegram object and database session.

        Args:
        - telegram: The Telegram object containing the update.
        - db_session: The database session for performing database operations.
        """
        self.telegram = telegram
        self.telegram_update = telegram.telegram_update
        self.db_session = db_session
        
    @property
    def contact_id(self):
        """
        Retrieves the contact ID from the Telegram update.

        Returns:
        - str: The contact ID.
        """
        contact = self.telegram_update.message.from_
        _contact_id = contact.get("id")
        return str(_contact_id)
    
    @property
    def name(self):
        """
        Retrieves the contact's name from the Telegram update.

        Returns:
        - str: The contact's first name.
        """
        contact = self.telegram_update.message.from_
        name = contact.get("first_name")
        return name
        
    async def is_first_message(self) -> bool:
        """
        Checks if the current message is the first message from the contact.

        Returns:
        - bool: True if it's the first message, False otherwise.
        """
        contact_db = self.db_session.get(Contact, self.contact_id)
        if not contact_db:
            contact = Contact(uid=self.contact_id)
            self.db_session.add(contact)
            self.db_session.commit()
            return True
        return False
        
    async def convert_file_to_binary(self, file_name: str) -> bytes:
        """
        Converts a file to binary format.

        Args:
        - file_name (str): The name of the file to be converted.

        Returns:
        - bytes: The binary content of the file.
        """
        async with aiofiles.open(file_name, mode='rb') as file:
            content = await file.read()
            return content
    
    async def save(self) -> None:
        """
        Saves the contact's details and updates the Telegram update information in the database.
        """
        contact_db = self.db_session.get(Contact, self.contact_id)
        contact_db.telegram_update = self.telegram_update.dict()
        contact_db.updated_at = datetime.now()
        file_name = self.telegram.file_name

        if file_name:
            
            binary_file = await self.convert_file_to_binary(file_name)
            file_name = file_name.split(".")[0]
            if "audio" in file_name:
                contact_db.audios = [] if contact_db.audios is None else list(contact_db.audios)
                audio_count = len(contact_db.audios)
                _filename = f"{file_name}_{audio_count}"
                contact_db.audios.append(_filename)
            if "photo" in file_name:
                _filename = file_name
                
            telegram_file = TelegramFile()
            telegram_file.file_id = _filename
            telegram_file.content = binary_file
            self.db_session.add(telegram_file)
        self.db_session.add(contact_db)
        self.db_session.commit()
        
    
    