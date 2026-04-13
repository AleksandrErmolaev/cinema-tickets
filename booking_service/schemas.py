from pydantic import BaseModel, Field
from typing import List
from datetime import datetime
from enum import Enum

class BookingStatusEnum(str, Enum):
    pending = "pending"
    confirmed = "confirmed"
    cancelled = "cancelled"
    expired = "expired"

class BookingCreate(BaseModel):
    user_id: str
    session_id: str
    seat_ids: List[str]

class BookingResponse(BaseModel):
    id: str
    user_id: str
    session_id: str
    seat_ids: List[str]
    status: BookingStatusEnum
    created_at: datetime
    expires_at: datetime | None

class PaymentCompletedEvent(BaseModel):
    booking_id: str
    payment_id: str
    status: str