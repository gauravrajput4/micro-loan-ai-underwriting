from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from jose import jwt
from datetime import datetime, timedelta
import os
from passlib.context import CryptContext

try:
    from database.mongodb import users_collection
except ModuleNotFoundError:
    from ..database.mongodb import users_collection

router = APIRouter()

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserRegister(BaseModel):
    email: str = Field(...,)
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


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, stored_password: str) -> bool:
    # Support both hashed and old plaintext records during migration.
    if stored_password.startswith("$2"):
        return pwd_context.verify(plain_password, stored_password)
    return plain_password == stored_password

@router.post("/register")
async def register(user: UserRegister):
    canonical_email = user.email.strip().lower()
    # Check if user exists
    if users_collection.find_one({"email": canonical_email}):
        raise HTTPException(status_code=400, detail="Email already registered")
    
    if user.user_type not in {"unemployed", "admin"}:
        raise HTTPException(status_code=400, detail="Invalid user_type")

    hashed_password = hash_password(user.password)
    
    # Create user document
    user_doc = {
        "email": canonical_email,
        "password": hashed_password,
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
        "email": canonical_email
    }

@router.post("/login")
async def login(user: UserLogin):
    canonical_email = user.email.strip().lower()
    # Find user
    db_user = users_collection.find_one({"email": canonical_email})
    
    if not db_user or not verify_password(user.password, db_user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Create access token
    access_token = create_access_token({
        "sub": canonical_email,
        "user_type": db_user["user_type"]
    })
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_type": db_user["user_type"],
        "full_name": db_user["full_name"],
        "email": db_user["email"]
    }
