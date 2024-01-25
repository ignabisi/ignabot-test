from datetime import datetime
from sqlmodel import Field, SQLModel, ARRAY, Column,String
from typing import List

class Contact(SQLModel, table=True):
    
    uid: str = Field(default=None, primary_key=True)
    audio_path : List[float] = Field(sa_column=Column(ARRAY(String)))
    created_at: datetime = Field(default_factory=datetime.now, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.now, nullable=False)
    
    class Config:
        arbitrary_types_allowed = True