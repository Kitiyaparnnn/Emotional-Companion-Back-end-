from fastapi import APIRouter, Depends, HTTPException, status
from app.core.security import get_current_user, get_password_hash
from app.models.user import User, UserCreate, UserUpdate, UserProfile, StarterAnswers
from app.models.about import AboutUser
from app.db.mongodb import mongodb
from datetime import datetime, timedelta
from bson import ObjectId
from typing import Optional

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
    users_collection = mongodb.get_collection("users")
    user = await users_collection.find_one({"_id": current_user["_id"]})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/me", response_model=User)
async def update_user(
    user_update: UserUpdate,
    current_user: dict = Depends(get_current_user)
):
    users_collection = mongodb.get_collection("users")
    update_data = user_update.model_dump(exclude_unset=True)
    
    if "password" in update_data:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
    
    update_data["updated_at"] = datetime.utcnow()
    
    result = await users_collection.update_one(
        {"_id": current_user["_id"]},
        {"$set": update_data}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    updated_user = await users_collection.find_one({"_id": current_user["_id"]})
    return updated_user

@router.put("/me/profile", response_model=User)
async def update_user_profile(
    profile_update: UserProfile,
    current_user: dict = Depends(get_current_user)
):
    users_collection = mongodb.get_collection("users")
    update_data = {"profile": profile_update.model_dump(exclude_unset=True)}
    update_data["updated_at"] = datetime.utcnow()
    
    result = await users_collection.update_one(
        {"_id": current_user["_id"]},
        {"$set": update_data}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    updated_user = await users_collection.find_one({"_id": current_user["_id"]})
    return updated_user

@router.get("/me/profile", response_model=UserProfile)
async def get_user_profile(current_user: dict = Depends(get_current_user)):
    users_collection = mongodb.get_collection("users")
    user = await users_collection.find_one({"_id": current_user["_id"]})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user.get("profile", {})

@router.put("/me/about", response_model=User)
async def update_user_about(
    about_update: AboutUser,
    current_user: dict = Depends(get_current_user)
):
    users_collection = mongodb.get_collection("users")
    update_data = {"about": about_update.model_dump(exclude_unset=True)}
    update_data["updated_at"] = datetime.utcnow()
    
    result = await users_collection.update_one(
        {"_id": current_user["_id"]},
        {"$set": update_data}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    updated_user = await users_collection.find_one({"_id": current_user["_id"]})
    return updated_user

@router.get("/me/about", response_model=AboutUser)
async def get_user_about(current_user: dict = Depends(get_current_user)):
    users_collection = mongodb.get_collection("users")
    user = await users_collection.find_one({"_id": current_user["_id"]})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user.get("about", {})

@router.post("/me/starter-answers", response_model=User)
async def submit_starter_answers(
    answers: StarterAnswers,
    current_user: dict = Depends(get_current_user)
):
    """
    Submit initial answers from the user and update their profile.
    This endpoint collects basic information about the user and updates their profile accordingly.
    """
    users_collection = mongodb.get_collection("users")
    
    # Calculate date of birth from age
    current_year = datetime.utcnow().year
    birth_year = current_year - answers.age
    date_of_birth = datetime(birth_year, 1, 1)  # Using January 1st as default date
    
    # Create or update user profile
    profile_data = {
        "preferred_name": answers.preferred_name,
        "gender": answers.gender,
        "date_of_birth": date_of_birth,
        "occupation": answers.occupation,
        "has_therapy_experience": answers.has_therapy_experience,
        "last_updated": datetime.utcnow()
    }
    
    # Update user document
    update_data = {
        "profile": profile_data,
        "updated_at": datetime.utcnow()
    }
    
    result = await users_collection.update_one(
        {"_id": current_user["_id"]},
        {"$set": update_data}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Return updated user
    updated_user = await users_collection.find_one({"_id": current_user["_id"]})
    return updated_user 
