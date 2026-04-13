from fastapi import FastAPI, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db, engine
from models import Base
from schemas import BookingCreate, BookingResponse
from crud import create_booking, get_user_bookings, cancel_booking
from kafka_producer import start_kafka_producer, stop_kafka_producer
from kafka_consumer import consume_payment_events
import asyncio
import uuid

app = FastAPI(title="Booking Service")

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await start_kafka_producer()
    asyncio.create_task(consume_payment_events())

@app.on_event("shutdown")
async def shutdown():
    await stop_kafka_producer()

@app.post("/bookings", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
async def new_booking(booking_data: BookingCreate, db: AsyncSession = Depends(get_db)):
    booking, error = await create_booking(db, booking_data.user_id, booking_data.session_id, booking_data.seat_ids)
    if error:
        raise HTTPException(status_code=409, detail=error)
    return BookingResponse(
        id=booking.id,
        user_id=booking.user_id,
        session_id=booking.session_id,
        seat_ids=booking.seat_ids,
        status=booking.status,
        created_at=booking.created_at,
        expires_at=booking.expires_at
    )

@app.get("/bookings/user/{user_id}", response_model=list[BookingResponse])
async def list_user_bookings(user_id: str, db: AsyncSession = Depends(get_db)):
    bookings = await get_user_bookings(db, user_id)
    return [BookingResponse(
        id=b.id, user_id=b.user_id, session_id=b.session_id,
        seat_ids=b.seat_ids, status=b.status, created_at=b.created_at, expires_at=b.expires_at
    ) for b in bookings]

@app.delete("/bookings/{booking_id}")
async def cancel(booking_id: str, db: AsyncSession = Depends(get_db)):
    await cancel_booking(db, booking_id, reason="user_cancelled")
    return {"status": "cancelled"}

@app.get("/seats/{session_id}/available")
async def check_available(session_id: str, seat_ids: list[str] = None):
    redis = await get_redis()
    if seat_ids:
        locked = []
        for seat in seat_ids:
            key = f"seat:lock:{session_id}:{seat}"
            val = await redis.get(key)
            if val:
                locked.append(seat)
        available = [s for s in seat_ids if s not in locked]
        return {"available": available, "locked": locked}
    else:
        return {"message": "Please provide seat_ids list"}