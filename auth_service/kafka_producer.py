from aiokafka import AIOKafkaProducer
import json
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")

producer: AIOKafkaProducer = None

async def start_kafka_producer():
    global producer
    producer = AIOKafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda v: json.dumps(v).encode()
    )
    await producer.start()

async def stop_kafka_producer():
    if producer:
        await producer.stop()

async def send_user_registered_event(user_id: str, email: str):
    if producer is None:
        print("Kafka producer not initialized, event not sent")
        return
    event = {
        "event_type": "user.registered",
        "user_id": user_id,
        "email": email,
        "timestamp": "2026-04-13T00:00:00Z"
    }
    await producer.send("user.events", value=event)
    print(f"Sent event: {event}")