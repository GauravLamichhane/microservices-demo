import os
from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable
import time

_producer = None


def get_kafka_producer():
    global _producer
    if _producer is None:
        for attempt in range(10):
            try:
                _producer = KafkaProducer(
                    bootstrap_servers=os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092"),
                    value_serializer=lambda v: v if isinstance(v, bytes) else v.encode("utf-8"),
                )
                break
            except NoBrokersAvailable:
                print(f"Kafka not ready, retrying producer init ({attempt+1}/10)...")
                time.sleep(3)
    return _producer