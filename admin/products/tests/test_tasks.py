import pytest
from unittest.mock import Mock, patch

from products.models import Product, PublishedEvent
from products.tasks import publish_events_to_kafka, reconcile_products

pytestmark = pytest.mark.django_db

@patch("products.tasks.get_kafka_producer")
def test_publish_no_events(mock_get_producer):
    mock_get_producer.return_value = Mock()

    result = publish_events_to_kafka()

    assert result == "No new events found"

@patch("products.tasks.get_kafka_producer")
def test_publish_when_kafka_unavailable(mock_get_producer):
    mock_get_producer.return_value = None

    result = publish_events_to_kafka()

    assert result == "Kafka producer unavailable, skipping this run"
  
@patch("products.tasks.get_kafka_producer")
def test_publish_single_event(mock_get_producer):
    producer = Mock()

    future = Mock()
    future.get.return_value = None

    producer.send.return_value = future

    mock_get_producer.return_value = producer

    event = PublishedEvent.objects.create(
        channel="product-events",
        payload={"id": 1},
        extra={"type": "product_created"},
        is_consumed=False,
    )

    result = publish_events_to_kafka()

    event.refresh_from_db()

    assert event.is_consumed is True
    assert result == "Published 1 events"

    producer.send.assert_called_once()
    future.get.assert_called_once()
    producer.flush.assert_called_once()


@patch("products.tasks.get_kafka_producer")
def test_publish_failure_does_not_mark_consumed(mock_get_producer):
    producer = Mock()

    producer.send.side_effect = Exception("Kafka down")

    mock_get_producer.return_value = producer

    event = PublishedEvent.objects.create(
        channel="product-events",
        payload={"id": 1},
        extra={"type": "product_created"},
        is_consumed=False,
    )

    publish_events_to_kafka()

    event.refresh_from_db()

    assert event.is_consumed is False


@patch("products.tasks.get_kafka_producer")
def test_publish_multiple_events(mock_get_producer):
    producer = Mock()

    future = Mock()
    future.get.return_value = None

    producer.send.return_value = future

    mock_get_producer.return_value = producer

    for i in range(3):
        PublishedEvent.objects.create(
            channel="product-events",
            payload={"id": i},
            extra={"type": "product_created"},
        )

    result = publish_events_to_kafka()

    assert PublishedEvent.objects.filter(is_consumed=True).count() == 3
    assert result == "Published 3 events"
    assert producer.send.call_count == 3

@patch("products.tasks.requests.get")
def test_reconcile_when_in_sync(mock_get):
    Product.objects.create(
        id=1,
        title="Laptop",
        image="img.jpg",
    )

    response = Mock()
    response.json.return_value = [
        {
            "id": 1,
            "title": "Laptop",
            "image": "img.jpg",
        }
    ]

    mock_get.return_value = response

    reconcile_products()

    assert PublishedEvent.objects.count() == 1