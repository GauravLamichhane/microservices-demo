# storage.py
import os
from minio import Minio
from datetime import timedelta

# Internal connection - for Django's own server-to-server calls
minio_client = Minio(
    os.environ.get("MINIO_INTERNAL_ENDPOINT", "minio:9000"),
    access_key=os.environ.get("MINIO_ACCESS_KEY", "minioadmin"),
    secret_key=os.environ.get("MINIO_SECRET_KEY", "minioadmin123"),
    secure=False,
)

BUCKET_NAME = os.environ.get("MINIO_BUCKET", "products-images")


def get_presigned_upload_url(object_name):
    url = minio_client.presigned_put_object(
        BUCKET_NAME,
        object_name,
        expires=timedelta(minutes=15),
    )
    # Replace internal hostname with the externally-reachable one
    internal = os.environ.get("MINIO_INTERNAL_ENDPOINT", "minio:9000")
    external = os.environ.get("MINIO_EXTERNAL_ENDPOINT", "localhost:9000")
    return url.replace(internal, external)

def get_public_url(object_name):
    external = os.environ.get("MINIO_EXTERNAL_ENDPOINT", "localhost:9000")
    return f"http://{external}/{BUCKET_NAME}/{object_name}"