from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from jose import JWTError, jwt
import httpx

from database import Base, engine, get_db
from models import Booking, BookingStatus
from schemas import BookingCreate, BookingResponse, BookingStatusUpdate
from kafka_producer import publish, stop_producer
from config import settings

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Booking Service",
    description="Bus Ticket App — Ticket Reservation",
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


@app.on_event("shutdown")
async def shutdown():
    await stop_producer()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    try:
        return jwt.decode(credentials.credentials, settings.secret_key, algorithms=[settings.algorithm])
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Geçersiz token.")


@app.post("/bookings", response_model=BookingResponse, status_code=201, tags=["Bookings"])
async def create_booking(
    payload: BookingCreate,
    db: Session = Depends(get_db),
    token_data: dict = Depends(get_current_user),
):
    user_id = token_data["sub"]

    # Check if seat is already booked in our DB
    existing = db.query(Booking).filter(
        Booking.trip_id == payload.trip_id,
        Booking.seat_number == payload.seat_number,
        Booking.status.notin_([BookingStatus.cancelled, BookingStatus.refunded]),
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="Bu koltuk zaten rezerve edilmiş.")

    # Reserve seat in trip service
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(
                f"{settings.trip_service_url}/trips/{payload.trip_id}/reserve-seat",
                json={"seat_number": payload.seat_number, "user_id": user_id},
                timeout=10.0,
            )
            if resp.status_code != 200:
                raise HTTPException(status_code=resp.status_code, detail=resp.json().get("detail", "Koltuk rezerve edilemedi."))
        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="Trip servisi erişilemiyor.")

    booking = Booking(
        user_id=user_id,
        trip_id=payload.trip_id,
        seat_number=payload.seat_number,
        passenger_name=payload.passenger_name,
        passenger_tc=payload.passenger_tc,
        total_price=payload.total_price,
        status=BookingStatus.pending,
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)

    # Publish Kafka event
    await publish("booking.created", {
        "booking_id": str(booking.id),
        "user_id": user_id,
        "trip_id": str(booking.trip_id),
        "seat_number": booking.seat_number,
        "passenger_name": booking.passenger_name,
        "total_price": booking.total_price,
    })

    return booking


@app.get("/bookings/me", response_model=List[BookingResponse], tags=["Bookings"])
def get_my_bookings(
    db: Session = Depends(get_db),
    token_data: dict = Depends(get_current_user),
):
    return db.query(Booking).filter(Booking.user_id == token_data["sub"]).all()


@app.get("/bookings/{booking_id}", response_model=BookingResponse, tags=["Bookings"])
def get_booking(
    booking_id: UUID,
    db: Session = Depends(get_db),
    token_data: dict = Depends(get_current_user),
):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Rezervasyon bulunamadı.")
    if str(booking.user_id) != token_data["sub"] and token_data.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Erişim yetkisi yok.")
    return booking


@app.delete("/bookings/{booking_id}", tags=["Bookings"])
async def cancel_booking(
    booking_id: UUID,
    db: Session = Depends(get_db),
    token_data: dict = Depends(get_current_user),
):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Rezervasyon bulunamadı.")
    if str(booking.user_id) != token_data["sub"] and token_data.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Erişim yetkisi yok.")
    if booking.status == BookingStatus.cancelled:
        raise HTTPException(status_code=409, detail="Rezervasyon zaten iptal edilmiş.")

    booking.status = BookingStatus.cancelled
    db.commit()

    # Release seat in trip service
    async with httpx.AsyncClient() as client:
        try:
            await client.post(
                f"{settings.trip_service_url}/trips/{booking.trip_id}/release-seat",
                json={"seat_number": booking.seat_number},
                timeout=10.0,
            )
        except httpx.RequestError:
            pass  # Log but don't fail the cancellation

    # Publish cancellation event
    await publish("booking.cancelled", {
        "booking_id": str(booking.id),
        "user_id": str(booking.user_id),
        "trip_id": str(booking.trip_id),
        "seat_number": booking.seat_number,
    })

    return {"message": "Rezervasyon başarıyla iptal edildi."}


@app.patch("/bookings/{booking_id}/status", response_model=BookingResponse, tags=["Bookings"])
def update_booking_status(
    booking_id: UUID,
    payload: BookingStatusUpdate,
    db: Session = Depends(get_db),
    token_data: dict = Depends(get_current_user),
):
    if token_data.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin yetkisi gereklidir.")
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Rezervasyon bulunamadı.")
    booking.status = payload.status
    db.commit()
    db.refresh(booking)
    return booking


@app.get("/bookings/health", tags=["Health"])
def health():
    return {"status": "ok", "service": "booking-service"}
