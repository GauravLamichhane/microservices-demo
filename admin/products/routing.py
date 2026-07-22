from django.urls import path
from . import consumers

websocket_urlpatterns = [
  path('ws/likes/', consumers.LikeConsumer.as_asgi()),
]