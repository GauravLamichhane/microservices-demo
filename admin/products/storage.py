import os
from minio import Minio
from datetime import timedelta

internal_endpoint = os.environ["MINIO_INTERNAL_ENDPOINT"]
external_endpoint = os.environ["MINIO_EXTERNAL_ENDPOINT"]

minio_client = Minio(
    internal_endpoint,
    access_key=os.environ.get("MINIO_ACCESS_KEY", "minioadmin"),
    secret_key=os.environ.get("MINIO_SECRET_KEY", "minioadmin123"),
    secure=True,
)

BUCKET_NAME = "products-images"


def get_presigned_upload_url(object_name):
    return minio_client.presigned_put_object(BUCKET_NAME, object_name, expires=timedelta(minutes=15))


def get_public_url(object_name):
    return f"https://{external_endpoint}/{BUCKET_NAME}/{object_name}"