from fastapi import APIRouter, HTTPException, status
from app.models.chat import SentimentLog
from app.db.mongodb import mongodb
from datetime import datetime, timedelta
from typing import List
from bson import ObjectId

router = APIRouter()

@router.post("/logs", response_model=SentimentLog)
async def create_sentiment_log(log: SentimentLog):
    logs_collection = mongodb.get_collection("sentiment_logs")
    log_dict = log.dict()
    log_dict["timestamp"] = datetime.utcnow()
    
    result = await logs_collection.insert_one(log_dict)
    log_dict["id"] = str(result.inserted_id)
    return SentimentLog(**log_dict)

@router.get("/logs/{user_id}", response_model=List[SentimentLog])
async def get_user_sentiment_logs(
    user_id: str,
    start_date: str = None,
    end_date: str = None,
    limit: int = 100
):
    logs_collection = mongodb.get_collection("sentiment_logs")
    query = {"user_id": user_id}
    
    if start_date and end_date:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
        query["timestamp"] = {"$gte": start, "$lt": end}
    
    logs = await logs_collection.find(query).sort("timestamp", -1).limit(limit).to_list(length=limit)
    return [SentimentLog(**log) for log in logs]

@router.get("/summary/{user_id}")
async def get_sentiment_summary(
    user_id: str,
    start_date: str = None,
    end_date: str = None
):
    logs_collection = mongodb.get_collection("sentiment_logs")
    query = {"user_id": user_id}
    
    if start_date and end_date:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
        query["timestamp"] = {"$gte": start, "$lt": end}
    
    # Aggregate sentiment scores and emotion tags
    pipeline = [
        {"$match": query},
        {"$group": {
            "_id": None,
            "avg_sentiment": {"$avg": "$sentiment_score"},
            "emotion_distribution": {"$push": "$emotion_tags"},
            "total_messages": {"$sum": 1}
        }}
    ]
    
    result = await logs_collection.aggregate(pipeline).to_list(length=1)
    if not result:
        return {
            "avg_sentiment": 0,
            "emotion_distribution": {},
            "total_messages": 0
        }
    
    # Process emotion distribution
    emotion_counts = {}
    for tags in result[0]["emotion_distribution"]:
        for tag in tags:
            emotion_counts[tag] = emotion_counts.get(tag, 0) + 1
    
    return {
        "avg_sentiment": result[0]["avg_sentiment"],
        "emotion_distribution": emotion_counts,
        "total_messages": result[0]["total_messages"]
    } 