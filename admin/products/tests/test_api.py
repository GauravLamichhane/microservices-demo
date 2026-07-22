import pytest
from rest_framework.test import APIClient
from products.models import Product

pytestmark = pytest.mark.django_db

@pytest.fixture
def client():
  return APIClient()

@pytest.fixture
def product():
  return Product.objects.create(
    title="Laptop",
    image="https://abc.com/laptop.jpg"
  )

def test_create_product(client):
  response = client.post(
    "/api/products/",
    {
      "title": "Phone",
      "image": "https://abc.com/phone.jpg"
    },
    format="json"
  )

  assert response.status_code == 201
  assert Product.objects.count() == 1
  assert Product.objects.first().title == "Phone"

def test_list_products(client, product):
  response = client.get("/api/products/")

  assert response.status_code == 200
  assert len(response.data) == 1
  assert response.data[0]["title"] == "Laptop"

def test_retrieve_product(client, product):
  response = client.get(f"/api/products/{product.id}/")

  assert response.status_code == 200
  assert response.data['title'] == "Laptop"

def test_update_product(client, product):
  response = client.put(f"/api/products/{product.id}/",
                        {
                          "title": "Gaming Laptop",
                          "image": "https://prod/image.jpg",
                        },
                        format="json")
  
  product.refresh_from_db()

  assert response.status_code == 200
  assert product.title == "Gaming Laptop"

def test_delete_product(client, product):
  response = client.delete(f"/api/products/{product.id}/")

  assert response.status_code == 204
  assert Product.objects.count() == 0

##

def test_create_product_without_title(client):
    response = client.post(
        "/api/products/",
        {
            "image": "https://abc.com/test.jpg"
        },
        format="json"
    )

    assert response.status_code == 400


def test_create_product_without_image(client):
    response = client.post(
        "/api/products/",
        {
            "title": "Laptop"
        },
        format="json"
    )

    assert response.status_code == 400


def test_retrieve_invalid_product(client):
    response = client.get("/api/products/9999/")

    assert response.status_code == 404


def test_update_invalid_product(client):
    response = client.put(
        "/api/products/9999/",
        {
            "title": "Test",
            "image": "https://abc.com/test.jpg"
        },
        format="json"
    )

    assert response.status_code == 404


def test_delete_invalid_product(client):
    response = client.delete("/api/products/9999/")

    assert response.status_code == 404