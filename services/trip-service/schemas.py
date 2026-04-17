from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from models import TripStatus


class TripCreate(BaseModel):
    origin: str
    destination: str
    departure_time: datetime
    arrival_time: datetime
    bus_name: str
    bus_plate: str
    total_seats: int = 40
    price: float


class TripResponse(BaseModel):
    id: UUID
    origin: str
    destination: str
    departure_time: datetime
    arrival_time: datetime
    bus_name: str
    bus_plate: str
    total_seats: int
    available_seats: int
    price: float
    status: TripStatus
    created_at: datetime

    class Config:
        from_attributes = True


class SeatResponse(BaseModel):
    id: UUID
    trip_id: UUID
    seat_number: int
    is_reserved: bool

    class Config:
        from_attributes = True


class TripDetailResponse(TripResponse):
    seats: List[SeatResponse] = []


class SeatReserveRequest(BaseModel):
    seat_number: int
    user_id: UUID


class SeatReleaseRequest(BaseModel):
    seat_number: int
