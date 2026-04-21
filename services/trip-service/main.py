from fastapi import FastAPI, HTTPException, Depends, status, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from uuid import UUID
from jose import JWTError, jwt
from datetime import datetime, timezone

from database import Base, engine, get_db
from models import Trip, Seat, TripStatus, Company
from schemas import (
    TripCreate, TripResponse, TripDetailResponse, SeatResponse, 
    CompanyCreate, CompanyResponse
)
from websocket_manager import manager
from config import settings

# Create/Update tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Trip Service",
    description="Bus Ticket App — Managing Bus Trips and Seats",
    version="1.0.0",
    redirect_slashes=False,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()

# Authentication Helper
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    try:
        return jwt.decode(credentials.credentials, settings.secret_key, algorithms=[settings.algorithm])
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Geçersiz token.")

# --- Company Endpoints ---

@app.get("/companies", response_model=List[CompanyResponse], tags=["Companies"])
def get_companies(db: Session = Depends(get_db)):
    return db.query(Company).all()

@app.post("/companies", response_model=CompanyResponse, tags=["Companies"])
def create_company(company_in: CompanyCreate, db: Session = Depends(get_db), token_data: dict = Depends(get_current_user)):
    company = Company(**company_in.model_dump())
    db.add(company)
    db.commit()
    db.refresh(company)
    return company

# --- Trip Endpoints ---

@app.get("/trips", response_model=List[TripResponse], tags=["Trips"])
def get_trips(
    origin: Optional[str] = None,
    destination: Optional[str] = None,
    company_id: Optional[UUID] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Trip).options(joinedload(Trip.company)).filter(Trip.status != TripStatus.cancelled)
    
    if origin:
        query = query.filter(Trip.origin.ilike(f"%{origin}%"))
    if destination:
        query = query.filter(Trip.destination.ilike(f"%{destination}%"))
    if company_id:
        query = query.filter(Trip.company_id == company_id)
    if min_price is not None:
        query = query.filter(Trip.price >= min_price)
    if max_price is not None:
        query = query.filter(Trip.price <= max_price)
        
    return query.all()

@app.get("/trips/{trip_id}", response_model=TripDetailResponse, tags=["Trips"])
def get_trip_detail(trip_id: UUID, db: Session = Depends(get_db)):
    trip = db.query(Trip).options(joinedload(Trip.company)).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Sefer bulunamadı.")
    
    seats = db.query(Seat).filter(Seat.trip_id == trip_id).order_by(Seat.seat_number).all()
    
    # We return a dict to match what TripDetailResponse expects
    return {
        "id": trip.id,
        "origin": trip.origin,
        "destination": trip.destination,
        "departure_time": trip.departure_time,
        "arrival_time": trip.arrival_time,
        "bus_plate": trip.bus_plate,
        "bus_type": trip.bus_type,
        "bus_layout": trip.bus_layout,
        "total_seats": trip.total_seats,
        "available_seats": trip.available_seats,
        "price": trip.price,
        "status": trip.status,
        "amenities": trip.amenities,
        "description": trip.description,
        "estimated_duration": trip.estimated_duration,
        "created_at": trip.created_at,
        "company": trip.company,
        "seats": seats
    }

@app.post("/trips", response_model=TripResponse, tags=["Trips"])
def create_trip(trip_in: TripCreate, db: Session = Depends(get_db), token_data: dict = Depends(get_current_user)):
    trip_data = trip_in.model_dump()
    trip = Trip(**trip_data)
    db.add(trip)
    db.commit()
    db.refresh(trip)
    
    # Initialize seats
    for i in range(1, trip.total_seats + 1):
        seat = Seat(trip_id=trip.id, seat_number=i)
        db.add(seat)
    
    db.commit()
    return trip

@app.patch("/trips/{trip_id}/status", tags=["Trips"])
def update_trip_status(trip_id: UUID, status: str, db: Session = Depends(get_db), token_data: dict = Depends(get_current_user)):
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Sefer bulunamadı.")
    
    trip.status = status
    db.commit()
    return {"message": "Sefer durumu güncellendi."}

# Aligning with Booking Service expectations
@app.post("/trips/{trip_id}/reserve-seat")
async def reserve_seat(
    trip_id: UUID, 
    payload: dict, # {"seat_number": int, "user_id": UUID, "gender": Optional[str]}
    db: Session = Depends(get_db)
):
    seat_number = payload.get("seat_number")
    user_id = payload.get("user_id")
    gender = payload.get("gender")

    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Sefer bulunamadı.")
    
    seat = db.query(Seat).filter(Seat.trip_id == trip_id, Seat.seat_number == seat_number).first()
    if not seat:
        raise HTTPException(status_code=404, detail="Koltuk bulunamadı.")
    
    if seat.is_reserved:
        raise HTTPException(status_code=400, detail="Koltuk zaten dolu.")
    
    seat.is_reserved = True
    seat.reserved_by = user_id
    seat.gender = gender
    trip.available_seats -= 1
    db.commit()
    
    await manager.broadcast(trip_id, {
        "type": "seat_update", 
        "seat_number": seat_number, 
        "is_reserved": True, 
        "gender": gender
    })
    
    return {"message": "Koltuk başarıyla rezerve edildi."}

@app.post("/trips/{trip_id}/release-seat")
async def release_seat(trip_id: UUID, payload: dict, db: Session = Depends(get_db)):
    seat_number = payload.get("seat_number")
    
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Sefer bulunamadı.")
    
    seat = db.query(Seat).filter(Seat.trip_id == trip_id, Seat.seat_number == seat_number).first()
    if not seat:
        raise HTTPException(status_code=404, detail="Koltuk bulunamadı.")
    
    if not seat.is_reserved:
        return {"message": "Koltuk zaten boş."}
    
    seat.is_reserved = False
    seat.reserved_by = None
    seat.gender = None
    trip.available_seats += 1
    db.commit()
    
    await manager.broadcast(trip_id, {"type": "seat_update", "seat_number": seat_number, "is_reserved": False})
    
    return {"message": "Koltuk serbest bırakıldı."}

@app.get("/trips/stats/summary", tags=["Trips"])
def get_stats(db: Session = Depends(get_db)):
    total_trips = db.query(Trip).count()
    total_cities = db.query(Trip.origin).union(db.query(Trip.destination)).distinct().count()
    return {
        "total_trips": total_trips,
        "total_cities": total_cities,
        "happy_users": 150000,
        "rating": 4.8
    }

from fastapi import WebSocket, WebSocketDisconnect

@app.websocket("/ws/{trip_id}")
async def websocket_endpoint(websocket: WebSocket, trip_id: str):
    await manager.connect(websocket, trip_id)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket, trip_id)
