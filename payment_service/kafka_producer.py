from aiokafka import AIOKafkaProducer
import json
import os
import uuid
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

async def send_payment_event(booking_id: str, status: str):
    if producer is None:
        print("Kafka producer not ready")
        return
    event = {
        "event_type": f"payment.{status}",
        "data": {
            "booking_id": booking_id,
            "status": status,
            "payment_id": str(uuid.uuid4())
        },
        "timestamp": "2026-04-13T00:00:00Z"
    }
    await producer.send("payment.events", value=event)
    print(f"Sent payment event: {event}")