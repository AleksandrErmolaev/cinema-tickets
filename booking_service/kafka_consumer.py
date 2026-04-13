from aiokafka import AIOKafkaConsumer
import json
import asyncio
from booking_service.crud import confirm_booking, cancel_booking
from booking_service.database import AsyncSessionLocal
import os

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS")

async def consume_payment_events():
    consumer = AIOKafkaConsumer(
        'payment.events',
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        group_id='booking-service-group',
        value_deserializer=lambda v: json.loads(v.decode()),
        auto_offset_reset='earliest'
    )
    await consumer.start()
    try:
        async for msg in consumer:
            event = msg.value
            event_type = event.get("event_type")
            data = event.get("data", {})
            booking_id = data.get("booking_id")
            status = data.get("status")

            async with AsyncSessionLocal() as db:
                if event_type == "payment.completed" and status == "completed":
                    await confirm_booking(db, booking_id)
                elif event_type == "payment.failed":
                    await cancel_booking(db, booking_id, reason="payment_failed")
    finally:
        await consumer.stop()