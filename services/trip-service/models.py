from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
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


class Trip(Base):
    __tablename__ = "trips"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    origin = Column(String, nullable=False, index=True)
    destination = Column(String, nullable=False, index=True)
    departure_time = Column(DateTime(timezone=True), nullable=False)
    arrival_time = Column(DateTime(timezone=True), nullable=False)
    bus_name = Column(String, nullable=False)        # e.g. "Metro Turizm"
    bus_plate = Column(String, nullable=False)
    total_seats = Column(Integer, nullable=False, default=40)
    available_seats = Column(Integer, nullable=False, default=40)
    price = Column(Float, nullable=False)
    status = Column(SAEnum(TripStatus), default=TripStatus.scheduled)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class Seat(Base):
    __tablename__ = "seats"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trip_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    seat_number = Column(Integer, nullable=False)
    is_reserved = Column(Boolean, default=False)
    reserved_by = Column(UUID(as_uuid=True), nullable=True)
