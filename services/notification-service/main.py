import asyncio
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List
from jose import JWTError, jwt

from database import Base, engine, get_db
from models import Notification
from schemas import NotificationResponse
from kafka_consumer import consume
from config import settings

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Notification Service",
    description="Bus Ticket App — Email & SMS Notifications via Kafka",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()
_consumer_task = None


@app.on_event("startup")
async def startup():
    global _consumer_task
    _consumer_task = asyncio.create_task(consume())


@app.on_event("shutdown")
async def shutdown():
    if _consumer_task:
        _consumer_task.cancel()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    try:
        return jwt.decode(credentials.credentials, settings.secret_key, algorithms=[settings.algorithm])
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Geçersiz token.")


@app.get("/notifications/me", response_model=List[NotificationResponse], tags=["Notifications"])
def get_my_notifications(
    db: Session = Depends(get_db),
    token_data: dict = Depends(get_current_user),
):
    return db.query(Notification).filter(
        Notification.user_id == token_data["sub"]
    ).order_by(Notification.created_at.desc()).limit(50).all()


@app.get("/notifications/health", tags=["Health"])
def health():
    return {"status": "ok", "service": "notification-service"}
