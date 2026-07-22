from products.models import Product, PublishedEvent
import pytest
from rest_framework.test import APIClient

pytestmark = pytest.mark.django_db

def test_create_product():
    product = Product.objects.create(
        title="Laptop",
        image="https://abc.com/image.jpg"
    )

    assert product.pk is not None
    assert product.title == "Laptop"
  

def test_update_product():
    product = Product.objects.create(
        title="Laptop",
        image="https://abc.com/image.jpg"
    )

    product.title = "Gaming Laptop"
    product.save()

    product.refresh_from_db()

    assert product.title == "Gaming Laptop"

def test_delete_product():
    product = Product.objects.create(
        title="Laptop",
        image="https://abc.com/image.jpg"
    )

    product.delete()

    assert Product.objects.count() == 0


def test_creating_product_creates_published_event():
    product = Product.objects.create(
        title="Laptop",
        image="https://abc.com/image.jpg"
    )
    event = PublishedEvent.objects.filter(channel='product-events').last()
    assert event is not None
    assert event.payload['title'] == "Laptop"
    assert event.extra['type'] == "product_created"


def test_deleting_product_creates_published_event():
    product = Product.objects.create(
        title="Laptop",
        image="https://abc.com/image.jpg"
    )
    product_id = product.pk
    product.delete()

    event = PublishedEvent.objects.filter(channel='product-events').last()
    assert event is not None
    assert event.extra['type'] == 'product_deleted'
    assert event.payload == product_id

def test_likes_only_update_does_not_publish_event():
    product = Product.objects.create(title="Laptop", image="https://abc.com/img.jpg")
    initial_count = PublishedEvent.objects.count()

    product.likes += 1
    product.save(update_fields=['likes'])

    assert PublishedEvent.objects.count() == initial_count  # no new event created


def test_create_product_via_api():
    client = APIClient()
    response = client.post('/api/products/', {
        'title': "Laptop",
        "image": "https://abc.com/img.jpg"
    })

    assert response.status_code == 201
    assert Product.objects.count() == 1