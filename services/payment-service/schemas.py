from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID
from models import PaymentStatus, PaymentMethod


class PaymentCreate(BaseModel):
    booking_id: UUID
    amount: float
    method: PaymentMethod
    # Mock card data (not stored)
    card_number: Optional[str] = Field(None, description="Mock - not stored")
    card_holder: Optional[str] = None


class PaymentResponse(BaseModel):
    id: UUID
    booking_id: UUID
    user_id: UUID
    amount: float
    method: PaymentMethod
    status: PaymentStatus
    transaction_id: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
