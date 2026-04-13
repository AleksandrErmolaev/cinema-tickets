from fastapi import FastAPI
import threading
from .kafka_consumer import start_consumer

app = FastAPI(title="Notification Service")

@app.get("/health")
def health():
    return {"status": "ok"}

def run_consumer():
    start_consumer()

threading.Thread(target=run_consumer, daemon=True).start()