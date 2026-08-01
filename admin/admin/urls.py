# admin/admin/urls.py
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path("admin/api/", include("products.urls")),
    path('admin/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('admin/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('admin/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]