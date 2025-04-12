from pydantic import BaseModel, Field
from typing import Dict
from datetime import datetime

class UnsureTrait(BaseModel):
    short_term: float = Field(ge=0.0, le=1.0)
    long_term: float = Field(ge=0.0, le=1.0)

class AboutUser(BaseModel):
    certain: Dict[str, bool]
    unsure: Dict[str, UnsureTrait]
    last_updated: datetime = Field(default_factory=datetime.utcnow)

    model_config = {
        "json_encoders": {
            datetime: lambda v: v.isoformat()
        }
    } 