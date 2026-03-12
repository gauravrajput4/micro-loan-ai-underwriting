from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from database.mongodb import users_collection
import os

router = APIRouter()
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440

class UserRegister(BaseModel):
    email: str
    password: str
    full_name: str
    user_type: str  # "unemployed" or "admin"
    phone: str = ""

class UserLogin(BaseModel):
    email: str
    password: str

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

@router.post("/register")
async def register(user: UserRegister):
    # Check if user exists
    if users_collection.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Hash password
    hashed_password = user.password
    
    # Create user document
    user_doc = {
        "email": user.email,
        "password": user.password,
        "full_name": user.full_name,
        "user_type": user.user_type,
        "phone": user.phone,
        "created_at": datetime.utcnow(),
        "is_active": True
    }
    
    result = users_collection.insert_one(user_doc)
    
    return {
        "message": "User registered successfully",
        "user_id": str(result.inserted_id),
        "email": user.email
    }

@router.post("/login")
async def login(user: UserLogin):
    # Find user
    db_user = users_collection.find_one({"email": user.email})
    
    if not db_user or user.password!=db_user["password"]:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Create access token
    access_token = create_access_token({
        "sub": user.email,
        "user_type": db_user["user_type"]
    })
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_type": db_user["user_type"],
        "full_name": db_user["full_name"],
        "email": db_user["email"]
    }
