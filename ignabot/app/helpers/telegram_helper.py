
import os
from enum import Enum

import httpx


async def get_file(file_id):
    telegram_token = os.getenv("TELEGRAM_TOKEN")
    file_url = f"https://api.telegram.org/bot{telegram_token}/getFile?file_id={file_id}"
    async with httpx.AsyncClient() as client:
        file_response = await client.get(file_url)
        if file_response.status_code == 200:
            file_path = file_response.json()["result"]["file_path"]
            url = f"https://api.telegram.org/file/bot{telegram_token}/{file_path}"
            response = await client.get(url)
            file = response.read()
            return response, file
    return None, None
