import pytest
from rest_framework.test import APIClient
from products.models import User

pytestmark = pytest.mark.django_db


@pytest.fixture
def client():
    return APIClient()


def test_user_api_returns_random_user(client):
    User.objects.create()
    User.objects.create()

    response = client.get("/api/user/")

    assert response.status_code == 200
    assert "id" in response.data


def test_user_api_returns_404_when_no_users(client):
    response = client.get("/api/user/")

    assert response.status_code == 404
    assert response.data["detail"] == "No users found."