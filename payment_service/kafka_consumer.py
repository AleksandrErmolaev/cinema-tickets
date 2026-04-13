from aiokafka import AIOKafkaConsumer
import json
import asyncio
import random
import os
from sqlalchemy.ext.asyncio import AsyncSession
from database import AsyncSessionLocal
from models import Payment, PaymentStatus
from kafka_producer import send_payment_event
from datetime import datetime

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS")
SUCCESS_RATE = float(os.getenv("PAYMENT_SUCCESS_RATE", "0.8"))

async def process_booking_created(event_data: dict):
    booking_id = event_data.get("booking_id")
    if not booking_id:
        return
    
    async with AsyncSessionLocal() as db:
        from sqlalchemy import select
        stmt = select(Payment).where(Payment.booking_id == booking_id)
        result = await db.execute(stmt)
        existing = result.scalar_one_or_none()
        if existing:
            print(f"Payment for booking {booking_id} already processed")
            return
        
        amount = 10.0
        success = random.random() < SUCCESS_RATE
        
        payment = Payment(
            booking_id=booking_id,
            amount=amount,
            status=PaymentStatus.COMPLETED if success else PaymentStatus.FAILED,
            completed_at=datetime.utcnow() if success else None
        )
        db.add(payment)
        await db.commit()
        
        status = "completed" if success else "failed"
        await send_payment_event(booking_id, status)
        print(f"Payment for booking {booking_id} {status}")

async def consume_booking_events():
    consumer = AIOKafkaConsumer(
        'booking.events',
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        group_id='payment-service-group',
        value_deserializer=lambda v: json.loads(v.decode()),
        auto_offset_reset='earliest'
    )
    await consumer.start()
    try:
        async for msg in consumer:
            event = msg.value
            event_type = event.get("event_type")
            data = event.get("data", {})
            if event_type == "booking.created":
                await process_booking_created(data)
    finally:
        await consumer.stop()