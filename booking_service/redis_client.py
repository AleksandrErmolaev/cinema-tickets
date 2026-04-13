import redis.asyncio as redis
import os
import json

redis_client = None

async def init_redis():
    global redis_client
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    redis_client = await redis.from_url(redis_url, decode_responses=True)
    print("Redis connected")

async def close_redis():
    if redis_client:
        await redis_client.close()

async def get_free_seats_mask(session_id: str) -> str | None:
    """Возвращает битовую маску свободных мест для сеанса"""
    key = f"seats:free:{session_id}"
    return await redis_client.get(key)

async def set_free_seats_mask(session_id: str, mask: str, ttl_seconds: int = 3600):
    """Сохраняет маску свободных мест в кэш на час"""
    key = f"seats:free:{session_id}"
    await redis_client.setex(key, ttl_seconds, mask)

async def lock_seat(session_id: str, seat_number: int, ttl_seconds: int = 600) -> bool:
    """
    Временная блокировка места (на время бронирования).
    Возвращает True, если место не заблокировано и блокировка установлена.
    """
    lock_key = f"seat:lock:{session_id}:{seat_number}"
    # setnx (set if not exists) с TTL
    return await redis_client.setnx(lock_key, "locked") and await redis_client.expire(lock_key, ttl_seconds)

async def unlock_seat(session_id: str, seat_number: int):
    """Освобождает место (при отмене или истечении времени)"""
    lock_key = f"seat:lock:{session_id}:{seat_number}"
    await redis_client.delete(lock_key)

async def mark_seat_as_booked(session_id: str, seat_number: int):
    """
    Постоянно занимает место в маске свободных мест (после оплаты).
    Обновляем маску: меняем бит с 1 на 0.
    """
    mask_key = f"seats:free:{session_id}"
    mask = await redis_client.get(mask_key)
    if mask and len(mask) > seat_number:
        # Инвертируем бит (1 -> 0)
        new_mask = mask[:seat_number] + '0' + mask[seat_number+1:]
        await redis_client.set(mask_key, new_mask)
        # Можно продлить TTL
        await redis_client.expire(mask_key, 3600)