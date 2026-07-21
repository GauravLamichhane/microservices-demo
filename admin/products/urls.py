from rest_framework.routers import DefaultRouter
from django.urls import path
from .views import ProductViewSet, UserAPIView, get_upload_url

router = DefaultRouter()
router.register("products", ProductViewSet, basename="products")

urlpatterns = [
    path("user/", UserAPIView.as_view()),
    path('products/upload-url/', get_upload_url, name='get-upload-url'),
] + router.urls 