import boto3
from botocore.client import Config
import os
import json
from datetime import datetime
import uuid

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9000")
ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin")
BUCKET = os.getenv("MINIO_BUCKET", "analytics-events")
SECURE = os.getenv("MINIO_SECURE", "False").lower() == "true"

def get_minio_client():
    return boto3.client(
        "s3",
        endpoint_url=f"http{'s' if SECURE else ''}://{MINIO_ENDPOINT}",
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY,
        config=Config(signature_version="s3v4"),
        region_name="us-east-1"
    )

def ensure_bucket_exists():
    client = get_minio_client()
    try:
        client.head_bucket(Bucket=BUCKET)
    except:
        client.create_bucket(Bucket=BUCKET)
        print(f"Bucket {BUCKET} created")

async def save_event_to_minio(event_data: dict):
    """
    Сохраняет событие в MinIO в виде JSON файла.
    Путь: events/YYYY/MM/DD/event_timestamp_uuid.json
    """
    client = get_minio_client()
    timestamp = event_data.get("timestamp", datetime.utcnow().isoformat())
    try:
        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
    except:
        dt = datetime.utcnow()
    
    year = dt.strftime("%Y")
    month = dt.strftime("%m")
    day = dt.strftime("%d")
    event_id = str(uuid.uuid4())
    filename = f"{dt.timestamp()}_{event_id}.json"
    object_key = f"events/{year}/{month}/{day}/{filename}"
    
    json_str = json.dumps(event_data, indent=2)
    client.put_object(
        Bucket=BUCKET,
        Key=object_key,
        Body=json_str.encode("utf-8"),
        ContentType="application/json"
    )
    print(f"Saved event to s3://{BUCKET}/{object_key}")