from pydantic import BaseModel, EmailStr, Field, GetJsonSchemaHandler
from typing import Optional, Any, Dict, Annotated
from datetime import datetime
from bson import ObjectId
from pydantic.json_schema import JsonSchemaValue

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

class UserBase(BaseModel):
    email: EmailStr
    name: str

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    password: Optional[str] = None

class User(UserBase):
    id: Annotated[PyObjectId, Field(default_factory=PyObjectId, alias="_id")]
    hashed_password: str
    created_at: datetime
    updated_at: datetime

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