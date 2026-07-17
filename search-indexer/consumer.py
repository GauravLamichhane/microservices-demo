import json
import os
import time
from kafka import KafkaConsumer
from kafka.errors import NoBrokersAvailable
from elasticsearch import Elasticsearch

es = Elasticsearch(os.environ.get("ELASTICSEARCH_URL", "http://elasticsearch:9200"))
INDEX_NAME = "products"

consumer = None
for attempt in range(10):
    try:
        consumer = KafkaConsumer(
            "product-events",
            bootstrap_servers=os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092"),
            group_id="search-indexer",
            enable_auto_commit=False,
            auto_offset_reset="earliest",
            value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        )
        break
    except NoBrokersAvailable:
        print(f"Kafka not ready, retrying ({attempt+1}/10)...")
        time.sleep(3)

print("Search indexer started consuming")
for message in consumer:
    headers = dict(message.headers or [])
    event_type = headers.get("type", b"").decode("utf-8")
    data = message.value

    if event_type in ("product_created", "product_updated"):
        es.index(index=INDEX_NAME, id=data["id"], document={
            "title": data["title"],
            "image": data["image"],
        })
        print(f"Indexed product {data['id']}")

    elif event_type == "product_deleted":
        try:
            es.delete(index=INDEX_NAME, id=data)
            print(f"Removed product {data} from index")
        except Exception as e:
            print(f"Product {data} not in index, skipping delete: {e}")

    consumer.commit()