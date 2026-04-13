from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from models import Booking, BookingStatus
from redis_client import get_redis
from kafka_producer import send_event
from datetime import datetime, timedelta
import os
import httpx

BOOKING_TTL_MINUTES = int(os.getenv("BOOKING_TTL_MINUTES", "10"))

async def reserve_seats(session_id: str, seat_ids: list[str], booking_id: str, ttl_seconds: int = BOOKING_TTL_MINUTES * 60):
    """Резервирует места в Redis с TTL. Возвращает True, если все места свободны и заблокированы."""
    redis = await get_redis()
    pipe = redis.pipeline()
    for seat in seat_ids:
        key = f"seat:lock:{session_id}:{seat}"
        pipe.setnx(key, booking_id)
        pipe.expire(key, ttl_seconds)
    results = await pipe.execute()
    setnx_results = results[0::2]
    if all(setnx_results):
        return True
    else:
        for idx, seat in enumerate(seat_ids):
            if setnx_results[idx] == 0:
                for j in range(idx):
                    key = f"seat:lock:{session_id}:{seat_ids[j]}"
                    await redis.delete(key)
        return False

async def release_seats(session_id: str, seat_ids: list[str], booking_id: str):
    """Освобождает места, если они заблокированы этим бронированием."""
    redis = await get_redis()
    for seat in seat_ids:
        key = f"seat:lock:{session_id}:{seat}"
        current = await redis.get(key)
        if current == booking_id:
            await redis.delete(key)

async def create_booking(db: AsyncSession, user_id: str, session_id: str, seat_ids: list[str]):
    booking_id = str(uuid.uuid4())
    reserved = await reserve_seats(session_id, seat_ids, booking_id)
    if not reserved:
        return None, "Seats already taken"
    
    expires_at = datetime.utcnow() + timedelta(minutes=BOOKING_TTL_MINUTES)
    booking = Booking(
        id=booking_id,
        user_id=user_id,
        session_id=session_id,
        seat_ids=seat_ids,
        status=BookingStatus.PENDING,
        expires_at=expires_at
    )
    db.add(booking)
    await db.commit()
    await db.refresh(booking)
    
    await send_event("booking.events", "booking.created", {
        "booking_id": booking.id,
        "user_id": user_id,
        "session_id": session_id,
        "seat_ids": seat_ids,
        "expires_at": expires_at.isoformat()
    })
    return booking, None

async def confirm_booking(db: AsyncSession, booking_id: str):
    stmt = select(Booking).where(Booking.id == booking_id)
    result = await db.execute(stmt)
    booking = result.scalar_one_or_none()
    if not booking or booking.status != BookingStatus.PENDING:
        return
    booking.status = BookingStatus.CONFIRMED
    await db.commit()

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(f"http://auth_service:8001/internal/users/{booking.user_id}/email")
            user_email = resp.json().get("email") if resp.status_code == 200 else None
        except Exception:
            user_email = None

    movie_title = "Unknown Movie"
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(f"http://movie_service:8000/showtimes/{booking.session_id}/movie")
            if resp.status_code == 200:
                movie_title = resp.json().get("movie_title", movie_title)
        except Exception:
            pass

    await send_event(
        "booking.events",
        "booking.confirmed",
        {
            "booking_id": booking_id,
            "user_email": user_email,
            "seat_ids": booking.seat_ids,
            "movie_title": movie_title
        }
    )

async def cancel_booking(db: AsyncSession, booking_id: str, reason: str = "user_cancelled"):
    stmt = select(Booking).where(Booking.id == booking_id)
    result = await db.execute(stmt)
    booking = result.scalar_one_or_none()
    if not booking or booking.status != BookingStatus.PENDING:
        return
    booking.status = BookingStatus.CANCELLED
    await db.commit()
    await release_seats(booking.session_id, booking.seat_ids, booking_id)
    await send_event("booking.events", "booking.cancelled", {"booking_id": booking_id, "reason": reason})

async def get_user_bookings(db: AsyncSession, user_id: str):
    stmt = select(Booking).where(Booking.user_id == user_id).order_by(Booking.created_at.desc())
    result = await db.execute(stmt)
    return result.scalars().all()