from rest_framework.routers import DefaultRouter
from django.urls import path
from .views import ProductViewSet, UserAPIView

router = DefaultRouter()
router.register("products", ProductViewSet, basename="products")

urlpatterns = [
    path("user/", UserAPIView.as_view()),
] + router.urls