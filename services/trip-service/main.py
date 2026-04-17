from fastapi import FastAPI, HTTPException, Depends, status, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from jose import JWTError, jwt

from database import Base, engine, get_db
from models import Trip, Seat, TripStatus
from schemas import TripCreate, TripResponse, TripDetailResponse, SeatResponse, SeatReserveRequest, SeatReleaseRequest
from config import settings

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Trip Service",
    description="Bus Ticket App — Trip & Seat Management",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer(auto_error=False)


def get_token_data(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[dict]:
    if not credentials:
        return None
    try:
        return jwt.decode(credentials.credentials, settings.secret_key, algorithms=[settings.algorithm])
    except JWTError:
        return None


def require_admin(token_data: Optional[dict] = Depends(get_token_data)):
    if not token_data or token_data.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin yetkisi gereklidir.")
    return token_data


def _create_seats(db: Session, trip_id: UUID, total_seats: int):
    seats = [Seat(trip_id=trip_id, seat_number=i + 1) for i in range(total_seats)]
    db.bulk_save_objects(seats)
    db.commit()


@app.post("/trips", response_model=TripResponse, status_code=201, tags=["Trips"])
def create_trip(
    payload: TripCreate,
    db: Session = Depends(get_db),
    _: dict = Depends(require_admin),
):
    trip = Trip(
        origin=payload.origin,
        destination=payload.destination,
        departure_time=payload.departure_time,
        arrival_time=payload.arrival_time,
        bus_name=payload.bus_name,
        bus_plate=payload.bus_plate,
        total_seats=payload.total_seats,
        available_seats=payload.total_seats,
        price=payload.price,
    )
    db.add(trip)
    db.commit()
    db.refresh(trip)
    _create_seats(db, trip.id, trip.total_seats)
    return trip


@app.get("/trips", response_model=List[TripResponse], tags=["Trips"])
def list_trips(
    origin: Optional[str] = Query(None),
    destination: Optional[str] = Query(None),
    date: Optional[str] = Query(None, description="YYYY-MM-DD"),
    db: Session = Depends(get_db),
):
    query = db.query(Trip).filter(Trip.status != TripStatus.cancelled)
    if origin:
        query = query.filter(Trip.origin.ilike(f"%{origin}%"))
    if destination:
        query = query.filter(Trip.destination.ilike(f"%{destination}%"))
    if date:
        try:
            target_date = datetime.strptime(date, "%Y-%m-%d").date()
            query = query.filter(
                Trip.departure_time >= datetime.combine(target_date, datetime.min.time()),
                Trip.departure_time < datetime.combine(target_date, datetime.max.time()),
            )
        except ValueError:
            raise HTTPException(status_code=400, detail="Geçersiz tarih formatı. YYYY-MM-DD kullanın.")
    return query.order_by(Trip.departure_time).all()


@app.get("/trips/{trip_id}", response_model=TripDetailResponse, tags=["Trips"])
def get_trip(trip_id: UUID, db: Session = Depends(get_db)):
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Sefer bulunamadı.")
    seats = db.query(Seat).filter(Seat.trip_id == trip_id).order_by(Seat.seat_number).all()
    result = TripDetailResponse.model_validate(trip)
    result.seats = [SeatResponse.model_validate(s) for s in seats]
    return result


@app.post("/trips/{trip_id}/reserve-seat", tags=["Seats"])
def reserve_seat(trip_id: UUID, payload: SeatReserveRequest, db: Session = Depends(get_db)):
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Sefer bulunamadı.")
    if trip.available_seats <= 0:
        raise HTTPException(status_code=409, detail="Bu seferde yer kalmadı.")
    seat = db.query(Seat).filter(
        Seat.trip_id == trip_id,
        Seat.seat_number == payload.seat_number,
    ).first()
    if not seat:
        raise HTTPException(status_code=404, detail="Koltuk bulunamadı.")
    if seat.is_reserved:
        raise HTTPException(status_code=409, detail="Bu koltuk zaten rezerve edilmiş.")
    seat.is_reserved = True
    seat.reserved_by = payload.user_id
    trip.available_seats -= 1
    db.commit()
    return {"message": "Koltuk başarıyla rezerve edildi.", "seat_number": seat.seat_number}


@app.post("/trips/{trip_id}/release-seat", tags=["Seats"])
def release_seat(trip_id: UUID, payload: SeatReleaseRequest, db: Session = Depends(get_db)):
    seat = db.query(Seat).filter(
        Seat.trip_id == trip_id,
        Seat.seat_number == payload.seat_number,
    ).first()
    if not seat:
        raise HTTPException(status_code=404, detail="Koltuk bulunamadı.")
    seat.is_reserved = False
    seat.reserved_by = None
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if trip:
        trip.available_seats += 1
    db.commit()
    return {"message": "Koltuk serbest bırakıldı."}


@app.get("/trips/health", tags=["Health"])
def health():
    return {"status": "ok", "service": "trip-service"}
