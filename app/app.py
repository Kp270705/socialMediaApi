from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
import hashlib

# Import our modules
from initResources.db import SessionLocal, engine, get_db, Base
from models import models, schemas

# Create database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(title="User CRUD API", description="Simple CRUD API with related tables")

# Utility function to hash passwords (simple hash - use bcrypt in production)
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

# USER CRUD OPERATIONS

@app.post("/users/", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    
    # Check if user already exists
    db_user = db.query(models.User).filter(
        (models.User.email == user.email) | (models.User.username == user.username)
    ).first()
    
    if db_user:
        raise HTTPException(
            status_code=400, 
            detail="Email or username already registered"
        )
    
    # Hash the password
    hashed_password = hash_password(user.password)
    
    # Create new user
    db_user = models.User(
        email=user.email,
        username=user.username,
        password=hashed_password
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

@app.get("/users/", response_model=List[schemas.UserWithDetails])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all users with their details"""
    users = db.query(models.User).offset(skip).limit(limit).all()
    return users

@app.get("/users/{user_id}", response_model=schemas.UserWithDetails)
def read_user(user_id: int, db: Session = Depends(get_db)):
    """Get a specific user by ID with details"""
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.put("/users/{user_id}", response_model=schemas.User)
def update_user(user_id: int, user_update: schemas.UserUpdate, db: Session = Depends(get_db)):
    """Update user information"""
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update fields that are provided
    update_data = user_update.dict(exclude_unset=True)
    
    # Hash password if it's being updated
    if "password" in update_data:
        update_data["password"] = hash_password(update_data["password"])
    
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    db.commit()
    db.refresh(db_user)
    
    return db_user

@app.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """Delete a user and their details"""
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(db_user)
    db.commit()
    
    return {"message": "User deleted successfully"}

# USER DETAILS CRUD OPERATIONS

@app.post("/users/{user_id}/details/", response_model=schemas.UserDetails, status_code=status.HTTP_201_CREATED)
def create_user_details(user_id: int, details: schemas.UserDetailsBase, db: Session = Depends(get_db)):
    """Create or update user details"""
    
    # Check if user exists
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if details already exist
    existing_details = db.query(models.UserDetails).filter(models.UserDetails.user_id == user_id).first()
    
    if existing_details:
        raise HTTPException(status_code=400, detail="User details already exist. Use PUT to update.")
    
    # Create new user details
    db_details = models.UserDetails(user_id=user_id, **details.dict())
    
    db.add(db_details)
    db.commit()
    db.refresh(db_details)
    
    return db_details

@app.get("/users/{user_id}/details/", response_model=schemas.UserDetails)
def read_user_details(user_id: int, db: Session = Depends(get_db)):
    """Get user details by user ID"""
    db_details = db.query(models.UserDetails).filter(models.UserDetails.user_id == user_id).first()
    
    if db_details is None:
        raise HTTPException(status_code=404, detail="User details not found")
    
    return db_details

@app.put("/users/{user_id}/details/", response_model=schemas.UserDetails)
def update_user_details(user_id: int, details_update: schemas.UserDetailsUpdate, db: Session = Depends(get_db)):
    """Update user details"""
    db_details = db.query(models.UserDetails).filter(models.UserDetails.user_id == user_id).first()
    
    if db_details is None:
        raise HTTPException(status_code=404, detail="User details not found")
    
    # Update fields that are provided
    update_data = details_update.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(db_details, field, value)
    
    db.commit()
    db.refresh(db_details)
    
    return db_details

@app.delete("/users/{user_id}/details/")
def delete_user_details(user_id: int, db: Session = Depends(get_db)):
    """Delete user details"""
    db_details = db.query(models.UserDetails).filter(models.UserDetails.user_id == user_id).first()
    
    if db_details is None:
        raise HTTPException(status_code=404, detail="User details not found")
    
    db.delete(db_details)
    db.commit()
    
    return {"message": "User details deleted successfully"}

# Root endpoint
@app.get("/")
def read_root():
    return {"message": "Welcome to User CRUD API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)