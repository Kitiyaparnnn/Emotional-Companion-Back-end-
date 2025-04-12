from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from .user import PyObjectId

class Message(BaseModel):
    role: str
    content: str

class ChatMessage(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: str
    message: str
    response: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    message: str
    response: str

class ChatSession(BaseModel):
    id: str
    user_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    messages: List[Message]
    daily_summary: Optional[str] = None

class SentimentLog(BaseModel):
    id: str
    message_id: str
    user_id: str
    timestamp: datetime
    sentiment_score: float
    emotion_tags: List[str]
    context: Optional[dict] = None

class LongTermMemory(BaseModel):
    id: str
    user_id: str
    trait_type: str
    trait_value: str
    confidence_score: float
    last_updated: datetime
    source_messages: List[str] 