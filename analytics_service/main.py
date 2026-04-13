import asyncio
import threading
from kafka_consumer import start_consumer, stop_consumer
from minio_client import ensure_bucket_exists
from health import run_health_server
from setup_lifecycle import setup_lifecycle

async def main():
    # Создаём bucket в MinIO, если не существует
    ensure_bucket_exists()

    setup_lifecycle()
    
    # Запускаем Kafka consumer
    consumer_task = asyncio.create_task(start_consumer())
    
    # Запускаем health check сервер в отдельном потоке
    health_thread = threading.Thread(target=run_health_server, daemon=True)
    health_thread.start()
    
    # Ждём завершения consumer (бесконечно)
    await consumer_task

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Shutting down analytics service...")
        asyncio.run(stop_consumer())