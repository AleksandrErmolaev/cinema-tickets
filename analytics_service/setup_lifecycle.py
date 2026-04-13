from minio import Minio
from minio.commonconfig import GovernanceConfiguration, Tags, LifecycleRule, Expiration
from minio.lifecycleconfig import LifecycleConfig
import os

def setup_lifecycle():
    client = Minio(
        os.getenv("MINIO_ENDPOINT", "localhost:9000"),
        access_key=os.getenv("MINIO_ACCESS_KEY", "minioadmin"),
        secret_key=os.getenv("MINIO_SECRET_KEY", "minioadmin"),
        secure=os.getenv("MINIO_SECURE", "False").lower() == "true"
    )
    bucket = os.getenv("MINIO_BUCKET", "analytics-events")

    expiration = Expiration(days=365)
    rule = LifecycleRule(
        id="expire-old-events",
        status="Enabled",
        expiration=expiration,
        filter={"prefix": "events/"}
    )
    config = LifecycleConfig(rules=[rule])
    client.set_bucket_lifecycle(bucket, config)
    print(f"Lifecycle policy set for bucket {bucket}: delete events older than 365 days")

if __name__ == "__main__":
    setup_lifecycle()