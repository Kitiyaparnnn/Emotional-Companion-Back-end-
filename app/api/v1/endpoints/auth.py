from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import timedelta, datetime
from app.core.security import create_access_token, verify_password, get_password_hash
from app.models.user import UserCreate, User, Token
from app.db.mongodb import mongodb
from app.core.config import settings

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@router.post("/register", response_model=User)
async def register(user: UserCreate):
    users_collection = mongodb.get_collection("users")
    if await users_collection.find_one({"email": user.email}):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    user_dict = user.model_dump(exclude={"password"})
    user_dict["hashed_password"] = get_password_hash(user.password)
    user_dict["created_at"] = user_dict["updated_at"] = datetime.utcnow()
    
    result = await users_collection.insert_one(user_dict)
    
    created_user = await users_collection.find_one({"_id": result.inserted_id})
    return created_user

@router.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    users_collection = mongodb.get_collection("users")
    user = await users_collection.find_one({"email": form_data.username})
    
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user["_id"])}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"} 