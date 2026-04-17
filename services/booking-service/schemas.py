from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from models import BookingStatus


class BookingCreate(BaseModel):
    trip_id: UUID
    seat_number: int
    passenger_name: str
    passenger_tc: str = Field(..., min_length=11, max_length=11)
    total_price: float


class BookingResponse(BaseModel):
    id: UUID
    user_id: UUID
    trip_id: UUID
    seat_number: int
    passenger_name: str
    passenger_tc: str
    total_price: float
    status: BookingStatus
    created_at: datetime

    class Config:
        from_attributes = True


class BookingStatusUpdate(BaseModel):
    status: BookingStatus
