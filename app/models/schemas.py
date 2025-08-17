from pydantic import BaseModel, EmailStr
from typing import Optional

# User Registration Schema
class UserCreate(BaseModel):
    email: EmailStr
    name: str
    password: str

# User Login Schema
class UserLogin(BaseModel):
    email: EmailStr
    password: str

# Profile Schema
class UserProfileBase(BaseModel):
    interests: Optional[str] = None
    about: Optional[str] = None
    address: Optional[str] = None

# Profile Update
class UserProfileUpdate(UserProfileBase):
    pass

# Response Schema for User + Profile
class UserResponse(BaseModel):
    id: int
    email: EmailStr
    name: str
    profile: Optional[UserProfileBase] = None

    class Config:
        orm_mode = True
