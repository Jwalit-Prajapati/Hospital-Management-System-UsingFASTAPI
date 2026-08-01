from pydantic import BaseModel, ConfigDict, EmailStr
from typing import Optional
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    ADMIN = "admin"
    DOCTOR = "doctor"
    PATIENT = "patient"
    STAFF = "staff"

#Shared properties for User model
class UserBase(BaseModel):
    username: str
    email: EmailStr
    is_active: bool = True
    role: UserRole

# Properties for User model when creating a new user
class UserCreate(UserBase):
    password: str
    reference_id: Optional[str] = None  # Optional reference ID for doctors and patients

# Properties for User model when updating an existing user
class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None
    role: Optional[UserRole] = None
    reference_id: Optional[str] = None

# Properties for User model when reading user data from the database    
class UserInDBBase(UserBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)  # Enable ORM mode for compatibility with SQLAlchemy models

# Properties for User model when returning user data in API responses
class User(UserInDBBase):
    pass

# Properties for User model when storing user data in the database
class UserInDB(UserInDBBase):
    hashed_password: str

# Token model for authentication
class Token(BaseModel):
    access_token:str
    token_type:str

class TokenPayload(BaseModel):
    sub: Optional[str] = None
    role: Optional[int] = None
