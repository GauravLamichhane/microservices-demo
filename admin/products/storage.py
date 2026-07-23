import os
from minio import Minio
from datetime import timedelta

minio_client = Minio(
    os.environ.get("MINIO_ENDPOINT", "173.231.235.106:9000"),
    access_key=os.environ.get("MINIO_ACCESS_KEY", "minioadmin"),
    secret_key=os.environ.get("MINIO_SECRET_KEY", "minioadmin123"),
    secure=False,
)

BUCKET_NAME = "products-images"


def get_presigned_upload_url(object_name):
    return minio_client.presigned_put_object(BUCKET_NAME, object_name, expires=timedelta(minutes=15))


def get_public_url(object_name):
    endpoint = os.environ.get("MINIO_ENDPOINT", "173.231.235.106:9000")
    return f"http://{endpoint}/{BUCKET_NAME}/{object_name}"
