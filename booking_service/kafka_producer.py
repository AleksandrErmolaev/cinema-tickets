from aiokafka import AIOKafkaProducer
import json
import os
from dotenv import load_dotenv

load_dotenv()

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")

producer: AIOKafkaProducer = None

async def start_kafka_producer():
    global producer
    producer = AIOKafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda v: json.dumps(v, default=str).encode()
    )
    await producer.start()

async def stop_kafka_producer():
    if producer:
        await producer.stop()

async def send_event(topic: str, event_type: str, data: dict):
    if producer is None:
        print("Kafka producer not ready")
        return
    message = {
        "event_type": event_type,
        "data": data,
        "timestamp": "2026-04-13T00:00:00Z"
    }
    await producer.send(topic, value=message)
    print(f"Sent event {event_type} to {topic}: {message}")


async def send_booking_event(booking_data: dict):
    """Отправка события бронирования в Kafka"""
    await send_event("booking.events", "booking_event", booking_data)
