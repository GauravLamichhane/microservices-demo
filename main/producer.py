import json
import os
from kafka import KafkaProducer

producer = KafkaProducer(
    bootstrap_servers=os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"),
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
)

def publish(method, body):
    producer.send(
        "product-likes",
        value=body,
        headers=[("type", method.encode("utf-8"))]
    )
    producer.flush()