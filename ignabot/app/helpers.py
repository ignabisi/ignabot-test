import os
import logging

import httpx

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

async def send_telegram_message(chat_id: int, text: str):
    
    telegram_token = os.getenv("TELEGRAM_TOKEN")
    
    url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload)
        logging.debug(response)
