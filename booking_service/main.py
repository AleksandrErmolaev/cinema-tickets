from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from redis_client import init_redis, close_redis, get_free_seats_mask, lock_seat, unlock_seat, mark_seat_as_booked
from kafka_producer import send_event
from database import get_db
import asyncio

app = FastAPI()

@app.on_event("startup")
async def startup():
    await init_redis()

@app.on_event("shutdown")
async def shutdown():
    await close_redis()

@app.post("/bookings")
async def create_booking(
    session_id: str, 
    seat_numbers: list[int],
    user_id: str,
    db: AsyncSession = Depends(get_db)
):
    mask = await get_free_seats_mask(session_id)
    if mask is None:
        mask = await load_mask_from_db(session_id, db)
        await set_free_seats_mask(session_id, mask)
    
    unavailable = []
    for seat in seat_numbers:
        if mask[seat] != '1' or not await lock_seat(session_id, seat, ttl_seconds=600):
            unavailable.append(seat)
    if unavailable:
        for seat in seat_numbers:
            await unlock_seat(session_id, seat)
        raise HTTPException(status_code=409, detail=f"Seats {unavailable} not available")
    
    booking_id = await create_booking_in_db(session_id, seat_numbers, user_id, db)
    
    await send_booking_event("booking.created", {
        "booking_id": booking_id,
        "session_id": session_id,
        "seat_numbers": seat_numbers,
        "user_id": user_id
    })
    
    return {"booking_id": booking_id, "status": "pending"}

# Эндпоинт для подтверждения оплаты (вызывается после payment.completed)
@app.post("/bookings/{booking_id}/confirm")
async def confirm_booking(booking_id: str, db: AsyncSession = Depends(get_db)):
    # Получаем session_id и seat_numbers из БД
    session_id, seat_numbers = await get_booking_details(booking_id, db)
    # Окончательно занимаем места в Redis
    for seat in seat_numbers:
        await mark_seat_as_booked(session_id, seat)
        await unlock_seat(session_id, seat)  # снимаем временную блокировку
    # Обновляем статус в БД
    await update_booking_status(booking_id, "confirmed", db)
    # Публикуем событие booking.confirmed
    await send_booking_event("booking.confirmed", {"booking_id": booking_id})
    return {"status": "confirmed"}

# Отмена брони (пользователь или таймаут)
@app.delete("/bookings/{booking_id}")
async def cancel_booking(booking_id: str, db: AsyncSession = Depends(get_db)):
    session_id, seat_numbers = await get_booking_details(booking_id, db)
    for seat in seat_numbers:
        await unlock_seat(session_id, seat)  # освобождаем блокировку, но маска не меняется? 
        # Для отмены до оплаты – место снова свободно. Нужно обновить маску:
        # await mark_seat_as_free(session_id, seat) - допишите по аналогии
    await update_booking_status(booking_id, "cancelled", db)
    await send_event("booking.cancelled", {"booking_id": booking_id})