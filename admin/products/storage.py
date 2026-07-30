import os
from datetime import timedelta
from minio import Minio

INTERNAL_ENDPOINT = os.environ["MINIO_INTERNAL_ENDPOINT"]
EXTERNAL_ENDPOINT = os.environ["MINIO_EXTERNAL_ENDPOINT"]

ACCESS_KEY = os.environ["MINIO_ACCESS_KEY"]
SECRET_KEY = os.environ["MINIO_SECRET_KEY"]

BUCKET_NAME = os.environ["MINIO_BUCKET"]


# Used by Django for internal operations
internal_client = Minio(
    INTERNAL_ENDPOINT,
    access_key=ACCESS_KEY,
    secret_key=SECRET_KEY,
    secure=False,
)

# Used only to generate URLs for the browser
external_client = Minio(
    EXTERNAL_ENDPOINT,
    access_key=ACCESS_KEY,
    secret_key=SECRET_KEY,
    secure=True,
)


def get_presigned_upload_url(object_name):
    return external_client.presigned_put_object(
        BUCKET_NAME,
        object_name,
        expires=timedelta(minutes=15),
    )


def get_public_url(object_name):
    return f"https://{EXTERNAL_ENDPOINT}/{BUCKET_NAME}/{object_name}"

def delete_object(image_url):
    prefix = f"https://{EXTERNAL_ENDPOINT}/{BUCKET_NAME}/"
    if not image_url or not image_url.startswith(prefix):
        return  # not a MinIO url, skip (e.g. old picsum links)
    object_name = image_url[len(prefix):]
    try:
        internal_client.remove_object(BUCKET_NAME, object_name)
    except Exception as e:
        print(f"Failed to delete MinIO object {object_name}: {e}")