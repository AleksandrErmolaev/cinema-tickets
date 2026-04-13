from aiokafka import AIOKafkaConsumer
import json
import asyncio
import os
from minio_client import save_event_to_minio

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
TOPICS = os.getenv("KAFKA_TOPICS", "user.events,booking.events,payment.events").split(",")
GROUP_ID = os.getenv("KAFKA_GROUP_ID", "analytics-group")

consumer = None

async def start_consumer():
    global consumer
    consumer = AIOKafkaConsumer(
        *TOPICS,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        group_id=GROUP_ID,
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        auto_offset_reset="earliest",
        enable_auto_commit=True
    )
    await consumer.start()
    print(f"Analytics consumer started, listening to topics: {TOPICS}")
    try:
        async for msg in consumer:
            event = msg.value
            print(f"Received event: {event.get('event_type')} from {msg.topic}")
            await save_event_to_minio(event)
    finally:
        await consumer.stop()

async def stop_consumer():
    if consumer:
        await consumer.stop()