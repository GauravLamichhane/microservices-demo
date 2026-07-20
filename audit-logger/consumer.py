import json
import os
import time
from datetime import datetime, timezone
from kafka import KafkaConsumer
from kafka.errors import NoBrokersAvailable
from pymongo import MongoClient

mongo_client = MongoClient(os.environ.get("MONGO_URL", "mongodb://mongo:27017/"))
db = mongo_client["audit_log_db"]
collection = db["audit_logs"]

consumer = None
for attempt in range(10):
  try:
    consumer = KafkaConsumer(
      "product-events", "product-likes",
      bootstrap_servers=os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092"),
      group_id="audit-logger",
      enable_auto_commit = False,
      auto_offset_reset="latest",
      value_deserializer=lambda v: json.loads(v.decode("utf-8")),
    )
    break
  except NoBrokersAvailable:
    print(f"Kafka not ready, retrying ({attempt+1}/10)..")
    time.sleep(3)

print("Audit logger started consuming")
for message in consumer:
  headers = dict(message.headers or [])
  event_type = headers.get("type", b"").decode("utf-8")

  log_entry = {
    "event_type": event_type,
    "topic": message.topic,
    "payload": message.value,
    "timestamp": datetime.now(timezone.utc),
  }

  collection.insert_one(log_entry)
  print(
    f"[{message.topic}] "
    f"{event_type} "
    f"offset={message.offset} "
    f"payload={message.value}"
)

  consumer.commit()