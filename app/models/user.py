from pydantic import BaseModel, EmailStr, Field, GetJsonSchemaHandler
from typing import Optional, Any, Dict, Annotated, List, Literal, Union
from datetime import datetime
from bson import ObjectId
from pydantic.json_schema import JsonSchemaValue
from enum import Enum
from app.models.about import AboutUser

class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"
    NON_BINARY = "nonbinary"
    SELF_DESCRIBE = "self-describe"
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
    """Model for initial user answers during onboarding"""
    preferred_name: str = Field(..., description="User's preferred name or nickname")
    age: Union[int, Literal["Prefer not to say"]] = Field(..., description="User's age or preference not to disclose")
    gender: Literal["male", "female", "nonbinary", "self-describe", "prefer_not_to_say"] = Field(..., description="User's gender identity")
    occupation: str = Field(..., description="User's occupation")
    current_mood_scale: int = Field(..., ge=1, le=10, description="User's current mood on a scale of 1-10")
    current_emotion: Literal["angry", "disgust", "fear", "joy", "neutral", "sadness", "surprise"] = Field(..., description="User's primary emotion")
    topic_of_interest: Literal["Work", "Relationships", "Health", "Goals", "Stress", "Happiness", "Other"] = Field(..., description="User's preferred topic for discussion")
    has_therapy_experience: bool = Field(..., description="Previous experience with mental health or therapy apps")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When the onboarding was completed")
    completed: bool = Field(default=True, description="Whether onboarding was fully completed")

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
    gender: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    life_focus: Optional[str] = None
    current_mood: Optional[int] = None
    current_emotion: Optional[str] = None
    preferred_topic: Optional[str] = None
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

