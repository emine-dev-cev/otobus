from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, ForeignKey, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
import enum
from datetime import datetime, timezone
from database import Base


class TripStatus(str, enum.Enum):
    scheduled = "scheduled"
    boarding = "boarding"
    departed = "departed"
    arrived = "arrived"
    cancelled = "cancelled"


class Company(Base):
    __tablename__ = "companies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False, index=True)
    logo_url = Column(String, nullable=True)
    rating = Column(Float, default=0.0)
    contact_info = Column(String, nullable=True)
    
    trips = relationship("Trip", back_populates="company")


class Trip(Base):
    __tablename__ = "trips"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    origin = Column(String, nullable=False, index=True)
    destination = Column(String, nullable=False, index=True)
    departure_time = Column(DateTime(timezone=True), nullable=False)
    arrival_time = Column(DateTime(timezone=True), nullable=False)
    
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=True)
    company = relationship("Company", back_populates="trips")

    bus_plate = Column(String, nullable=False)
    bus_type = Column(String, nullable=True, default="Standard")
    bus_layout = Column(String, nullable=False, default="2+2") # "2+1" or "2+2"
    
    total_seats = Column(Integer, nullable=False, default=40)
    available_seats = Column(Integer, nullable=False, default=40)
    price = Column(Float, nullable=False)
    status = Column(SAEnum(TripStatus), default=TripStatus.scheduled)
    
    # Advanced Details
    amenities = Column(String, nullable=True)        # e.g. "WiFi, Power Outlet, TV"
    description = Column(String, nullable=True)     # Detailed trip description
    estimated_duration = Column(String, nullable=True) # e.g. "4h 30m"
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class Seat(Base):
    __tablename__ = "seats"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trip_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    seat_number = Column(Integer, nullable=False)
    is_reserved = Column(Boolean, default=False)
    reserved_by = Column(UUID(as_uuid=True), nullable=True)
    gender = Column(String, nullable=True) # "E" (Erkek), "K" (Kadın)
