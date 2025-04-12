from fastapi import APIRouter, HTTPException, status
from app.models.chat import LongTermMemory
from app.db.mongodb import mongodb
from app.core.security import encrypt_data, decrypt_data
from datetime import datetime
from typing import List
from bson import ObjectId

router = APIRouter()

@router.post("/traits", response_model=LongTermMemory)
async def create_memory_trait(trait: LongTermMemory):
    memory_collection = mongodb.get_collection("long_term_memory")
    trait_dict = trait.dict()
    
    # Encrypt sensitive trait data
    trait_dict["trait_value"] = encrypt_data(trait_dict["trait_value"])
    trait_dict["last_updated"] = datetime.utcnow()
    
    result = await memory_collection.insert_one(trait_dict)
    trait_dict["id"] = str(result.inserted_id)
    return LongTermMemory(**trait_dict)

@router.get("/traits/{user_id}", response_model=List[LongTermMemory])
async def get_user_traits(user_id: str, trait_type: str = None):
    memory_collection = mongodb.get_collection("long_term_memory")
    query = {"user_id": user_id}
    
    if trait_type:
        query["trait_type"] = trait_type
    
    traits = await memory_collection.find(query).sort("last_updated", -1).to_list(length=100)
    
    # Decrypt trait values
    for trait in traits:
        trait["trait_value"] = decrypt_data(trait["trait_value"])
    
    return [LongTermMemory(**trait) for trait in traits]

@router.put("/traits/{trait_id}")
async def update_memory_trait(trait_id: str, trait: LongTermMemory):
    memory_collection = mongodb.get_collection("long_term_memory")
    trait_dict = trait.dict()
    
    # Encrypt sensitive trait data
    trait_dict["trait_value"] = encrypt_data(trait_dict["trait_value"])
    trait_dict["last_updated"] = datetime.utcnow()
    
    result = await memory_collection.update_one(
        {"_id": ObjectId(trait_id)},
        {"$set": trait_dict}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Trait not found")
    return {"message": "Trait updated successfully"}

@router.delete("/traits/{trait_id}")
async def delete_memory_trait(trait_id: str):
    memory_collection = mongodb.get_collection("long_term_memory")
    result = await memory_collection.delete_one({"_id": ObjectId(trait_id)})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Trait not found")
    return {"message": "Trait deleted successfully"} 