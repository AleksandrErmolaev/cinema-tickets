from fastapi import FastAPI
import uvicorn
import os

health_app = FastAPI()

@health_app.get("/health")
async def health():
    return {"status": "ok", "service": "analytics"}

def run_health_server():
    port = int(os.getenv("HEALTH_PORT", "8006"))
    uvicorn.run(health_app, host="0.0.0.0", port=port)