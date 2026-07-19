import json
import os
import time
from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable

producer = None
for attempt in range(10):
    try:
        producer = KafkaProducer(
            bootstrap_servers=os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"),
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        )
        break
    except NoBrokersAvailable:
        print(f"Kafka not ready, retrying producer init ({attempt+1}/10)...")
        time.sleep(3)

if producer is None:
    print("WARNING: Kafka producer could not connect after 10 attempts.")


def publish(method, body):
    if producer is None:
        print(f"Kafka producer not initialized, dropping event: {method}")
        return
    producer.send(
        "product-likes",  # or "product-likes" depending on which producer.py this is
        value=body,
        headers=[("type", method.encode("utf-8"))]
    )
    producer.flush()