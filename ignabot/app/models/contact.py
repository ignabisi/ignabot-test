from datetime import datetime
from typing import List, Optional

from sqlmodel import ARRAY, JSON, Column, Field, LargeBinary, SQLModel, String


class Contact(SQLModel, table=True):
    
    uid: str = Field(default=None, primary_key=True)
    audio_content: List[bytes] = Field(default=None, sa_column=Column(LargeBinary))
    audios : List[str] = Field(default_factory=list, sa_column=Column(ARRAY(String)))
    telegram_update: Optional[dict] = Field(sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.now, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.now, nullable=False)
    
    class Config:
        arbitrary_types_allowed = True