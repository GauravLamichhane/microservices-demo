import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "admin.settings")
django.setup()

import json
import time
from kafka import KafkaConsumer
from kafka.errors import NoBrokersAvailable
from products.models import Product
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

consumer = None
for attempt in range(10):
    try:
        consumer = KafkaConsumer(
            "product-likes",
            bootstrap_servers=os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"),
            group_id="products-like-consumer",
            enable_auto_commit=False,
            auto_offset_reset="earliest",
            value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        )
        break
    except NoBrokersAvailable:
        print(f"Kafka not ready, retrying ({attempt+1}/10)...")
        time.sleep(3)

print("Started consuming")
for message in consumer:
    headers = dict(message.headers or [])
    event_type = headers.get("type", b"").decode("utf-8")
    product_id = message.value
    print(f"Event type: {event_type}")
    print(product_id)

    try:
        product = Product.objects.get(id=product_id)
        product.likes += 1
        product.save(update_fields=["likes"])

        channel_layer = get_channel_layer()

        async_to_sync(channel_layer.group_send)(
            "likes",
            {
                "type": "like_updated",
                "product_id": product.id,
                "likes": product.likes,
            },
        )

        print("Product likes increased")
    except Product.DoesNotExist:
        print(f"Product {product_id} not found, skipping")
    finally:
        consumer.commit()