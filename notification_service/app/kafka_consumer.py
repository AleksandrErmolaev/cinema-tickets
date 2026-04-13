# notification_service/app/kafka_consumer.py
import json
from kafka import KafkaConsumer
from .config import KAFKA_BROKER
from .email_sender import send_email

def start_consumer():
    consumer = KafkaConsumer(
        "booking.events",
        bootstrap_servers=KAFKA_BROKER,
        value_deserializer=lambda m: json.loads(m.decode()),
        auto_offset_reset="earliest"
    )

    print("Notification service started... listening for booking events")

    for msg in consumer:
        event = msg.value
        event_type = event.get("event_type")
        data = event.get("data", {})

        if event_type == "booking.confirmed":
            user_email = data.get("user_email")
            movie_title = data.get("movie_title", "Your movie")
            seats = data.get("seat_ids", [])

            if not user_email:
                print("No user email, skip notification")
                continue

            subject = "Your ticket is confirmed!"
            message = f"""
Hello!

Your booking is confirmed.

Movie: {movie_title}
Seats: {', '.join(seats)}

Enjoy your movie
"""
            send_email(user_email, subject, message)
            print(f"Email sent to {user_email}")