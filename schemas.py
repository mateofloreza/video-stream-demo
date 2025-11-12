# schemas.py
from pydantic import BaseModel
from datetime import datetime

class VideoCreate(BaseModel):
    filename: str
    mime_type: str
    s3_key: str

class VideoRead(BaseModel):
    id: int
    filename: str
    mime_type: str
    s3_key: str
    created_at: datetime

    class Config:
        orm_mode = True

