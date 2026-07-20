import os
import time
from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable

_producer = None


def get_kafka_producer():
    global _producer

    if _producer is not None:
        try:
            if _producer.bootstrap_connected():
                return _producer
        except Exception:
            try:
                _producer.close()
            except Exception:
                pass
            _producer = None

    for attempt in range(10):
        try:
            _producer = KafkaProducer(
                bootstrap_servers=os.environ.get(
                    "KAFKA_BOOTSTRAP_SERVERS",
                    "kafka:9092",
                ),
                value_serializer=lambda v: (
                    v if isinstance(v, bytes)
                    else v.encode("utf-8")
                ),
                retries=5,
                retry_backoff_ms=1000,
                reconnect_backoff_ms=1000,
                reconnect_backoff_max_ms=5000,
            )
            return _producer

        except NoBrokersAvailable:
            print(f"Attempt {attempt + 1}/10 failed")
            time.sleep(3)

    return None