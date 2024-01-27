

import logging
import sys
import traceback

from app.models.telegram import TelegramUpdate
from app.services.contact_processing import ContactManager
from app.services.telegram import Telegram
from app.utils import get_session
from fastapi import APIRouter, Depends, status
from sqlmodel import Session

logger = logging.getLogger()
logger.setLevel(logging.INFO)

router = APIRouter(prefix="/api/v1/ignabot/telegram", tags=["ignabot"])

@router.post("/", status_code=status.HTTP_200_OK)
async def handle_message(
    telegram_update: TelegramUpdate,
    db_session: Session = Depends(get_session),
):
    """
    Processes an incoming message from Telegram.
    Retrieves or creates a contact, processes the message, and responds appropriately.
    Arguments:
    - telegram_update: TelegramUpdate object containing the message data.
    - db_session: SQLModel session for database interactions.
    """
    logging.debug(telegram_update)  
    telegram = Telegram(telegram_update)
    contact = ContactManager(telegram, db_session)
    try:
        if await contact.is_first_message():
            welcome_message = f"Hello, {contact.name}! It's great to hear from you for the first time."
            await telegram.send(welcome_message)
        response = await telegram.process()
        await telegram.send(response)
        await contact.save()
    except Exception as err:
        error_traceback = traceback.format_exception(*sys.exc_info())
        formatted_traceback = [line.strip() for line in error_traceback if line.strip()]
        error_type = type(err).__name__
        logging.error({
            "error_type": error_type,
            "traceback": formatted_traceback,
        })
        response = {"status_code": 500, "content": "We're sorry, but an internal error occurred. Please try again later."}
    finally:    
        return response
        





    


