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
        raise RuntimeError("Kafka producer not initialized")
    future = producer.send(
        "product-likes",
        value=body,
        headers=[("type", method.encode("utf-8"))]
    )
    record_metadata = future.get(timeout=10)
    print(f"Published to {record_metadata.topic}, partition {record_metadata.partition}, offset {record_metadata.offset}")
    producer.flush()