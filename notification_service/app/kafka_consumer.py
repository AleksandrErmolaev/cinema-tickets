import json
from kafka import KafkaConsumer
from .config import KAFKA_BROKER
from .email_sender import send_email

def start_consumer():
    consumer = KafkaConsumer(
        "payment.succeeded",
        bootstrap_servers=KAFKA_BROKER,
        value_deserializer=lambda m: json.loads(m.decode())
    )

    print("Notification service started... listening Kafka")

    for msg in consumer:
        event = msg.value

        print("Received event:", event)

        user_email = event.get("user_email", "test@example.com")
        movie_title = event.get("movie_title", "Your movie")
        seats = event.get("seats", [])

        subject = "🎟 Your ticket is confirmed!"
        message = f"""
Hello!

Your booking is confirmed.

Movie: {movie_title}
Seats: {seats}

Enjoy your movie 🍿
"""

        send_email(user_email, subject, message)
        print("Email sent to", user_email)