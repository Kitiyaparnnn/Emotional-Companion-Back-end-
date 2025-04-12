from fastapi import APIRouter, Depends, HTTPException, status
from app.core.security import get_current_user, get_password_hash
from app.models.user import User, UserCreate, UserUpdate
from app.db.mongodb import mongodb
from datetime import datetime
from bson import ObjectId

router = APIRouter()

@router.post("/", response_model=User)
async def create_user(user: UserCreate):
    users_collection = mongodb.get_collection("users")
    
    # Check if user already exists
    if await users_collection.find_one({"email": user.email}):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    user_dict = user.model_dump()
    user_dict["hashed_password"] = get_password_hash(user_dict.pop("password"))
    user_dict["created_at"] = datetime.utcnow()
    user_dict["updated_at"] = user_dict["created_at"]
    
    result = await users_collection.insert_one(user_dict)
    created_user = await users_collection.find_one({"_id": result.inserted_id})
    return created_user

@router.get("/me", response_model=User)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    return current_user

@router.put("/me", response_model=User)
async def update_user(
    user_update: UserUpdate,
    current_user: dict = Depends(get_current_user)
):
    users_collection = mongodb.get_collection("users")
    
    # Update user
    update_data = user_update.model_dump(exclude_unset=True)
    if "password" in update_data:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
    update_data["updated_at"] = datetime.utcnow()
    
    result = await users_collection.update_one(
        {"_id": ObjectId(current_user["_id"])},
        {"$set": update_data}
    )
    
    if result.modified_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    updated_user = await users_collection.find_one({"_id": ObjectId(current_user["_id"])})
    return updated_user 