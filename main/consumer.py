import json
import time
import os
from kafka import KafkaConsumer
from kafka.errors import NoBrokersAvailable
from main import app, Product, db
import redis

cache = redis.Redis(host='redis', port=6379, decode_responses=True)

consumer = None
for attempt in range(10):
    try:
        consumer = KafkaConsumer(
            "product-events",
            bootstrap_servers=os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"),
            group_id="admin-product-consumer",
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
    data = message.value
    if event_type == "product_deleted":
        print(f"Received {event_type} for product {data}")
    else:
        print(f"Received {event_type} for product {data.get('id')}")
    print(
    f"Topic={message.topic}, "
    f"Partition={message.partition}, "
    f"Offset={message.offset}"
    )

    with app.app_context():
        if event_type == "product_created":
            existing = Product.query.get(data["id"])
            if existing:
                print(f"Product {data['id']} already exists, skipping create")
            else:
                product = Product(id=data["id"], title=data["title"], image=data["image"])
                db.session.add(product)
                db.session.commit()
                try:
                    cache.delete("products")
                except redis.exceptions.RedisError:
                    pass
                print("Product Created")

        elif event_type == "product_updated":
            product = Product.query.get(data["id"])
            if product:
                product.title = data["title"]
                product.image = data["image"]
                db.session.commit()
                try:
                    cache.delete("products")
                except redis.exceptions.RedisError:
                    pass
                print("Product Updated")
            else:
                print(f"Product {data['id']} not found in Flask DB, skipping update")

        elif event_type == "product_deleted":
            product = Product.query.get(data)
            if product:
                db.session.delete(product)
                db.session.commit()
                try:
                    cache.delete("products")
                except redis.exceptions.RedisError:
                    pass
                print("Product deleted")
            else:
                print(f"Product {data} not found in Flask DB, skipping delete")
        else:
            print(f"Unknown event: {event_type}")

    consumer.commit()