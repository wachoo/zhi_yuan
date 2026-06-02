import uuid
from datetime import datetime
from pydantic import BaseModel


class ChatSessionOut(BaseModel):
    session_id: str
    title: str
    message_count: int
    skill_id: str | None = None
    last_message_at: datetime | None = None


class ChatMessageOut(BaseModel):
    id: uuid.UUID
    session_id: str
    role: str
    content: str
    skill_id: str | None = None
    skill_name: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True
