from fastapi import APIRouter, Depends, HTTPException, status
from app.core.security import get_current_user
from app.models.chat import ChatMessage, ChatRequest, ChatResponse, Message, ChatSession
from app.db.mongodb import mongodb
from app.core.config import settings
from datetime import datetime, timedelta
from typing import List
from bson import ObjectId
from random import choice

router = APIRouter()

SYSTEM_RESPONSES = [
    "I understand how you're feeling. Would you like to tell me more about that?",
    "That sounds challenging. How are you coping with it?",
    "I'm here to listen. What else is on your mind?",
    "Thank you for sharing that with me. How does it make you feel?",
    "I appreciate you opening up about this. What support do you need right now?"
]

@router.post("/send", response_model=ChatResponse)
async def send_message(
    chat_request: ChatRequest,
    current_user: dict = Depends(get_current_user)
):
    try:
        # Simple response selection (you can make this more sophisticated later)
        ai_response = choice(SYSTEM_RESPONSES)

        # Store the conversation in MongoDB
        chat_collection = mongodb.get_collection("chats")
        chat_message = ChatMessage(
            user_id=str(current_user["_id"]),
            message=chat_request.message,
            response=ai_response
        )
        
        await chat_collection.insert_one(chat_message.model_dump(by_alias=True))

        return ChatResponse(
            message=chat_request.message,
            response=ai_response
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )

@router.get("/history", response_model=List[ChatMessage])
async def get_chat_history(current_user: dict = Depends(get_current_user)):
    chat_collection = mongodb.get_collection("chats")
    chat_history = await chat_collection.find(
        {"user_id": str(current_user["_id"])}
    ).sort("created_at", -1).to_list(length=50)  # Get last 50 messages
    
    return chat_history

@router.get("/messages/{user_id}", response_model=List[Message])
async def get_user_messages(user_id: str, skip: int = 0, limit: int = 100):
    messages_collection = mongodb.get_collection("messages")
    messages = await messages_collection.find(
        {"user_id": user_id}
    ).sort("timestamp", -1).skip(skip).limit(limit).to_list(length=limit)
    
    return [Message(**msg) for msg in messages]

@router.get("/sessions/{user_id}", response_model=List[ChatSession])
async def get_chat_sessions(user_id: str, date: str = None):
    sessions_collection = mongodb.get_collection("chat_sessions")
    query = {"user_id": user_id}
    
    if date:
        start_date = datetime.strptime(date, "%Y-%m-%d")
        end_date = start_date + timedelta(days=1)
        query["start_time"] = {"$gte": start_date, "$lt": end_date}
    
    sessions = await sessions_collection.find(query).sort("start_time", -1).to_list(length=100)
    return [ChatSession(**session) for session in sessions]

@router.post("/sessions", response_model=ChatSession)
async def create_chat_session(session: ChatSession):
    sessions_collection = mongodb.get_collection("chat_sessions")
    session_dict = session.dict()
    session_dict["start_time"] = datetime.utcnow()
    
    result = await sessions_collection.insert_one(session_dict)
    session_dict["id"] = str(result.inserted_id)
    return ChatSession(**session_dict)

@router.put("/sessions/{session_id}")
async def update_chat_session(session_id: str, session: ChatSession):
    sessions_collection = mongodb.get_collection("chat_sessions")
    session_dict = session.dict()
    session_dict["updated_at"] = datetime.utcnow()
    
    result = await sessions_collection.update_one(
        {"_id": ObjectId(session_id)},
        {"$set": session_dict}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"message": "Session updated successfully"} 