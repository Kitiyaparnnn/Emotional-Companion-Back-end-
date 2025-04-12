from fastapi import APIRouter, HTTPException, status
from app.db.mongodb import mongodb
from typing import Dict
from datetime import datetime
from bson import ObjectId

router = APIRouter()

@router.post("/{user_id}/connect")
async def connect_service(user_id: str, service_data: Dict):
    services_collection = mongodb.get_collection("connected_services")
    
    # Check if service already connected
    existing_service = await services_collection.find_one({
        "user_id": user_id,
        "service_type": service_data["service_type"]
    })
    
    if existing_service:
        # Update existing service connection
        await services_collection.update_one(
            {"_id": existing_service["_id"]},
            {
                "$set": {
                    "credentials": service_data["credentials"],
                    "updated_at": datetime.utcnow()
                }
            }
        )
    else:
        # Create new service connection
        service_data["user_id"] = user_id
        service_data["created_at"] = service_data["updated_at"] = datetime.utcnow()
        await services_collection.insert_one(service_data)
    
    return {"message": f"Service {service_data['service_type']} connected successfully"}

@router.get("/{user_id}")
async def get_connected_services(user_id: str):
    services_collection = mongodb.get_collection("connected_services")
    services = await services_collection.find({"user_id": user_id}).to_list(length=100)
    
    # Remove sensitive credentials before returning
    for service in services:
        if "credentials" in service:
            del service["credentials"]
    
    return services

@router.delete("/{user_id}/{service_type}")
async def disconnect_service(user_id: str, service_type: str):
    services_collection = mongodb.get_collection("connected_services")
    result = await services_collection.delete_one({
        "user_id": user_id,
        "service_type": service_type
    })
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=404,
            detail=f"Service {service_type} not found for user {user_id}"
        )
    
    return {"message": f"Service {service_type} disconnected successfully"} 