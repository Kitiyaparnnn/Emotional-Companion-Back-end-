from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth,
    users,
    chat,
    sentiment,
    memory,
    services
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(sentiment.router, prefix="/sentiment", tags=["sentiment"])
api_router.include_router(memory.router, prefix="/memory", tags=["memory"])
api_router.include_router(services.router, prefix="/services", tags=["services"]) 