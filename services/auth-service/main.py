from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import JWTError

import models
from database import Base, engine, get_db
from routers.auth import router as auth_router
from schemas import UserResponse
from security import decode_token
from models import User

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Auth Service",
    description="Bus Ticket App — Authentication & Authorization",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
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


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    try:
        payload = decode_token(credentials.credentials)
        if payload.get("type") != "access":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Geçersiz token tipi.")
        
        user_id = payload.get("sub")
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Kullanıcı bulunamadı.")
        
        if not user.is_active:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Hesap aktif değil.")
            
        return user
    except JWTError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Geçersiz token.")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Sistem hatası.")


app.include_router(auth_router)


@app.get("/auth/me", response_model=UserResponse, tags=["Authentication"])
@app.get("/auth/me/", response_model=UserResponse, tags=["Authentication"], include_in_schema=False)
def get_my_info(current_user: User = Depends(get_current_user)):
    try:
        return {
            "id": current_user.id,
            "email": current_user.email,
            "full_name": current_user.full_name,
            "role": current_user.role,
            "is_active": current_user.is_active,
            "created_at": current_user.created_at
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="Kullanıcı bilgileri işlenemedi.")


@app.get("/auth/health", tags=["Health"])
@app.get("/auth/health/", tags=["Health"], include_in_schema=False)
def health():
    return {"status": "ok", "service": "auth-service"}
