from pydantic import BaseModel, Field, GetJsonSchemaHandler
from typing import List, Optional, Annotated, Dict
from datetime import datetime
from bson import ObjectId
from pydantic.json_schema import JsonSchemaValue
from .user import Emotion

class PyObjectId(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, handler=None):
        if isinstance(v, ObjectId):
            return str(v)
        if isinstance(v, str):
            return v
        raise ValueError("Invalid ObjectId")

    @classmethod
    def __get_pydantic_json_schema__(
        cls,
        _schema_generator: GetJsonSchemaHandler,
        _field_name: str | None = None,
    ) -> JsonSchemaValue:
        return {"type": "string"}

class Message(BaseModel):
    role: str
    content: str
    timestamp: datetime
    emotion: Emotion

    model_config = {
        "json_encoders": {
            datetime: lambda v: v.isoformat()
        }
    }

class ChatMessage(BaseModel):
    user_id: str
    message: str
    emotion: Optional[Emotion] = None
    response: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {
        "json_encoders": {
            datetime: lambda v: v.isoformat()
        }
    }

class ChatRequest(BaseModel):
    message: str
    emotion: Optional[Emotion] = None

class ChatResponse(BaseModel):
    message: str
    response: str

class ChatSession(BaseModel):
    id: Annotated[PyObjectId, Field(default_factory=PyObjectId, alias="_id")]
    user_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    messages: List[Message]
    daily_summary: Optional[str] = None
    overall_emotion: Emotion
    emotion_history: List[Emotion] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {
        "json_encoders": {
            ObjectId: str,
            datetime: lambda v: v.isoformat()
        }
    }

class SentimentLog(BaseModel):
    id: Annotated[PyObjectId, Field(default_factory=PyObjectId, alias="_id")]
    message_id: str
    user_id: str
    timestamp: datetime
    sentiment_score: float
    emotion_tags: List[Emotion]
    context: Optional[dict] = None

    model_config = {
        "json_encoders": {
            datetime: lambda v: v.isoformat()
        }
    }

class LongTermMemory(BaseModel):
    id: Annotated[PyObjectId, Field(default_factory=PyObjectId, alias="_id")]
    user_id: str
    trait_type: str
    trait_value: str
    confidence_score: float
    last_updated: datetime
    source_messages: List[str]

    model_config = {
        "json_encoders": {
            datetime: lambda v: v.isoformat()
        }
    } 