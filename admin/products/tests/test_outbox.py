import pytest
from products.models import Product, PublishedEvent

pytestmark = pytest.mark.django_db


def test_product_create_creates_outbox_event():
    Product.objects.create(
        title="Laptop",
        image="https://abc.com/image.jpg"
    )

    event = PublishedEvent.objects.first()

    assert event is not None
    assert event.channel == "product-events"
    assert event.extra["type"] == "product_created"
    assert event.is_consumed is False
    assert event.payload["title"] == "Laptop"


def test_product_update_creates_outbox_event():
    product = Product.objects.create(
        title="Laptop",
        image="https://abc.com/image.jpg"
    )

    PublishedEvent.objects.all().delete()

    product.title = "Gaming Laptop"
    product.save()

    event = PublishedEvent.objects.first()

    assert event is not None
    assert event.extra["type"] == "product_updated"
    assert event.is_consumed is False
    assert event.payload["title"] == "Gaming Laptop"


def test_product_delete_creates_outbox_event():
    product = Product.objects.create(
        title="Laptop",
        image="https://abc.com/image.jpg"
    )

    PublishedEvent.objects.all().delete()

    product_id = product.id
    product.delete()

    event = PublishedEvent.objects.first()

    assert event is not None
    assert event.extra["type"] == "product_deleted"
    assert event.payload == product_id
    assert event.is_consumed is False
  

def test_likes_update_does_not_create_outbox_event():
    product = Product.objects.create(
        title="Laptop",
        image="https://abc.com/image.jpg"
    )

    PublishedEvent.objects.all().delete()

    product.likes = 10
    product.save(update_fields=["likes"])

    assert PublishedEvent.objects.count() == 0