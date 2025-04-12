from pydantic import BaseModel, EmailStr, Field, GetJsonSchemaHandler
from typing import Optional, Any, Dict
from datetime import datetime
from bson import ObjectId

class PyObjectId(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, handler=None, **kwargs):
        if not isinstance(v, (str, ObjectId)):
            raise TypeError('ObjectId required')
        if isinstance(v, str):
            try:
                ObjectId(v)
            except Exception:
                raise ValueError('Invalid ObjectId')
        return str(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, _schema_generator: GetJsonSchemaHandler) -> Dict[str, Any]:
        return {"type": "string"}

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
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    hashed_password: str
    created_at: datetime
    updated_at: datetime

    class Config:
        json_encoders = {
            ObjectId: str,
            datetime: lambda v: v.isoformat(),
        }
        populate_by_name = True
        arbitrary_types_allowed = True
        exclude = {"hashed_password"}  # Don't include password in responses

class Token(BaseModel):
    access_token: str
    token_type: str 