from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from models import TripStatus


# --- Company Schemas ---
class CompanyBase(BaseModel):
    name: str
    logo_url: Optional[str] = None
    rating: float = 0.0
    contact_info: Optional[str] = None

class CompanyCreate(CompanyBase):
    pass

class CompanyResponse(CompanyBase):
    id: UUID

    class Config:
        from_attributes = True


# --- Seat Schemas ---
class SeatBase(BaseModel):
    seat_number: int
    is_reserved: bool = False
    gender: Optional[str] = None # "E" or "K"

class SeatResponse(SeatBase):
    id: UUID
    trip_id: UUID

    class Config:
        from_attributes = True


# --- Trip Schemas ---
class TripBase(BaseModel):
    origin: str
    destination: str
    departure_time: datetime
    arrival_time: datetime
    bus_plate: str
    bus_type: str = "Standard"
    bus_layout: str = "2+2"
    total_seats: int = 40
    price: float
    status: TripStatus = TripStatus.scheduled
    amenities: Optional[str] = None
    description: Optional[str] = None
    estimated_duration: Optional[str] = None

class TripCreate(TripBase):
    company_id: Optional[UUID] = None

class TripResponse(TripBase):
    id: UUID
    available_seats: int
    created_at: datetime
    company: Optional[CompanyResponse] = None

    class Config:
        from_attributes = True

class TripDetailResponse(TripResponse):
    seats: List[SeatResponse] = []
