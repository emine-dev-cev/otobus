from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from jose import JWTError, jwt

from database import Base, engine, get_db
from models import UserProfile
from schemas import UserProfileCreate, UserProfileUpdate, UserProfileResponse
from config import settings

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="User Service",
    description="Bus Ticket App — User Profile Management",
    version="1.0.0",
    redirect_slashes=False,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()


def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    try:
        payload = jwt.decode(credentials.credentials, settings.secret_key, algorithms=[settings.algorithm])
        return payload
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Geçersiz token.")


@app.post("/users", response_model=UserProfileResponse, status_code=201, tags=["Users"])
def create_profile(payload: UserProfileCreate, db: Session = Depends(get_db)):
    existing = db.query(UserProfile).filter(UserProfile.auth_user_id == payload.auth_user_id).first()
    if existing:
        raise HTTPException(status_code=409, detail="Profil zaten mevcut.")
    profile = UserProfile(**payload.model_dump())
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


@app.get("/users/me", response_model=UserProfileResponse, tags=["Users"])
def get_my_profile(
    token_data: dict = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    profile = db.query(UserProfile).filter(
        UserProfile.auth_user_id == token_data["sub"]
    ).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profil bulunamadı.")
    return profile


@app.get("/users/health", tags=["Health"])
@app.get("/users/health/", tags=["Health"], include_in_schema=False)
def health():
    return {"status": "ok", "service": "user-service"}
