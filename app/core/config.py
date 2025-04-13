from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Project settings
    PROJECT_NAME: str = "Emotional Companion API"
    API_V1_STR: str = "/api/v1"
    
    # MongoDB settings
    MONGODB_URL: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "emotional_companion"
    
    # JWT settings
    JWT_SECRET_KEY: str = "your-secret-key"  # Change this in production!
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # OAuth settings
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    SPOTIFY_CLIENT_ID: Optional[str] = None
    SPOTIFY_CLIENT_SECRET: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    
    # Encryption key for sensitive data
    ENCRYPTION_KEY: str = "your-encryption-key-32bytes-long!!"  # 32 bytes for Fernet

    class Config:
        env_file = ".env"

settings = Settings() 