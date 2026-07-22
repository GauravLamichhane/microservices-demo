import pytest
from rest_framework.test import APIClient
from unittest.mock import patch

pytestmark = pytest.mark.django_db


@pytest.fixture
def client():
    return APIClient()


@patch("products.views.get_presigned_upload_url")
@patch("products.views.get_public_url")
def test_get_upload_url(mock_public_url, mock_upload_url, client):
    mock_upload_url.return_value = "https://upload-url"
    mock_public_url.return_value = "https://public-url"

    response = client.post(
        "/api/products/upload-url/",
        {"filename": "image.jpg"},
        format="json"
    )

    assert response.status_code == 200
    assert response.data["upload_url"] == "https://upload-url"
    assert response.data["public_url"] == "https://public-url"
    assert "object_name" in response.data