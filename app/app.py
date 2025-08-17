from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from app.initResources.db import Base, engine, get_db
from app.models import models, schemas

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="User Management API")

# Register User
@app.post("/register", response_model=schemas.UserResponse)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = models.User(
        email=user.email,
        name=user.name,
        password=user.password  # ⚠️ In production, hash the password!
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


# Login User
@app.post("/login")
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()

    # if not db_user or db_user.password != user.password:
    #     raise HTTPException(status_code=400, detail="Invalid email or password")

    if db_user is None or db_user.password != user.password:
        raise HTTPException(status_code=400, detail="Invalid email or password")

    return {"message": "Login successful", "user_id": db_user.id}


# Update User Profile
@app.put("/users/{user_id}/profile", response_model=schemas.UserResponse)
def update_profile(user_id: int, profile: schemas.UserProfileUpdate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    if db_user.profile:
        db_user.profile.interests = profile.interests
        db_user.profile.about = profile.about
        db_user.profile.address = profile.address
    else:
        new_profile = models.UserProfile(
            interests=profile.interests,
            about=profile.about,
            address=profile.address,
            owner=db_user
        )
        db.add(new_profile)

    db.commit()
    db.refresh(db_user)
    return db_user


# Get User with Profile
@app.get("/users/{user_id}", response_model=schemas.UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user
