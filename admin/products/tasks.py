import json
import requests
from celery import shared_task
from .models import Product, PublishedEvent
from .producer import publish
from .kafka_client import get_kafka_producer


@shared_task
def publish_events_to_kafka():
    producer = get_kafka_producer()

    if producer is None:
        return "Kafka producer unavailable, skipping this run"

    events = PublishedEvent.objects.filter(is_consumed=False)[:50]

    if not events.exists():
        return "No new events found"

    success_count = 0
    for event in events:
        try:
            value_bytes = json.dumps(event.payload).encode("utf-8")
            event_type = event.extra.get("type", "")
            headers = [("type", event_type.encode("utf-8"))]

            future = producer.send(
                event.channel,
                value=value_bytes,
                headers=headers,
            )
            # Block briefly to confirm delivery before marking as consumed
            future.get(timeout=5)

            event.is_consumed = True
            event.save(update_fields=["is_consumed"])
            success_count += 1

        except Exception as e:
            print(f"Failed to publish event {event.id}, will retry next run: {e}")
            continue

    producer.flush()
    return f"Published {success_count} events"

@shared_task
def reconcile_products():
    django_products = {p.id: p for p in Product.objects.all()}
    django_ids = set(django_products.keys())

    try:
        flask_response = requests.get("http://main-backend-1:5000/api/products", timeout=5)
        flask_products = flask_response.json()
        flask_ids = {p["id"] for p in flask_products}
    except Exception as e:
        print(f"Reconciliation failed: could not reach Flask - {e}")
        return

    missing_in_flask = django_ids - flask_ids
    extra_in_flask = flask_ids - django_ids

    for product_id in missing_in_flask:
        product = django_products[product_id]
        publish('product_created', {
            'id': product.id,
            'title': product.title,
            'image': product.image,
            'likes': product.likes,
        })
        print(f"Re-published missing product {product_id} to Kafka")

    for product_id in extra_in_flask:
        publish('product_deleted', product_id)
        print(f"Published delete for ghost product {product_id}")

    if not missing_in_flask and not extra_in_flask:
        print("Reconciliation check passed: Django and Flask are in sync")