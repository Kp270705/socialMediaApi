from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    password: Optional[str] = None

class User(UserBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# UserDetails Schemas
class UserDetailsBase(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    bio: Optional[str] = None

class UserDetailsCreate(UserDetailsBase):
    user_id: int

class UserDetailsUpdate(UserDetailsBase):
    pass

class UserDetails(UserDetailsBase):
    id: int
    user_id: int
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Combined Schema for User with Details
class UserWithDetails(User):
    user_details: Optional[UserDetails] = None