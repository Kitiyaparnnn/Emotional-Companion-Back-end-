from pydantic import BaseModel, EmailStr, Field, GetJsonSchemaHandler
from typing import Optional, Any, Dict, Annotated, List
from datetime import datetime
from bson import ObjectId
from pydantic.json_schema import JsonSchemaValue
from enum import Enum
from app.models.about import AboutUser

class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"
    PREFER_NOT_TO_SAY = "prefer_not_to_say"

class Emotion(str, Enum):
    ANGRY = "angry"
    DISGUST = "disgust"
    FEAR = "fear"
    JOY = "joy"
    NEUTRAL = "neutral"
    SADNESS = "sadness"
    SURPRISE = "surprise"

class PyObjectId(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, handler=None):
        if not isinstance(v, (str, ObjectId)):
            raise TypeError('ObjectId required')
        if isinstance(v, str):
            try:
                ObjectId(v)
            except Exception:
                raise ValueError('Invalid ObjectId')
        return str(v)

    @classmethod
    def __get_pydantic_json_schema__(
        cls,
        _schema_generator: GetJsonSchemaHandler,
        _field_name: str | None = None,
    ) -> JsonSchemaValue:
        return {"type": "string", "format": "objectid"}

class StarterAnswers(BaseModel):
    preferred_name: str
    age: int
    gender: Gender
    occupation: str
    current_mood_scale: int = Field(ge=1, le=10)
    current_emotion: Emotion
    topic_of_interest: str
    has_therapy_experience: bool
    created_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {
        "json_encoders": {
            datetime: lambda v: v.isoformat()
        }
    }

class UserBase(BaseModel):
    email: EmailStr
    name: str

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    password: Optional[str] = None

class UserProfile(BaseModel):
    preferred_name: Optional[str] = None
    gender: Optional[Gender] = None
    age: int
    occupation: Optional[str] = None
    has_therapy_experience: Optional[bool] = None
    last_updated: datetime = Field(default_factory=datetime.utcnow)

    model_config = {
        "json_encoders": {
            datetime: lambda v: v.isoformat()
        }
    }

class User(UserBase):
    id: Annotated[PyObjectId, Field(default_factory=PyObjectId, alias="_id")]
    hashed_password: str
    created_at: datetime
    updated_at: datetime
    profile: Optional[UserProfile] = None
    about: Optional[AboutUser] = None

    model_config = {
        "json_encoders": {
            ObjectId: str,
            datetime: lambda v: v.isoformat(),
        },
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "exclude": {"hashed_password"}  # Don't include password in responses
    }

class Token(BaseModel):
    access_token: str
    token_type: str 

