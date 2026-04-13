from pydantic import BaseModel
from datetime import datetime
from enum import Enum

class PaymentStatusEnum(str, Enum):
    pending = "pending"
    completed = "completed"
    failed = "failed"

class PaymentResponse(BaseModel):
    id: str
    booking_id: str
    amount: float
    status: PaymentStatusEnum
    created_at: datetime
    completed_at: datetime | None

class BookingCreatedEvent(BaseModel):
    booking_id: str
    user_id: str
    session_id: str
    seat_ids: list[str]
    expires_at: str

class PaymentInitiateRequest(BaseModel):
    booking_id: str
    amount: float = 10.0