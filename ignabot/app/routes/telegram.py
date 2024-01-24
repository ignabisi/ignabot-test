from sqlmodel import Session
from fastapi import APIRouter, Depends, Request, status

from app.models.telegram import TelegramUpdate 
from app.utils import get_session
from app.helpers import send_telegram_message

router = APIRouter(prefix="/api/v1/ignabot/telegram", tags=["ignabot"])

@router.post("/", status_code=status.HTTP_200_OK)
async def handle_message(
    update: TelegramUpdate,
    db_session: Session = Depends(get_session),
):
    if update.message.text:
        print("text")
        
    if update.message.photo:
        print("photo")
    
    
    print(update)
    chat_id = update.message.chat.get("id")
    await send_telegram_message( chat_id=chat_id, text="Hello World!")
        
    return {"ok": True}



