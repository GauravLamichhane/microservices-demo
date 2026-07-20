import json
import requests
from celery import shared_task
from .models import Product, PublishedEvent
# from .producer import publish
from .kafka_client import get_kafka_producer


@shared_task
def publish_events_to_kafka():
    print("=" * 60)
    print("Running publish_events_to_kafka")
    producer = get_kafka_producer()

    if producer is None:
        return "Kafka producer unavailable, skipping this run"

    events = PublishedEvent.objects.filter(is_consumed=False)[:50]

    print("Pending events:", events.count())


    if not events.exists():
        return "No new events found"

    success_count = 0
    for event in events:
        try:
            value_bytes = json.dumps(event.payload).encode("utf-8")
            event_type = event.extra.get("type", "")
            headers = [("type", event_type.encode("utf-8"))]

            print("Publishing event", event.id)

            future = producer.send(
                event.channel,
                value=value_bytes,
                headers=headers,
            )
            # Block briefly to confirm delivery before marking as consumed
            future.get(timeout=5)

            print("Kafka ACK received")

            event.is_consumed = True
            event.save(update_fields=["is_consumed"])
            success_count += 1
            print("Marked consumed")

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

        PublishedEvent.objects.create(
            channel="product-events",
            payload={
                "id": product.id,
                "title": product.title,
                "image": product.image,
                "likes": product.likes,
            },
            extra={"type": "product_created"},
        )

        print(f"Created outbox event for {product.id}")
        print(f"Re-published missing product {product_id} to Kafka")

    for product_id in extra_in_flask:
        PublishedEvent.objects.create(
            channel="product-events",
            payload=product_id,
            extra={"type": "product_deleted"},
        )

    if not missing_in_flask and not extra_in_flask:
        print("Reconciliation check passed: Django and Flask are in sync")