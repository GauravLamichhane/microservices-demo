import json
import os
from kafka import KafkaProducer

producer = KafkaProducer(
    bootstrap_servers=os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"),
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
)

def publish(method, body):
    future = producer.send(
        "product-events",
        value=body,
        headers=[("type", method.encode("utf-8"))]
    )
    try:
        record_metadata = future.get(timeout=10)
        print(f"Published to {record_metadata.topic}, partition {record_metadata.partition}, offset {record_metadata.offset}")
    except Exception as e:
        print(f"Kafka publish failed: {e}")
    producer.flush()