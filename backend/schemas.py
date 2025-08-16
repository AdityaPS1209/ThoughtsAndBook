from pydantic import BaseModel
from datetime import datetime

class CardCreate(BaseModel):
    content: str

class CardOut(BaseModel):
    id: int
    content: str
    created_at: datetime

    class Config:
        from_attributes = True